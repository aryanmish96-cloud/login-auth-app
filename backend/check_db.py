from db_config import get_db_connection, init_db
import mysql.connector

def test_connection():
    print("Attempting to connect to MySQL...")
    try:
        # First try to initialize (create DB if not exists)
        init_db()
        print("Database initialization successful (or already initialized).")
        
        # Then try to get a connection to the specific DB
        conn = get_db_connection()
        if conn and conn.is_connected():
            print("Successfully connected to the database!")
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"Tables in database: {[t[0] for t in tables]}")
            cursor.close()
            conn.close()
            return True
        else:
            print("Failed to connect to the database.")
            return False
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    test_connection()
