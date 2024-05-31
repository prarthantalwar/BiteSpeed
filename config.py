import os
import mysql.connector as sqlc
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    connection = sqlc.connect(
        host=os.getenv("db_host"),
        user=os.getenv("db_user"),
        password=os.getenv("db_password"),
        db=os.getenv("db_name"),
    )
    return connection
