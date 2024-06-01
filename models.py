from config import get_db_connection


def create_tables():
    """
    Creates the Contact table in the database if it does not already exist.
    The table includes fields for ID, phone number, email, linked ID, link precedence,
    and timestamps for creation, updating, and deletion.
    """
    # Establish a connection to the database
    conn = get_db_connection()

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute the SQL statement to create the Contact table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Contact (
            id INT AUTO_INCREMENT PRIMARY KEY,
            phoneNumber VARCHAR(255),
            email VARCHAR(255),
            linkedId INT,
            linkPrecedence ENUM('primary', 'secondary') NOT NULL,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deletedAt TIMESTAMP NULL DEFAULT NULL
        )
        """
    )

    # Commit the changes to the database
    conn.commit()

    # Close the cursor and the connection to the database
    cursor.close()
    conn.close()
