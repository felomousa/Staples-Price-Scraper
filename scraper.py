from selenium import webdriver
import sqlite3
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
import time

geckodriver_path = './geckodriver'
options = FirefoxOptions()
options.add_argument("--headless")
service = Service(executable_path=geckodriver_path)
driver = webdriver.Firefox(service=service, options=options)

conn = sqlite3.connect('StaplesDB')
c = conn.cursor()
c.execute('''CREATE TABLE staples(productID TEXT, productName TEXT, price INT, discount INT)''')




def accept_cookies():
    try:
        # Target the 'Accept All' button specifically within the cookie banner
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.cookie-banner button'))
        )
        accept_button.click()
        print("Cookie banner accepted.")
    except TimeoutException:
        print("No cookie banner found or it's not clickable.")

def scrape_current_page():
    #print("Scraping data from:", driver.current_url)
    WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'ais-hits--item')))
    items = driver.find_elements(By.CLASS_NAME, 'ais-hits--item')
        
    for index, item in enumerate(items):
        product_link = item.find_element(By.CSS_SELECTOR, '.product-thumbnail__title.product-link')
        productName = product_link.text
        price_info = item.find_element(By.CSS_SELECTOR, '.money.pre-money')
        price = price_info.text
        productID = price_info.get_attribute('data-product-id')  # Extracting product ID
        discount = "No discount"
        discount_elements = item.find_elements(By.TAG_NAME, 'strike')
        if discount_elements:
            discount = discount_elements[0].text
            discount = discount - price
        c.execute('''INSERT INTO staples VALUES(?,?,?,?)''', (productID, productName, price, discount))
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
            # Scroll the next page button into view
            driver.execute_script("arguments[0].scrollIntoView();", next_page_button)
            time.sleep(1)  # Adding a brief delay to ensure the page adjusts before clicking
            
            try:
                # Attempt to click the button normally
                next_page_button.click()
            except ElementClickInterceptedException:
                # If a normal click doesn't work, use JavaScript to force the click
                driver.execute_script("arguments[0].click();", next_page_button)
            
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'ais-hits--item')))
            return True
    except (TimeoutException, NoSuchElementException):
        return False

def main():
    driver.get('https://www.staples.ca/collections/laptops-90')

    accept_cookies()  # Handle the cookie banner at the start

    all_data = []
    try:
        while True:
            scrape_current_page()
            if not click_next_page():
                print("Reached the last page or next page button not clickable.")
                break
            time.sleep(2)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
