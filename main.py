import base64
from enum import Enum
import json
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
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
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

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    params = {
        "q": sku,
        "limit": 5,
    }

    response = requests.get(EBAY_ENDPOINT, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        try:
            for itemSummary in data["itemSummaries"]:
                title = itemSummary["title"]
                price = itemSummary["price"]["value"]
                url = itemSummary["itemWebUrl"]
                searchResults.append(SearchResult(
                    source="Ebay", name=title, price=price, url=url))

        except (IndexError, KeyError):
            return "Price not available"

        print("Ebay Results Fetched")
    else:
        return f"Error: {response.status_code} {response.text}"


def get_item_name(sku):
    url = "https://go-upc.com/search?q=" + sku
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("h1")
        return (title.text.strip())

    else:
        print(f"Failed to retrieve item name. Status code: {
              response.status_code}")


def get_guitar_center_price(item_name):
    url = "https://www.guitarcenter.com/search?typeAheadSuggestion=true&fromRecentHistory=false&Ntt=" + item_name

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        # when querying guitar center, it can either return a list of products or a single product page if the match is close enough
        # if the product_titles is empty, then we are on a single product page
        product_titles = soup.find_all("div", class_="plp-product-details")

        if product_titles == []:
            product_name = soup.find("h1").text.strip() if soup.find(
                "h1") else "Product name not found"
            data = soup.find("script", id="__NEXT_DATA__",
                             type="application/json")
            jsondata = json.loads(data.text)

            # getting the product price is a horrendous process
            product_price = jsondata["props"]["pageProps"]["dehydratedState"]["queries"][
                0]["state"]["data"]["PDPStyleSelector"]['styleSelectorArr'][0]['salePrice']

            searchResults.append(SearchResult(
                source="Guitar Center", name=product_name, price=product_price, url=response.url))

            print("Guitar Center Results Fetched")
        else:
            for title in product_titles:
                product_text = title.text.strip()
                split_product_text = product_text.split("$")
                title_href = title.find("a", href=True)
                print(title_href['href'])

                searchResults.append(SearchResult(
                    source="Guitar Center", name=split_product_text[0], price=split_product_text[1], url="https://www.guitarcenter.com" + title_href['href']))

            print("Guitar Center Results Fetched")
    else:
        print(f"Failed to retrieve guitar center price. Status code: {
              response.status_code}")


def get_amazon_results(search_query):
    google_search_url = "https://www.googleapis.com/customsearch/v1"
    amazon_urls = []

    # Parameters for the API request
    params = {
        "key": GOOGLE_API_KEY,
        "cx": "b3d9512d0c5d2447a",        # Custom Search Engine ID
        "q": search_query,
        "num": 10,           # Number of results (max 10 per request)
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }

    response = requests.get(google_search_url, params=params)

    if response.status_code == 200:
        results = response.json().get("items", [])
        for item in results:
            link = item.get("link")
            amazon_urls.append(link)
    else:
        print(f"Error: {response.status_code}, {response.text}")

    if amazon_urls == []:
        print("No Amazon results found")
        return

    # generally speaking there's only 1 amazon url. Repeat urls from the google search lead back to the same page, so we only need to check the first one
    response = requests.get(amazon_urls[0])
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract the product title
        title_element = soup.find("span", id="productTitle")
        product_title = title_element.text.strip() if title_element else "Title not found"

        # Extract the product price
        price_element = soup.find("span", class_="a-price-whole")
        price_fraction_element = soup.find("span", class_="a-price-fraction")

        if price_element:
            product_price = price_element.text.strip()
            if price_fraction_element:
                product_price += price_fraction_element.text.strip()

            searchResults.append(SearchResult(
                source="Amazon", name=product_title, price=product_price, url=amazon_urls[0]))
            print("Amazon Results Fetched")
        else:
            product_price = "Price not found"
    else:
        print(f"Failed to retrieve amazon price. Status code: {
              response.status_code}")


def get_user_input(prompt):
    "Helper function to get user input and handle quitting."
    user_input = input(prompt)
    if user_input.lower() == 'q':
        print("Quitting the program...")
        exit()
    return user_input


def main():
    state = State.sku_input_state
    confirmation = "n"
    sku = ""

    print(f'Welcome to SKU Price Fetcher (press \'q\' anytime to quit)')

    while state != State.confirmed_state:
        if confirmation == 'q':
            return

        if state == State.sku_input_state:
            sku = get_user_input("Enter the SKU: ")
            item_name = get_item_name(sku)
            print(f'The item name for the product code is {item_name}')
            print(f'Is this correct?')
            state = State.confirmation_request_state
        elif state == State.confirmation_request_state:
            confirmation = get_user_input(f' ("y" or "n")')
            if confirmation == 'y':
                state = State.confirmed_state
                break
            if confirmation == 'n':
                state = State.sku_input_state
            else:
                print("unrecognized input")

    print(f"Fetching Product info for SKU: {sku} ...")

    get_ebay_price(sku)
    get_guitar_center_price("Roland AX-Edge Keytar Synthesizer White")
    get_amazon_results(sku)

    if len(searchResults) == 0:
        print("No results found")
        return

    cheapest = min(searchResults, key=lambda x: float(
        x.price.replace(",", "")))
    print("\n")
    print("=====================================")
    print("\n")
    print("Cheapest Result:")
    print(f"Source: {cheapest.source}")
    print(f"Name: {cheapest.name}")
    print(f"Price: {cheapest.price}")
    print(f"URL: {cheapest.url}")
    print("\n")
    print("=====================================")
    print("\n")

    print("Other Deals:")
    print("\n")
    for result in searchResults:
        print(f"Source: {result.source}")
        print(f"Name: {result.name}")
        print(f"Price: {result.price}")
        print(f"URL: {result.url}")
        print("\n")


if __name__ == "__main__":
    main()
