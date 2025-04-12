# staples-scraper

Headless Selenium script that scrapes laptop listings from [staples.ca](https://www.staples.ca/collections/laptops-90), storing product info and historical prices in SQLite.

## Features
- extracts product ID, name, current price, and discount  
- navigates through paginated listings  
- stores data in `staples` and `PriceHistory` tables  
- updates existing entries, logs price history  

## Tech Stack
- **Python** with `selenium`, `sqlite3`
- **Firefox** (headless) via `geckodriver`

## Database Schema

### staples
| column       | type   |
|--------------|--------|
| productID    | TEXT PRIMARY KEY |
| productName  | TEXT   |
| price        | REAL   |
| discount     | REAL   |

### PriceHistory
| column       | type   |
|--------------|--------|
| historyID    | INTEGER PRIMARY KEY AUTOINCREMENT |
| productID    | TEXT (FK) |
| price        | REAL   |
| discount     | REAL   |
| dateRecorded | DATETIME (default: now) |

## Usage

1. install Firefox + geckodriver  
2. run:
   ```bash
   python script.py
   ```
3. output: `StaplesDB` sqlite database file

## Skills Highlighted

- web scraping with Selenium (headless, paginated navigation)
- DOM interaction and error handling (timeouts, intercepts, fallbacks)
- real-time data extraction and parsing
- SQLite database design and CRUD operations
- browser automation with Firefox and geckodriver
- data deduplication and historical tracking logic
- basic ETL pattern in Python scripts
