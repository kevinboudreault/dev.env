import csv, sqlite3, logging, os


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


def import_csv(db_path: str, csv_file: str) -> int:
    # Setup Logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    LOGGER = logging.getLogger(__name__)

    # Read CSV and insert each unique record into businesses.
    if not os.path.isfile(csv_file):
        logging.error(f"CSV file missing at : {os.path.abspath(csv_file)}")
        return 0
    
    conn   = get_connection(db_path)
    cur    = conn.cursor()
    
    records: list[dict] = []

    with open(csv_file, 'r', encoding='utf-8') as fh:
        for row in csv.DictReader(fh):
            name       = (row.get('name') or '').strip()
            phone      = ((row.get('phone')  or '')).strip() if row.get('phone') else None
            address    = ((row.get('address') or '')).strip() if row.get('address') else None
            website    = ((row.get('website') or '')).strip() if row.get('website') else None
            records.append({'name': name, 'phone': phone, 'address': address, 'website': website})

    inserted = 0
    for row in records:
        cur.execute("""SELECT COUNT(*) FROM businesses WHERE name=?""", (row['name'],))
        cnt   = cur.fetchone()[0] if cur.description else 0

        if cnt == 0:
            try:
                cur.execute(
                    "INSERT INTO businesses(name, phone, address, website) VALUES (?, ?, ?, ?)",
                    (row['name'], row['phone'], row['address'], row['website'])
                )
                inserted += 1
            except Exception as e:
                logging.error(f"Failed to insert record: {e}")

    conn.commit()
    LOGGER.info(f"Inserted: {inserted} | Read from CSV: {len(records)}")
    return inserted


if __name__ == '__main__':
    db_path   = input("DB path: ").strip() or 'businesses.db'
    csv_file  = input("_csv_file_ :").strip() or 'belleville_businesses.csv'

    import_csv(db_path, csv_file)