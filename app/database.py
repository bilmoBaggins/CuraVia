# database.py
import mysql.connector
import os

MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql_service")
MYSQL_USER = os.getenv("MYSQL_USER", "nhs_user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "nhs_password")
MYSQL_DB = os.getenv("MYSQL_DB", "nhs_ai")

def get_mysql_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )
