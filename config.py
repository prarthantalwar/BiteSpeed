import os
import mysql.connector as sqlc
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()


def get_db_connection():
    """
    Establishes a connection to the MySQL database using credentials from environment variables.

    Returns:
        connection: A MySQL database connection object.
    """

    # Connect to the database using credentials stored in environment variables
    connection = sqlc.connect(
        host=os.getenv("db_host"),  # Database host address
        user=os.getenv("db_user"),  # Database username
        password=os.getenv("db_password"),  # Database password
        db=os.getenv("db_name"),  # Database name
    )

    return connection  # Return the database connection object
