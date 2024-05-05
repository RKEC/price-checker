import requests
import logging
import json
import os
import argparse

from time import sleep
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from email_functionality import send_email

skill = False

def welcome():
    message = r"""
                  _      _                   _               _       
                 (_)    | |                 | |             | |      
             _ __ _  ___| |__   __ _ _ __ __| | ___ ___   __| | ___  
            | '__| |/ __| '_ \ / _` | '__/ _` |/ __/ _ \ / _` |/ _ \ 
            | |  | | (__| | | | (_| | | | (_| | (_| (_) | (_| |  __/ 
            |_|  |_|\___|_| |_|\__,_|_|  \__,_|\___\___/ \__,_|\___|                                                                                                                                        
            """
    
    print(message)


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
    while True:
        try:
            page = requests.get(url=url, headers=headers, timeout=30)
            page.raise_for_status()  # Raise an exception for HTTP errors
            raw = BeautifulSoup(page.content, 'html.parser')

            try:
                title_element = raw.find(id="productTitle")
            except Exception:
                raise Exception("Cannot find title element on the page.")

            try:
                if raw.find(id="priceValue") is not None:
                    price_element = raw.find(id="priceValue")
                    price_element = price_element.get('value')
                elif raw.find(id="twister-plus-price-data-price") is not None:
                    price_element = raw.find(id="twister-plus-price-data-price").get('value')
                elif raw.find("span", class_="aok-offscreen") is not None:
                    price_element = raw.find("span", class_="aok-offscreen")
                    price_element = price_element.get_text().replace("£","")
                else:
                    raise Exception("Cannot find price element on the page.")
            except Exception:
                raise Exception("Cannot find price element on the page.")
            
            try:
                brand_element = raw.find(id="bylineInfo")
            except Exception:
                raise Exception("Cannot find brand element on the page.")

            try:
                image_elements = raw.find(class_="a-dynamic-image")
            except Exception:
                raise Exception("Cannot find image element on the page.")

            if title_element is None or price_element is None or image_elements is None:
                raise ValueError("Cannot find all necessary elements on the page.")

            dynamic_image_data = image_elements.get('data-a-dynamic-image')
            try:
                dynamic_image_dict = json.loads(dynamic_image_data)
            except json.JSONDecodeError:
                logging.error("Error decoding JSON data for image.")

            title = title_element.get_text().strip()
            current_price = float(price_element)

            brand_href = brand_element.get('href')
            start_index = brand_href.find("/stores/") + len("/stores/")
            end_index = brand_href.find("/page")     
            brand_name = brand_href[start_index:end_index]
            
            if start_index == -1 or end_index == -1:
                brand_name = "Unknown"

            image_url = list(dynamic_image_dict.keys())[2]
            image_dimensions = list(dynamic_image_dict.values())[2]

            item_details = {
                "brand": brand_name,
                "title": title,
                "current_price": current_price
            }

            image_details = {
                "url": image_url,
                "width": image_dimensions[0],
                "height": image_dimensions[1]
            }

            return item_details, image_details
        except requests.exceptions.MissingSchema:
            logging.error("Invalid URL: No scheme supplied. Please make sure to include http:// or https:// in the URL.")
        except requests.exceptions.ConnectionError:
            logging.error("Can't connect to the server. Please check your internet connection.")
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP Error: {e.response.status_code}")
        except ValueError as ve:
            logging.error(f"ValueError: {ve}")
        except Exception as ex:
            logging.error(f"An unexpected error occurred: {ex}")

def gather_data(url, price, scrape=True):
    headers = {'User-Agent': 'Safari/605.1.15'}
    previous_price = float('inf')
    data = {}

    while scrape:    
        item_details, image_details = scrape_data(url, headers)
        try:
            if item_details and image_details:

                product = {
                    "url": url,
                    "brand": item_details["brand"],
                    "title": item_details["title"],
                    "price": item_details["current_price"],
                    "target_price": price,
                    "previous_price": previous_price,
                    "image_url": image_details['url'],
                    "image_width": image_details['width'],
                    "image_height": image_details['height']
                }

                data[len(data.keys())] = product

                logging.info(f"Data received from the server: {product}")
                if item_details["current_price"] < previous_price:
                    if item_details["current_price"] <= price:
                        send_email(os.getenv('TO_EMAIL'), product)
                previous_price = item_details["current_price"]
                sleep(3600)
            else:
                logging.error("Couldn't find necessary data on the page.")
        except Exception as e:
            logging.error(f"Error occurred while parsing data: {e}")
    else:
        logging.error("No data received from the server.")

def main():
    welcome()
    load_dotenv()
    gather_data(os.getenv('URL'), float(os.getenv('PRICE')))


if __name__ == '__main__':
    main()