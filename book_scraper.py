import requests
from bs4 import BeautifulSoup
import re
import json
import os

BASE_URL = "http://books.toscrape.com/"


def clean_price(price_str):
    cleaned_string = re.sub(r'[^\d\.]','',price_str)
    return float(cleaned_string)

def get_exchange_rate():
    try:
        url = "https://www.valuta.se/valuta/gbp-till-sek"
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        rate_element = soup.find("input", {"id": "pair-value"})
        if rate_element:
            return float(rate_element.get("value").replace(',', '.'))

    except:
        pass
    return 13.5


def get_category_url(category_name):

   if not os.path.exists("categories.json"):
       response = requests.get(BASE_URL + "index.html")
       soup = BeautifulSoup(response.content, 'html.parser')
       categories = {}
       for link in soup.find("ul", class_="nav-list").find("ul").find_all("a"):
           categories[link.get_text(strip=True).lower()] = BASE_URL + link['href']

       with open(f"categories.json", "w") as f:
           json.dump(categories, f)

   with open(f"categories.json", "r") as f:
       categories = json.load(f)

   return categories[category_name.lower()]


def fetch_books_from_web(category_url):
    "Scrapar böker från den angivnina URL:en"
    response = requests.get(category_url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    books_data = []
    rate = get_exchange_rate()

    articles = soup.find_all('article', class_='product_pod')

    for index, article in enumerate(articles):
        h3 = article.find('h3')
        title = h3.find('a')['title']

        price_text = article.find('p', class_='price_color').text
        price_gbp = clean_price(price_text)
        price_sek = round(price_gbp * rate, 2)

        rating = article.find('p', class_='star-rating')['class'][1]

        book_id = f"book_{index}"

        books_data.append({
            "id": book_id,
            "title": title,
            "price_gbp": price_gbp,
            "price_sek": price_sek,
            "rating": rating,
        })

    return books_data




