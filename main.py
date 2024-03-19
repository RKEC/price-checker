import requests
from bs4 import BeautifulSoup
import logging
import json
import os
import smtplib
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
                current_price = price_element.get('value')
                data = {
                    "title": title,
                    "price": float(current_price),
                    "target_price": float(price)
                }
                print(json.dumps(data, indent=4))
                if data['price'] <= price:
                    send_email(os.getenv('TO_EMAIL'), data)
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

    body = f'Item: {data['title']} is on sale at £{data['price']}! This is a price decrease of £{data['target_price'] - data['price']}.'
    message.attach(MIMEText(body, 'plain'))

    text = message.as_string()
    server.sendmail(os.getenv('SENDER_EMAIL'), to_email, text)
    server.quit()
    print("Email sent!")


if __name__ == '__main__':
    load_dotenv()
    url, price = user_input()
    gather_data(url, price)
