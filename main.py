import requests
from bs4 import BeautifulSoup
import logging
import json

# url = 'https://www.amazon.co.uk/gp/product/B07CGNP3RH/ref=ox_sc_saved_title_9?smid=A3P5ROKL5A1OLE&psc=1'
headers = {'User-Agent': 'Safari/605.1.15'}

def user_input():
    while True:
        try:
            url = input("Enter item URL: ")
            price = float(input("Enter desired price (in £): "))

            break
        except ValueError:
            print("Invalid input. Please enter a valid string and a valid double.")

    return url, price

def scrape_data(url, headers):
    try:
        page = requests.get(url=url, headers=headers)

        raw = BeautifulSoup(page.content, 'html.parser')

        return BeautifulSoup(raw.prettify(), "html.parser")
    
    except:
        logging.error("Can't connect to the server")
        
def gather_data(url, price):
    pretty = scrape_data(url, headers)
    try:
        data = {
            "title": pretty.find(id="productTitle").get_text().strip().split(',')[0],
            "price": pretty.find(id="priceValue").get('value')
        }

        dumps = json.dumps(data, indent=4)
        print(dumps)

        if float(data['price']) <= price:
            print(f"Price is lower than {price}")
    except:
        logging.error("Can't find the data")

if __name__ == '__main__':
    url, price = user_input()
    gather_data(url, price)

