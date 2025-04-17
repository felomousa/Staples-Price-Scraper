import sqlite3
import time
import logging
import requests
import json
from itertools import islice
from sql import setup_database

DB_PATH        = "StaplesDB"  # path to SQLite database
ALG_APP_ID     = "H5YOVYKINU"  # Algolia app ID from network headers
ALG_API_KEY    = "e4ce50ff37c38b6132d9a01b2623942c"  # Algolia search API key
INDEX          = "shopify_products"
ALG_URL        = f"https://{ALG_APP_ID.lower()}-dsn.algolia.net/1/indexes/{INDEX}/query"
ALG_HEADERS    = {
    "X-Algolia-API-Key":        ALG_API_KEY,
    "X-Algolia-Application-Id": ALG_APP_ID,
    "Content-Type":             "application/json",
    "X-Algolia-Agent":          "Algolia for JavaScript (4.10.5); Browser"
}

# base payload for Algolia search: empty query + filters for en_CA laptops collection
BASE_PAYLOAD = {
    "query": "",
    "attributesToRetrieve": [
        "title", "compare_at_price", "handle", "id", "image",
        "named_tags", "objectID", "price", "sku", "meta",
        "store_inventory", "fc"
    ],
    "filters": 'tags:en_CA AND NOT named_tags.channel_availability:"PCAM Only" AND collections:"laptops-90"',
    "facets": ["*"], "facetFilters": [[]],
    "numericFilters": [], "clickAnalytics": True,
    "getRankingInfo": True, "optionalFilters": []
}

ALG_PAGE_SIZE    = 300    # can bump to 1000 but watch for rate limits
ALG_PAUSE        = 0.2    # seconds between Algolia page requests

# Endpoint for fetching discount rules per Shopify variant
PRICE_RULES_URL   = (
    "https://api.staples.ca/pre/policy/execution/ext/v1.0/"
    "go_pre/pricerules/staples-canada.myshopify.com/rulesets"
)
RULES_BATCH_SIZE = 100    # number of variant IDs per rules request
RULES_PAUSE      = 0.2    # seconds between rules requests

# configure logging for progress output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

def fetch_algolia_items():
    session = requests.Session()
    session.headers.update(ALG_HEADERS)
    page = 0
    while True:
        payload = BASE_PAYLOAD.copy()
        payload.update({"page": page, "hitsPerPage": ALG_PAGE_SIZE})
        logging.info(f"Algolia page {page}")
        r = session.post(ALG_URL, json=payload)
        r.raise_for_status()

        hits = r.json().get("hits", [])
        if not hits:
            break  # no more pages

        for item in hits:
            vid   = str(item["id"])
            name  = item.get("title", "").strip()
            base  = float(item.get("price", 0.0))
            # pull stock count for store 93 (langley)
            stock = next(
                (inv["store_93"] for inv in item.get("store_inventory", [])
                 if "store_93" in inv),
                0
            )
            yield {"variant_id": vid, "name": name, "base_price": base, "stock93": stock}

        page += 1
        time.sleep(ALG_PAUSE)

def fetch_price_rules(ids):
    # fetch discount rules for a batch of variant IDs
    params = {"products": ",".join(ids)}
    headers = {"Origin": "https://www.staples.ca"}
    r = requests.get(PRICE_RULES_URL, params=params, headers=headers)
    r.raise_for_status()

    # handle possible double-encoded JSON
    try:
        data = r.json()
    except ValueError:
        data = json.loads(r.text)

    # extract list of rulesets
    rulesets = data.get("results") or data.get("rulesets") or (data if isinstance(data, list) else [])
    out = {}
    for raw in rulesets:
        rule = json.loads(raw) if isinstance(raw, str) else raw
        actions = rule.get("actions") or (rule.get("rules", [{}])[0].get("actions", []))
        if not actions:
            continue
        # map each selected product to its new price
        for sel in rule.get("product_selection", {}).get("products", []):
            pid = sel.get("product_id") or sel.get("variant_id")
            val = actions[0].get("value")
            if pid and val is not None:
                out[str(pid)] = float(val) / 100.0  # convert cents to dollars (it's in cents for some reason lol)
    return out

def batched(it, n):
    # yield successive n-sized chunks
    it = iter(it)
    while True:
        batch = list(islice(it, n))
        if not batch:
            return
        yield batch

def main():
    logging.info("init db")
    setup_database(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    total = 0

    # fetch all products from Algolia first
    items = list(fetch_algolia_items())
    logging.info(f"got {len(items)} items")

    # process in batches to avoid long URLs
    for batch in batched(items, RULES_BATCH_SIZE):
        vids  = [i["variant_id"] for i in batch]
        rules = fetch_price_rules(vids)
        time.sleep(RULES_PAUSE)

        for itm in batch:
            vid   = itm["variant_id"]
            name  = itm["name"]
            base  = itm["base_price"]
            stock = itm["stock93"]
            final = rules.get(vid, base)
            disc  = round(base - final, 2)

            # fix weird discounts (>99% off)
            if disc > (base * 0.99):
                final, disc = base, 0.0

            # upsert latest price & stock
            c.execute("""
                INSERT INTO staples(productID,productName,price,discount,stock93)
                VALUES(?,?,?,?,?)
                ON CONFLICT(productID) DO UPDATE SET
                  productName=excluded.productName,
                  price=excluded.price,
                  discount=excluded.discount,
                  stock93=excluded.stock93
            """, (vid, name, final, disc, stock))

            # record price history
            c.execute("""
                INSERT INTO PriceHistory(productID,price,discount,stock93)
                VALUES(?,?,?,?)
            """, (vid, final, disc, stock))

            total += 1

        conn.commit()

    conn.close()
    logging.info(f"done, wrote {total} rows")

if __name__ == "__main__":
    main()
