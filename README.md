# SKU Price Fetcher

## Description
SKU Price Fetcher is a tool designed to fetch and display prices for various SKUs from different sources.

## Features
- Fetch prices from multiple sources (amazon, ebay, guitarcenter)
- Display prices in a user-friendly format

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/arthurliu987/sku_price_fetcher.git
    ```
2. Navigate to the project directory:
    ```bash
    cd sku_price_fetcher
    ```
3. Create a .env file in root directory with values for:
    ```
    CLIENT_ID = yourebayclientid
    CLIENT_SECRET = yourebayclientsecret

    GOOGLE_API_KEY = yourgoogleapikey
    GOOGLE_CUSTOM_SEARCH_ENGINE_KEY = yourgooglecustomsearchengineAPIkey
    ```
4. Create a virtual environment
   ```
   python -m venv venv_name
   ```
5. activate virtual environment 
   (windows)
   ```
   venv_name\Scripts\activate
   ```
      (MacOS/Linux)
   ```
    source venv_name/bin/activate
   ```
6. Install Dependences
    ```
    pip install -r requirements.txt
    ```


## Usage
1. Run the application by running 
    python main.py

2. Enter the SKU you want to fetch the price for.


