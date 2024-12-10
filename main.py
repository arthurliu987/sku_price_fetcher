import base64
from enum import Enum
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

class State(Enum):
    sku_input_state = 1
    confirmation_request_state = 2
    confirmed_state = 3
    finished_state = 4

class SearchResult(object):
    source = ''
    name = ''
    price = ''
    url = ''

    def __init__(self, source, name, price, url):
        self.source = source
        self.name = name
        self.price = price
        self.url = url



CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
EBAY_ENDPOINT = "https://api.ebay.com/buy/browse/v1/item_summary/search"
TEST_SKU = "761294512418"

searchResults = []

def get_ebay_access_token():
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
    }
    payload = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }

    response = requests.post(
        url,
        headers=headers,
        data=payload,
    )

    if response.status_code == 200:
        token = response.json()["access_token"]
        return token
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def get_ebay_price(sku):
    token = get_ebay_access_token()

    # return token
    headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
    params = {
        "q": sku,
        "limit": 1,
    }
    
    response = requests.get(EBAY_ENDPOINT, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        try:
            price = data["itemSummaries"][0]["price"]["value"]
            currency = data["itemSummaries"][0]["price"]["currency"]
            return f"{price} {currency}"
        except (IndexError, KeyError):
            return "Price not available"
    else:
        return f"Error: {response.status_code} {response.text}"


def get_item_name(sku):
    url = "https://go-upc.com/search?q=" + sku
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("h1")  
        return(title.text.strip()) 

    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

def get_guitar_center_price(sku):
    url = "https://www.guitarcenter.com/search?typeAheadSuggestion=true&fromRecentHistory=false&Ntt=roland%20ax%20edge"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }

    # Make the GET request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Find and extract the relevant data (e.g., product titles)
        product_titles = soup.find_all("div", class_="plp-product-details")

        # Print the product titles
        for title in product_titles:
            product_text = title.text.strip()
            split_product_text = product_text.split("$")
            title_href = title.find("a", href=True)
            print(title_href['href'])

            searchResults.append(SearchResult(source="Guitar Center", name=split_product_text[0], price=split_product_text[1], url=title_href['href']))
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")


def main():
    # results = list[SearchResult] = []

    # state = State.sku_input_state
    # confirmation = "n"

    # while state != State.confirmed_state:
    #     if state == State.sku_input_state:
    #         sku = input("Enter the SKU: ")
    #         item_name = get_item_name(sku)
    #         print(f'The item name for the product code is {item_name}')
    #         print(f'Is this correct?')
    #         state = State.confirmation_request_state
    #     elif state == State.confirmation_request_state:
    #         confirmation = input(f' ("y" or "n")')
    #         if confirmation == 'y':
    #             state = State.confirmed_state
    #             break
    #         if confirmation == 'n':
    #             state = State.sku_input_state
    #         else:
    #             print("unrecognized input")

    
    # amazon_price = get_amazon_price(sku)
    ebay_price = get_ebay_price(TEST_SKU)
    guitar_price = get_guitar_center_price(TEST_SKU)

    print("Results:")
    for result in searchResults:
        print(f"Source: {result.source}")
        print(f"Name: {result.name}")
        print(f"Price: {result.price}")
        print(f"URL: {result.url}")
        print("\n")
    
    # print(f"Amazon Price: {amazon_price}")
    print(f"eBay Price: {ebay_price}")

if __name__ == "__main__":
    main()