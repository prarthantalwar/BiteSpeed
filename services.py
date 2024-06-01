from collections import OrderedDict
from config import get_db_connection
import logging

# Configuring logging for debug
logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class ContactService:
    def identify_contact(self, email=None, phoneNumber=None):
        """
        Identify a contact based on email and/or phone number.
        If contact exists, merge the contacts. If not, create a new primary contact.
        """
        try:
            # Establish database connection
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Query to fetch contacts based on email or phone number
            query = "SELECT * FROM Contact WHERE email = %s OR phoneNumber = %s"
            cursor.execute(query, (email, phoneNumber))
            contacts = cursor.fetchall()

            logging.debug("Fetched contacts from the database: %s", contacts)

            new_contact = {"email": email, "phoneNumber": phoneNumber}
            if contacts:
                # Merge existing contacts if found
                logging.debug("Merging existing contacts")
                primary_contact, secondary_contacts = self.merge_contacts(
                    contacts, new_contact
                )
                response = self.build_response(primary_contact, secondary_contacts)
            else:
                # Create new primary contact if no existing contacts found
                logging.debug(
                    "No existing contacts found, creating new primary contact"
                )
                primary_contact = self.create_primary_contact(email, phoneNumber)
                response = self.build_response(primary_contact, [])
            cursor.close()
            conn.close()

        except Exception as e:
            logging.error("Error identifying contact: %s", e)
            raise

        return response

    def create_primary_contact(self, email, phoneNumber):
        """
        Create a new primary contact in the database.
        """
        try:
            logging.debug("Creating primary contact in the database")
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Insert new primary contact
            query = "INSERT INTO Contact (email, phoneNumber, linkPrecedence) VALUES (%s, %s, 'primary')"
            cursor.execute(query, (email, phoneNumber))
            conn.commit()

            # Fetch the newly created contact
            cursor.execute("SELECT * FROM Contact WHERE id = %s", (cursor.lastrowid,))
            primary_contact = cursor.fetchone()
            cursor.close()
            conn.close()

            logging.debug("Primary contact created successfully: %s", primary_contact)
        except Exception as e:
            logging.error("Error creating primary contact: %s", e)
            raise

        return primary_contact

    def merge_contacts(self, contacts, new_contact):
        """
        Merge existing contacts and link them appropriately.
        """
        logging.debug("Merging existing contacts")

        # Count the number of primary contacts
        num_primary = sum(
            1 for contact in contacts if contact.get("linkPrecedence") == "primary"
        )

        if num_primary > 1:
            logging.debug(
                "Have to convert some primary to secondary as more than 1 primary contact"
            )
            primary_contacts = [
                contact
                for contact in contacts
                if contact["linkPrecedence"] == "primary"
            ]
            secondary_contacts = [
                contact
                for contact in contacts
                if contact["linkPrecedence"] == "secondary"
            ]

            # Find the oldest primary contact
            primary_contact = min(primary_contacts, key=lambda c: c["createdAt"])
            id_for_link = primary_contact["id"]

            # Update other primary contacts to secondary
            for contact in primary_contacts:
                if contact["id"] != id_for_link:
                    self.update_contact_to_secondary(contact, id_for_link)
                    secondary_contacts.append(contact)

        else:
            logging.debug("Merging as only 1 primary contact")
            secondary_contacts = []

            for contact in contacts:
                if contact["linkPrecedence"] == "primary":
                    primary_contact = contact
                    id_for_link = contact["id"]
                else:
                    secondary_contacts.append(contact)

            # Add new contact to database
            second_contact = self.add_new_contact_to_database(new_contact, id_for_link)

            # Add new contact as secondary
            secondary_contacts.append(second_contact)

        return primary_contact, secondary_contacts

    def update_contact_to_secondary(self, contact, linkedId):
        """
        Update a contact to secondary and link it to the primary contact.
        """
        try:
            logging.debug("Updating contact to secondary in the database: %s", contact)
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = "UPDATE Contact SET linkPrecedence = 'secondary', linkedId = %s WHERE id = %s"
            cursor.execute(query, (linkedId, contact["id"]))
            conn.commit()

            cursor.close()
            conn.close()

            logging.debug("Contact updated to secondary successfully: %s", contact)
        except Exception as e:
            logging.error("Error updating contact to secondary: %s", e)
            raise

    def add_new_contact_to_database(self, new_contact, linkedId):
        """
        Add a new contact to the database as a secondary contact linked to the primary.
        """
        try:
            logging.debug(
                "Adding new contact to database with linkedId of %s: %s",
                linkedId,
                new_contact,
            )
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = "INSERT INTO Contact (email, phoneNumber, linkPrecedence, linkedId) VALUES (%s, %s, %s, %s)"
            cursor.execute(
                query,
                (
                    new_contact["email"],
                    new_contact["phoneNumber"],
                    "secondary",
                    linkedId,
                ),
            )
            logging.debug("Query for adding new contact data to database: %s", query)
            conn.commit()

            logging.debug("New contact added to the database successfully")

            # Retrieve the data to display as secondary
            cursor.execute("SELECT * FROM Contact WHERE id = %s", (cursor.lastrowid,))
            secondary = cursor.fetchone()

            logging.debug("New contact data: %s", secondary)
            cursor.close()
            conn.close()

            return secondary
        except Exception as e:
            logging.error("Error adding new contact to database: %s", e)
            raise

    def build_response(self, primary_contact, secondary_contacts):
        """
        Build the response structure with primary and secondary contacts.
        """
        try:
            logging.debug("Building response")
            logging.debug(
                "Primary contact: %s, Secondary contacts: %s",
                primary_contact,
                secondary_contacts,
            )
            response = {
                "contact": {
                    "primaryContactId": primary_contact["id"],
                    "emails": list(
                        OrderedDict.fromkeys(
                            [
                                email
                                for email in [primary_contact["email"]]
                                + [c["email"] for c in secondary_contacts]
                                if email
                            ]
                        )
                    ),
                    "phoneNumbers": list(
                        OrderedDict.fromkeys(
                            [
                                phone
                                for phone in [primary_contact["phoneNumber"]]
                                + [c["phoneNumber"] for c in secondary_contacts]
                                if phone
                            ]
                        )
                    ),
                    "secondaryContactIds": [c["id"] for c in secondary_contacts],
                }
            }

            logging.debug("Response built: %s", response)
        except Exception as e:
            logging.error("Error building response: %s", e)
            raise

        return response
