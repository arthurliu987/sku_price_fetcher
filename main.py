import requests

# Amazon Product Advertising API Configuration
AMAZON_ACCESS_KEY = "your_amazon_access_key"
AMAZON_SECRET_KEY = "your_amazon_secret_key"
AMAZON_ASSOCIATE_TAG = "your_associate_tag"
AMAZON_REGION = "us-east-1"
AMAZON_ENDPOINT = "https://webservices.amazon.com/paapi5/getitems"

# eBay Browse API Configuration
EBAY_APP_ID = "your_ebay_app_id"
EBAY_ENDPOINT = "https://api.ebay.com/buy/browse/v1/item_summary/search"

def get_amazon_price(sku):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "ItemIds": [sku],
        "PartnerTag": AMAZON_ASSOCIATE_TAG,
        "PartnerType": "Associates",
        "Marketplace": "www.amazon.com",
    }
    
    response = requests.post(
        AMAZON_ENDPOINT,
        headers=headers,
        auth=(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY),
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        try:
            price = data["ItemsResult"]["Items"][0]["Offers"]["Listings"][0]["Price"]["DisplayAmount"]
            return price
        except (IndexError, KeyError):
            return "Price not available"
    else:
        return f"Error: {response.status_code} {response.text}"

def get_ebay_price(sku):
    headers = {
        "Authorization": f"Bearer {EBAY_APP_ID}",
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

def main():
    sku = input("Enter the SKU: ")
    print("Fetching prices...")
    
    amazon_price = get_amazon_price(sku)
    ebay_price = get_ebay_price(sku)
    
    print(f"Amazon Price: {amazon_price}")
    print(f"eBay Price: {ebay_price}")

if __name__ == "__main__":
    main()