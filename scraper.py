from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
import sqlite3
import time

geckodriver_path = './geckodriver'
options = FirefoxOptions()
options.add_argument("--headless")
service = Service(executable_path=geckodriver_path)
driver = webdriver.Firefox(service=service, options=options)

conn = sqlite3.connect('StaplesDB')
c = conn.cursor()

def setup_database():
    c.execute('''CREATE TABLE IF NOT EXISTS staples(
                    productID TEXT PRIMARY KEY,
                    productName TEXT,
                    price REAL,
                    discount REAL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS PriceHistory(
                    historyID INTEGER PRIMARY KEY AUTOINCREMENT,
                    productID TEXT,
                    price REAL,
                    discount REAL,
                    dateRecorded DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (productID) REFERENCES staples(productID))''')
    conn.commit()

def accept_cookies():
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.cookie-banner button'))
        )
        accept_button.click()
        print("Cookie banner accepted.")
    except TimeoutException:
        print("No cookie banner found or it's not clickable.")

def update_staples_table(productID, productName, price, discount):
    c.execute('''SELECT productID FROM staples WHERE productID = ?''', (productID,))
    data = c.fetchone()
    if data is None:
        c.execute('''INSERT INTO staples(productID, productName, price, discount) VALUES(?,?,?,?)''', 
                  (productID, productName, price, discount))
    else:
        c.execute('''UPDATE staples SET productName = ?, price = ?, discount = ? WHERE productID = ?''', 
                  (productName, price, discount, productID))
    conn.commit()

def scrape_current_page():
    WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'ais-hits--item')))
    items = driver.find_elements(By.CLASS_NAME, 'ais-hits--item')
        
    for item in items:
        product_link = item.find_element(By.CSS_SELECTOR, '.product-thumbnail__title.product-link')
        productName = product_link.text
        price_info = item.find_element(By.CSS_SELECTOR, '.money.pre-money')
        price = price_info.text
        productID = price_info.get_attribute('data-product-id')
        discount = "No discount"
        discount_elements = item.find_elements(By.TAG_NAME, 'strike')
        if discount_elements:
            discount_text = discount_elements[0].text.replace('$', '').replace(',', '')
            discount = float(discount_text)
        price_text = price.replace('$', '').replace(',', '')
        price = float(price_text)

        if discount != "No discount":
            discount = discount - price

        update_staples_table(productID, productName, price, discount)
        c.execute('''INSERT INTO PriceHistory(productID, price, discount) VALUES(?,?,?)''', 
                  (productID, price, discount))
        conn.commit()

def click_next_page():
    try:
        next_page_button_parent = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.ais-Pagination-item--nextPage'))
        )
        if 'ais-Pagination-item--disabled' in next_page_button_parent.get_attribute('class'):
            print("Next page button is disabled. No more pages to navigate.")
            return False
        
        next_page_button = next_page_button_parent.find_element(By.CSS_SELECTOR, '.ais-Pagination-link')
        if next_page_button:
            driver.execute_script("arguments[0].scrollIntoView();", next_page_button)
            time.sleep(1)
            try:
                next_page_button.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", next_page_button)
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'ais-hits--item')))
            return True
    except (TimeoutException, NoSuchElementException):
        return False

def main():
    setup_database()  # Ensure the database is set up before starting
    driver.get('https://www.staples.ca/collections/laptops-90')
    accept_cookies()

    try:
        while True:
            scrape_current_page()
            if not click_next_page():
                break
            time.sleep(2)
    finally:
        driver.quit()
        conn.close()

if __name__ == "__main__":
    main()
