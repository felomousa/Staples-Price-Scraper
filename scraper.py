from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

geckodriver_path = './geckodriver'

options = FirefoxOptions()
options.add_argument("--headless")
service = Service(executable_path=geckodriver_path)
driver = webdriver.Firefox(service=service, options=options)

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
    print("Scraping data from:", driver.current_url)
    # Wait for the items to be visible on the page before scraping
    WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'ais-hits--item')))
    items = driver.find_elements(By.CLASS_NAME, 'ais-hits--item')
    return len(items)

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
            next_page_button.click()
            # Wait for the items to be visible on the next page to ensure the page has loaded
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'ais-hits--item')))
            return True
    except (TimeoutException, NoSuchElementException):
        return False

def main():
    start_url = 'https://www.staples.ca/collections/laptops-90?page=1&refinementList%5Bnamed_tags.bopis_eligible%5D%5B0%5D=True'
    driver.get(start_url)

    accept_cookies()  # Handle the cookie banner at the start
    
    try:
        while True:
            item_count = scrape_current_page()
            print(f"Scraped {item_count} items from the page.")
            if not click_next_page():
                print("Reached the last page or next page button not clickable.")
                break
            time.sleep(2)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
