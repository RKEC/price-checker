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
                    "url": url,
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

    price_difference = "{:.2f}".format(data['target_price'] - data['price'])

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
        <p>Good news!</p>
        <p>An item on your wishlist is on sale</p>
        
        <div class="title">{data['title']}</div>
        
        <ul class="details">
            <li>Target Price: <b>£{data['target_price']}</b></li>
            <li>Current Price: <b>£{data['price']}</b></li>
            <li>This represents a price decrease of <b>£{price_difference}</b></li>
        </ul>
        </br>
        
        <p>If you're interested, you can check it out at the following link:</p>
        <p><a href="{data['url']}">{data['url']}</a></p>
    </div>
    </body>
    </html>
    """
    
    message.attach(MIMEText(body, 'html'))

    text = message.as_string()
    server.sendmail(os.getenv('SENDER_EMAIL'), to_email, text)
    server.quit()
    print("Email sent!")


if __name__ == '__main__':
    load_dotenv()
    url, price = user_input()
    gather_data(url, price)
