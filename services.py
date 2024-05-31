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

            if contacts:
                primary_contact, secondary_contacts = self.merge_contacts(contacts)
                response = self.build_response(primary_contact, secondary_contacts)
            else:
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
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = "INSERT INTO Contact (email, phoneNumber, linkPrecedence) VALUES (%s, %s, 'primary')"
            cursor.execute(query, (email, phoneNumber))
            conn.commit()

            cursor.execute("SELECT * FROM Contact WHERE id = %s", (cursor.lastrowid,))
            primary_contact = cursor.fetchone()
            cursor.close()
            conn.close()
        except Exception as e:
            logging.error(f"Error creating primary contact: {e}")
            raise

        return primary_contact

    def merge_contacts(self, contacts):
        primary_contact = None
        secondary_contacts = []

        for contact in contacts:
            if contact["linkPrecedence"] == "primary":
                primary_contact = contact
            else:
                secondary_contacts.append(contact)

        if not primary_contact:
            primary_contact = contacts[0]
            primary_contact["linkPrecedence"] = "primary"
            secondary_contacts = contacts[1:]

        # Update secondary contacts to link to primary contact
        for secondary_contact in secondary_contacts:
            self.update_contact_to_secondary(
                secondary_contact["id"], primary_contact["id"]
            )

        return primary_contact, secondary_contacts

    def update_contact_to_secondary(self, contact_id, primary_contact_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            query = "UPDATE Contact SET linkPrecedence = 'secondary', linkedId = %s WHERE id = %s"
            cursor.execute(query, (primary_contact_id, contact_id))
            conn.commit()

            cursor.close()
            conn.close()
        except Exception as e:
            logging.error(f"Error updating contact to secondary: {e}")
            raise

    def build_response(self, primary_contact, secondary_contacts):
        try:
            response = {
                "contact": {
                    "primaryContactId": primary_contact["id"],
                    "emails": [
                        email
                        for email in [primary_contact["email"]]
                        + [c["email"] for c in secondary_contacts]
                        if email
                    ],
                    "phoneNumbers": [
                        phone
                        for phone in [primary_contact["phoneNumber"]]
                        + [c["phoneNumber"] for c in secondary_contacts]
                        if phone
                    ],
                    "secondaryContactIds": [c["id"] for c in secondary_contacts],
                }
            }
        except Exception as e:
            logging.error(f"Error building response: {e}")
            raise

        return response
