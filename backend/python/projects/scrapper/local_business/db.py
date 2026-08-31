import sqlite3

def create_db(db_name: string="businesses.db", create_only: bool=true):
    conn = sqlite3.connect(db_name)

    try:
        cursor = conn.cursor()

        # Create table
        cursor.execute('''CREATE TABLE IF NOT EXISTS businesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            website TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        if create_only:
            conn.close()

def get_connection(db_path: str) -> sqlite3.Connection:
    # Connect to the SQLite database and create the schema if it doesn't exist.
    conn  = sqlite3.connect(db_path)
    
    try:
        cur   = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS businesses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT   NOT NULL,
            phone       TEXT   ,
            address     TEXT   ,
            website     TEXT   ,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
    except Exception as e:
        logging.warning(f"Table already existed — skipping CREATE: {e}")
    
    conn.commit()
    return conn

if __name__ == "__main__":
    create_db()