import os
import psycopg2
from dotenv import load_dotenv

# Explicitly load the .env file
load_dotenv('.env')

# connection details
db_host = "127.0.0.1"
db_port = "5433"
db_name = "faceswap"
db_user = "postgres"
db_password = "password"

print(f"Attempting connection to: postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

try:
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )
    print("SUCCESS: Connection established!")
    conn.close()
except Exception as e:
    print(f"FAILURE: {e}")
