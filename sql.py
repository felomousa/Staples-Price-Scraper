import sqlite3

def setup_database(db_path: str = 'StaplesDB'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # products table, now including stock93
    c.execute('''
        CREATE TABLE IF NOT EXISTS staples(
            productID   TEXT    PRIMARY KEY,
            productName TEXT,
            price       REAL,
            discount    REAL,
            stock93     INTEGER DEFAULT 0
        )
    ''')

    # price history table, now including stock93
    c.execute('''
        CREATE TABLE IF NOT EXISTS PriceHistory(
            historyID   INTEGER PRIMARY KEY AUTOINCREMENT,
            productID   TEXT,
            price       REAL,
            discount    REAL,
            stock93     INTEGER DEFAULT 0,
            dateRecorded DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (productID) REFERENCES staples(productID)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_database()
