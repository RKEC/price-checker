import requests
from bs4 import BeautifulSoup
import logging
import json

def user_input():
    while True:
        try:
            url = input("Enter item URL: ")
            price = float(input("Enter desired price (in £): "))
            break
        except ValueError:
            print("Invalid input. Please enter a valid URL and a valid price.")

    return url, price

def scrape_data(url, headers):
    try:
        page = requests.get(url=url, headers=headers)
        page.raise_for_status()
        raw = BeautifulSoup(page.content, 'html.parser')
        return raw
    except requests.exceptions.MissingSchema:
        logging.error("Invalid URL: No scheme supplied. Please make sure to include http:// or https:// in the URL.")
    except requests.exceptions.ConnectionError:
        logging.error("Can't connect to the server. Please check your internet connection.")

def gather_data(url, price):
    headers = {'User-Agent': 'Safari/605.1.15'}
    pretty = scrape_data(url, headers)
    if pretty:
        try:
            title_element = pretty.find(id="productTitle")
            price_element = pretty.find(id="priceValue")
            if title_element and price_element:
                title = title_element.get_text().strip().split(',')[0]
                price = price_element.get('value')
                data = {
                    "title": title,
                    "price": price
                }
                print(json.dumps(data, indent=4))
                if float(data['price']) <= price:
                    print(f"Price is lower than {price}")
            else:
                logging.error("Couldn't find necessary data on the page.")
        except Exception as e:
            logging.error(f"Error occurred while parsing data: {e}")
    else:
        logging.error("No data received from the server.")

if __name__ == '__main__':
    url, price = user_input()
    gather_data(url, price)
