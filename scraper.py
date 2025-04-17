#!/usr/bin/env python3
import sqlite3
import time
import logging
import requests
from sql import setup_database

# —— CONFIG —— #
DB_PATH     = "StaplesDB"
PAGE_PAUSE  = 0.2
PER_PAGE    = 50

ALG_APP_ID  = "H5YOVYKINU"
ALG_API_KEY = "e4ce50ff37c38b6132d9a01b2623942c"
ALG_INDEX   = "shopify_products"
ALG_URL     = f"https://{ALG_APP_ID.lower()}-dsn.algolia.net/1/indexes/{ALG_INDEX}/query"
ALG_H       = {
    "X-Algolia-API-Key":        ALG_API_KEY,
    "X-Algolia-Application-Id": ALG_APP_ID,
    "Content-Type":             "application/x-www-form-urlencoded",
}

# logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

def get_all_items():
    page = 0
    while True:
        payload = {"params": f"query=&hitsPerPage={PER_PAGE}&page={page}"}
        logging.debug(f"algolia request page={page}")
        res = requests.post(ALG_URL, headers=ALG_H, data=payload)
        res.raise_for_status()
        js = res.json()
        hits = js.get("hits", [])
        logging.debug(f"received {len(hits)} hits")
        if not hits:
            break

        for idx, item in enumerate(hits, start=1):
            # variants list always present
            var = item["variants"][0]
            sku  = str(var["id"])
            name = item.get("title", "<no title>")
            price = var["price"] / 100.0
            orig  = (var.get("compare_at_price") or var["price"]) / 100.0
            disc  = orig - price
            logging.debug(f"hit#{idx}: sku={sku}, price={price}, discount={disc}")
            yield sku, name, price, disc

        page += 1
        time.sleep(PAGE_PAUSE)

def main():
    logging.info("initializing db")
    setup_database(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()

    total = 0
    start = time.time()
    for sku, name, price, disc in get_all_items():
        logging.info(f"upserting {sku}")
        c.execute(
            """
            INSERT INTO staples(productID, productName, price, discount)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(productID) DO UPDATE SET
              productName=excluded.productName,
              price=excluded.price,
              discount=excluded.discount
            """,
            (sku, name, price, disc),
        )
        c.execute(
            "INSERT INTO PriceHistory(productID, price, discount) VALUES (?,?,?)",
            (sku, price, disc),
        )
        total += 1

    conn.commit()
    conn.close()
    elapsed = time.time() - start
    logging.info(f"finished {total} items in {elapsed:.1f}s")

if __name__ == "__main__":
    main()
