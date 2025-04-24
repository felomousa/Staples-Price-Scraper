# staples-scraper
_Live @_ [tracker.felomousa.com](https://tracker.felomousa.com/)

script that pulls laptop listings from Staples Canada’s Algolia index and Shopify pricing-rules API, storing current historical pricing in SQLite.

## Features
- fetch from Algolia search index  
- batch lookup of discount rules via Shopify pricerules API
- compatible across most shopify storefronts, easily configurable 
- extracts product ID, name, final price, discount, and stock amount for store 93 (Langley)  
- upserts `staples` table and appends to `PriceHistory` each run  
- handles double-encoded JSON, huge page sizes, rate-limit pauses  

## Tech Stack
- **Python** with `requests`, `sqlite3`  
- pulls from Algolia & policy API, avoids manual web scraping using selenium etc. 

## Database Schema

### staples
| column      | type                    |
|-------------|-------------------------|
| productID   | TEXT PRIMARY KEY        |
| productName | TEXT                    |
| price       | REAL                    |
| discount    | REAL                    |
| stock93     | INTEGER                 |

### PriceHistory
| column       | type                            |
|--------------|---------------------------------|
| historyID    | INTEGER PRIMARY KEY AUTOINCREMENT |
| productID    | TEXT (FK)                       |
| price        | REAL                            |
| discount     | REAL                            |
| stock93      | INTEGER                         |
| dateRecorded | DATETIME (default: now)         |

## Usage

1. `pip install requests`  
2. ensure `StaplesDB` does not conflict with existing files  
3. ```python scraper.py```

output: updated StaplesDB file with current and historical data

## changes since v1 (Selenium-based)

- the scraper now uses direct algolia and shopify pricerules api requests instead of headless selenium browser automation.  it retrieves variant id, name, price, discount, and store-specific stock in a single paginated json query rather than clicking through dom pages.

