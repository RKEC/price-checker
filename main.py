import requests
from bs4 import BeautifulSoup

url = 'https://www.amazon.co.uk/gp/product/B07CGNP3RH/ref=ox_sc_saved_title_9?smid=A3P5ROKL5A1OLE&psc=1'
headers = {'User-Agent': 'Safari/605.1.15'}

def scrape_data(url, headers):
    try:
        page = requests.get(url=url, headers=headers)

        raw = BeautifulSoup(page.content, 'html.parser')

        return BeautifulSoup(raw.prettify(), "html.parser")
    except:
        print("Can't find page")

def gather_data():
    pretty = scrape_data(url, headers)
    try:
        data = {
            "title": pretty.find(id="productTitle").get_text().strip(),
            "price": pretty.find(id="priceValue").get('value')
        }

        print(data)
    except:
        print("Can't find information")

if __name__ == '__main__':
    gather_data()
