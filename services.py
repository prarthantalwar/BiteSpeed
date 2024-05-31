from collections import OrderedDict
from config import get_db_connection
import logging


class ContactService:
    def identify_contact(self, email=None, phoneNumber=None):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT * FROM Contact WHERE email = %s OR phoneNumber = %s"
            cursor.execute(query, (email, phoneNumber))
            contacts = cursor.fetchall()

            print("\n\nFetched contacts from the database:", contacts)

            new_contact = {"email": email, "phoneNumber": phoneNumber}
            if contacts:
                primary_contact, secondary_contacts = self.merge_contacts(
                    contacts, new_contact
                )
                response = self.build_response(primary_contact, secondary_contacts)
            else:
                print("\n\nNo existing contacts found, creating new primary contact")
                primary_contact = self.create_primary_contact(email, phoneNumber)
                response = self.build_response(primary_contact, [])
            cursor.close()
            conn.close()

        except Exception as e:
            logging.error(f"Error identifying contact: {e}")
            raise

        return response

    def create_primary_contact(self, email, phoneNumber):
        try:
            print("\n\nCreating primary contact in the database")
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = "INSERT INTO Contact (email, phoneNumber, linkPrecedence) VALUES (%s, %s, 'primary')"
            cursor.execute(query, (email, phoneNumber))
            conn.commit()

            cursor.execute("SELECT * FROM Contact WHERE id = %s", (cursor.lastrowid,))
            primary_contact = cursor.fetchone()
            cursor.close()
            conn.close()

            print("\n\nPrimary contact created successfully:", primary_contact)
        except Exception as e:
            logging.error(f"Error creating primary contact: {e}")
            raise

        return primary_contact

    def merge_contacts(self, contacts, new_contact):
        print("\n\nMerging existing contacts")

        num_primary = sum(
            1 for contact in contacts if contact.get("linkPrecedence") == "primary"
        )

        if num_primary > 1:
            print(
                "\n\n\nHave to convert some primary to secondary as more than 1 primary contact"
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

            # Add new contact to database
            # new_secondary_contact = self.add_new_contact_to_database(new_contact, id_for_link)
            # secondary_contacts.append(new_secondary_contact)

        else:
            print("\n\n\nMerging as only 1 primary contact")
            # primary_contact = None
            id_for_link = 0
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
        try:
            print("\n\nUpdating contact to secondary in the database:", contact)
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = "UPDATE Contact SET linkPrecedence = 'secondary', linkedId = %s WHERE id = %s"
            cursor.execute(query, (linkedId, contact["id"]))
            conn.commit()

            cursor.close()
            conn.close()

            print("\n\nContact updated to secondary successfully:", contact)
        except Exception as e:
            logging.error(f"Error updating contact to secondary: {e}")
            raise

    def add_new_contact_to_database(self, new_contact, linkedId):
        try:
            print(
                "\n\nAdding new contact to database",
                new_contact,
                "with linkedId of",
                linkedId,
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
            print("\n\nQuery for adding new contact data to database:", query)
            conn.commit()

            print("\n\nNew contact added to the database successfully")

            # Retrieve the data to display as secondary
            cursor.execute("SELECT * FROM Contact WHERE id = %s", (cursor.lastrowid,))
            secondary = cursor.fetchone()

            print("\n\nNew contact data:", secondary)
            cursor.close()
            conn.close()
            return secondary
        except Exception as e:
            logging.error(f"Error adding new contact to database: {e}")
            raise

    def build_response(self, primary_contact, secondary_contacts):
        try:
            print("\n\nBuilding response")
            print(
                "\n\n\nPrimarycontact:",
                primary_contact,
                "secondary contact:",
                secondary_contacts,
                "\n\n\n",
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

            print("\n\nResponse built:", response)
        except Exception as e:
            logging.error(f"Error building response: {e}")
            raise

        return response
