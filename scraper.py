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
    # Placeholder for your scraping logic
    print("Scraping data from:", driver.current_url)
    # Implement the data extraction logic here

def click_next_page():
    try:
        # Check if the 'next page' button's parent li has the 'disabled' class
        next_page_button_parent = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.ais-Pagination-item--nextPage'))
        )
        
        # If the parent element has the 'disabled' class, return False to indicate no more pages
        if 'ais-Pagination-item--disabled' in next_page_button_parent.get_attribute('class'):
            print("Next page button is disabled. No more pages to navigate.")
            return False
        
        # If the button is not disabled, click it to go to the next page
        next_page_button = next_page_button_parent.find_element(By.CSS_SELECTOR, '.ais-Pagination-link')
        if next_page_button:
            next_page_button.click()
            return True
    except (TimeoutException, NoSuchElementException):
        # If there's a timeout or the element is not found, assume no more pages
        return False


def main():
    ##start_url = 'https://www.staples.ca/collections/laptops-90?configure%5Bfilters%5D=tags%3A%22en_CA%22&configure%5BruleContexts%5D%5B0%5D=logged-out&page=1&refinementList%5Bnamed_tags.bopis_eligible%5D%5B0%5D=True&sortBy=shopify_products'  # Replace with the actual URL
    start_url = 'https://www.staples.ca/collections/laptops-90'
    driver.get(start_url)

    accept_cookies()  # Handle the cookie banner at the start
    
    # Example scraping and navigation logic
    try:
        while True:
            scrape_current_page()
            if not click_next_page():
                print("Reached the last page or next page button not clickable.")
                break  # Exit the loop if no next page button is found or clickable
            time.sleep(2)  # Adjust based on the observed behavior of the website
    finally:
        driver.quit()

if __name__ == "__main__":
    main()