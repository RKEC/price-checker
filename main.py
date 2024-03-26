import requests
from bs4 import BeautifulSoup
import logging
import json
import os
import smtplib
from time import sleep
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random

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

            title_element = raw.find(id="productTitle")
            if raw.find(id="twister-plus-price-data-price") is not None:
                price_element = raw.find(id="twister-plus-price-data-price")
            elif raw.find(id="priceValue") is not None:
                price_element = raw.find(id="priceValue")
            else:
                raise ValueError("Cannot find price element on the page.")
            
            brand_element = raw.find(id="bylineInfo")

            image_elements = raw.find(class_="a-dynamic-image")

            if title_element is None or price_element is None or image_elements is None:
                raise ValueError("Cannot find all necessary elements on the page.")

            dynamic_image_data = image_elements.get('data-a-dynamic-image')
            try:
                dynamic_image_dict = json.loads(dynamic_image_data)
            except json.JSONDecodeError:
                logging.error("Error decoding JSON data for image.")

            title = title_element.get_text().strip()
            current_price = float(price_element.get('value'))

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

    while scrape:    
        item_details, image_details = scrape_data(url, headers)
        try:
            if item_details and image_details:

                data = {
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
                if item_details["current_price"] < previous_price:
                    if item_details["current_price"] <= price:
                        send_email(os.getenv('TO_EMAIL'), data)
                previous_price = item_details["current_price"]
                sleep(3600)
            else:
                logging.error("Couldn't find necessary data on the page.")
        except Exception as e:
            logging.error(f"Error occurred while parsing data: {e}")
    else:
        logging.error("No data received from the server.")


def setup_email_server():
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.getenv('SENDER_EMAIL'), os.getenv('SENDER_PASSWORD'))
    return server

def send_email(to_email, data):
    server = setup_email_server()
    message = MIMEMultipart()
    message['From'] = os.getenv('SENDER_EMAIL')
    message['To'] = to_email
    message['Subject'] = 'An item on your wishlist is on sale!'

    price_difference = "{:.2f}".format(data['target_price'] - data['price'])
    current_price = "{:.2f}".format(data['price'])

    body = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    body {{
        font-family: Arial, sans-serif;
    }}
    .container {{
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
    }}
    .title {{
        font-weight: bold;
    }}
    .details {{
        margin-top: 10px;
    }}
    .details li {{
        margin-bottom: 5px;
    }}
    </style>
    </head>
    <body>
    <div class="container">
        <h2>An item on your wishlist is on sale!</h2>
        <br>
        
        <img src="{data['image_url']}" alt="{data['title']}" style="width: {data['image_width']*.75}px; height: {data['image_height']*.75}px; margin: 10px;">
        <br>

        <div class="title"><a href="{data['url']}">{data['title']}</a></div>

        <p>Details: </p>
        <ul class="details"> 
            <li>Current Price: <b>£{current_price}</b></li>
            <li>That's <b>£{price_difference}</b> cheaper than your target price of <b>£{data['target_price']}</b></li>
            <li>Brand: <b>{data['brand']}</b></li>
        </ul>
    </div>
    </body>
    </html>
    """

    message.attach(MIMEText(body, 'html'))
    text = message.as_string()
    server.sendmail(os.getenv('SENDER_EMAIL'), to_email, text)
    server.quit()
    print("Email sent!")

def main():
    load_dotenv()
    url, price = user_input()
    gather_data(url, price)

if __name__ == '__main__':
    main()