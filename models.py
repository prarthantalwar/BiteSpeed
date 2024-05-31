from config import get_db_connection


def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
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
            deletedAt TIMESTAMP NULL DEFAULT NULL,
            UNIQUE KEY unique_email_phone (email, phoneNumber)
        )
    """
    )
    conn.commit()
    cursor.close()
    conn.close()


create_tables()
