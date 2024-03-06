from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup
import csv

geckodriver_path = './geckodriver'

options = FirefoxOptions()
options.add_argument("--headless")
service = Service(executable_path=geckodriver_path)
driver = webdriver.Firefox(service=service, options=options)

url = 'https://www.staples.ca/collections/laptops-90'

driver.get(url)
driver.implicitly_wait(10)

page_source = driver.page_source

soup = BeautifulSoup(page_source, 'html.parser')

## Here is what we're trying to parse:
## <span class="money pre-money" data-product-id="(example product id)" style="visibility: visible;">$(example amount)</span>

products = soup.find_all('span', class_='money pre-money')

with open('products.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Product ID', 'Price'])

    for product in products:
        product_id = product.get('data-product-id')
        price = product.text.strip()
        if product_id and price:
            writer.writerow([product_id, price])

driver.quit()
