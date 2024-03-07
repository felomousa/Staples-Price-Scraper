from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
from bs4 import BeautifulSoup

geckodriver_path = './geckodriver'

options = FirefoxOptions()
options.add_argument("--headless")
service = Service(executable_path=geckodriver_path)
driver = webdriver.Firefox(service=service, options=options)

urls = [
    'https://www.staples.ca/collections/laptops-90',
]



for url in urls:
    driver.get(url)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ais-hits--item')))

    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Adjust this depending on your internet speed and the response time of the website
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    product_items = soup.find_all('div', class_='ais-hits--item')
    print("Number of items in product_items:", len(product_items))
driver.quit()