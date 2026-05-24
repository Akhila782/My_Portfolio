import pymysql
from pymysql import Error

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Sai#0709" 
DB_NAME = "portfolio"

def create_table():
    try:
        print(f"Connecting to MySQL ({DB_HOST}) as {DB_USER}...")
        # Connect to MySQL first without specifying DB to ensure it exists
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        if connection.open:
            cursor = connection.cursor()
            print(f"Ensuring database '{DB_NAME}' exists...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            connection.select_db(DB_NAME)
            print(f"Successfully connected to database: {DB_NAME}")
            
            # Create the messages table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                subject VARCHAR(255),
                budget VARCHAR(255),
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            print("Creating 'messages' table if it doesn't exist...")
            cursor.execute(create_table_query)
            print("Table 'messages' is ready!")
            
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        print("\nPlease check:")
        print("1. Is MySQL server running?")
        print("2. Is the database 'portfolio' created? (CREATE DATABASE portfolio;)")
        print("3. Is your MySQL password correct in this script and app.py?")
    finally:
        if 'connection' in locals() and connection.open:
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")

if __name__ == '__main__':
    create_table()
