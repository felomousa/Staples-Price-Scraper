import sqlite3

def setup_database(db_path: str = 'StaplesDB'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    #products table
    c.execute('''
        CREATE TABLE IF NOT EXISTS staples(
            productID TEXT PRIMARY KEY,
            productName TEXT,
            price REAL,
            discount REAL
        )
    ''')
    #price history table
    c.execute('''
        CREATE TABLE IF NOT EXISTS PriceHistory(
            historyID INTEGER PRIMARY KEY AUTOINCREMENT,
            productID TEXT,
            price REAL,
            discount REAL,
            dateRecorded DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (productID) REFERENCES staples(productID)
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_database()
    print("database initialized")
