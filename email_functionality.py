from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
import os

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

    body = email_template(data['title'], data['brand'], current_price, data['target_price'], price_difference, data['url'], data['image_url'], data['image_width'], data['image_height'])

    message.attach(MIMEText(body, 'html'))
    text = message.as_string()
    server.sendmail(os.getenv('SENDER_EMAIL'), to_email, text)
    server.quit()
    print("Email sent!")

def email_template(title, brand, current_price, target_price, price_difference, url, image_url, image_width, image_height):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Ubuntu+Mono:ital,wght@0,400;0,700;1,400;1,700&display=swap" rel="stylesheet">
    <style>
    .ubuntu-mono-regular {{
        font-family: "Ubuntu Mono", monospace;
        font-weight: 400;
        font-style: normal;
    }}
    body {{
        font-family: "Ubuntu Mono", sans-serif;
    }}
    h1{{
        color: rgb(8, 48, 177);
        text-align: center;
        font-weight: bold;
        margin: 0;
        font-size: 50px;
    }}
    h2{{
        text-align: center;
    }}
    .container {{
        width: 600px;
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
        background-color:#fff;
        height: 800px;
        max-height: 700px;
        border: black thin solid;
        border-radius: 25px;
    }}
    .details-container{{
        margin: 10px 50px;
        padding: 10px;
        max-width: 500px;
        border: black thin solid;
        border-radius: 25px;
        background-color: rgb(215, 215, 215);
    }}
    .title {{
        margin-top: 10px;
        font-weight: bold;
    }}
    .details {{
        margin-top: 10px;
        list-style-type: none;
    }}
    .details li {{
        margin-bottom: 5px;
        color: black;
    }}
    </style>
    </head>
    <body>
        

    <div class="container">
        <h1><u> richardcode <u></h1>
        <h2>An item on your wishlist is on sale!</h2>
        <br>
        
        <div style="width: {image_width*.75}px; height: {image_height*.75}px; max-width: 400px; max-height: 250px; min-width: 100px; min-height: 100px; display: flex; justify-content: center; margin: 0 auto;">
            <img src="{image_url}" alt="{title}" style="max-width: 100%; max-height: 100%; padding: 10px; display: block; object-fit: contain; display: block; margin: 0 auto;">
        </div>
        <br>

        <div class="details-container">
            <div class="title"><a href="{url}">{title}</a></div>

            <p>Details: </p>
            <ul class="details"> 
                <li>Current Price: <b>£{current_price}</b></li>
                <li>That's <b>£{price_difference}</b> cheaper than your target price of <b>£{target_price}</b></li>
                <li>Brand: <b>{brand}</b></li>
            </ul>
        </div>
    </div>
    </body>
    </html>
    """
