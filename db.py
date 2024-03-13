import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Retrieve environment variables using appropriate keys
db_user = os.getenv('DB_USER')
db_pw = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

def get_db_conn():
    # Construct the connection string
    conn = mysql.connector.connect(
        user=db_user,
        password=db_pw,
        host=db_host,
        port=db_port,
        database=db_name,
        ssl_disabled=True
    )
    return conn


if __name__ == "__main__":
    print(db_user)
    print(db_name)
    print(db_port)
    print(db_pw)
    print(db_host)
    conn = get_db_conn()
    if conn.is_connected():
        print("Successfully connected to the database")
        conn.close()
    else:
        print("Database connection failed")
