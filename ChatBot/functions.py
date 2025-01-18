# Functions that GPT can call for supplemental data.

import sys
import os
import requests
import datetime
from datetime import timedelta, datetime

# add to path so we can import other functions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import the API key manager
from EncryptionKeyStorage.API_key_manager import APIKeyManager
os.environ['GOOGLE_CLOUD_PROJECT'] = '258766016727'
api_key_manager = APIKeyManager()

# ------- FUNCTIONS THAT GPT CAN USE TO GATHER DATA ------

def get_stock_price(symbol: str):
    """
    Fetch the latest stock price for the given symbol using Alpha Vantage.

    Args:
        symbol (str): Stock ticker symbol (e.g., "IBM").

    Returns:
        dict: Parsed JSON data containing stock information or an error message.
    """
    api_key = api_key_manager.get_api_key('alpha_vantage')
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    print(url)
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()
        print(data)

        if "Global Quote" in data:
            print(data["Global Quote"])
            return data["Global Quote"]
        else:
            print('error')
            return {"error": "No data found for the given symbol."}
            
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def get_top_gainers_and_losers():
    """
    Fetch the top gainers, losers, and most actively traded for the current trading day using Alpha Vantage.

    Returns:
        dict: Parsed JSON data containing top gainers and losers or an error message.
    """
    api_key = api_key_manager.get_api_key('alpha_vantage')
    url = f'https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey=f{api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()

        if "metadata" in data:
            return data
        else:
            return {"error": "No data found for the given symbol."}
            
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    
def get_market_news_sentiment(tickers: str = None):
    """
    Fetch market news and sentiment data for given tickers.

    Args:
        tickers (str, optional): Comma-separated list of stock/crypto/forex symbols.

    Returns:
        dict: Parsed JSON data containing news and sentiment information or an error message.
    """
    api_key = api_key_manager.get_api_key('alpha_vantage')
    # get the time from for 3 days ago in exactly YYYYMMDDTHHMM format
    time_from = (datetime.datetime.now() - timedelta(days=3)).strftime("%Y%m%dT0000")
    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={tickers}&time_from={time_from}&apikey={api_key}'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()

        if "items" in data:
            return data
        else:
            return {"error": "No data found for the given symbol."}
    except requests.exceptions.RequestException as e:
       return {"error": str(e)}

def get_fred_data(series_id):
    """
    Fetch economic data from the FRED API.
    
    Parameters:
        series_id (str): The FRED series ID (e.g., 'GDP', 'UNRATE').
    
    Returns:
        dict: A dictionary containing the series data and metadata.
    """
    fred_key = api_key_manager.get_api_key('fred')
    base_url = "https://api.stlouisfed.org/fred/series/observations"
    end_date = datetime.today().strftime('%Y-%m-%d')
    # Set the start date (e.g., 5 years before the current date)
    start_date = (datetime.today() - timedelta(days=5*365)).strftime('%Y-%m-%d')
    params = {
        "series_id": series_id,
        "api_key": fred_key,
        "file_type": "json",
        "observation_start": start_date or "1776-07-04",
        "observation_end": end_date or "9999-12-31",
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Exception(f"Error fetching data from FRED API: {response.status_code} - {response.text}")
    

function_registry = {
    "get_stock_price": {
        "function": get_stock_price,
        "description": "Fetch the latest stock price, change, volume, etc for a given symbol.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Stock ticker symbol (e.g., 'IBM')."},
            },
            "required": ["symbol"],
            "additionalProperties": False,
        }
    },
    "get_top_gainers_and_losers": {
        "function": get_top_gainers_and_losers,
        "description": "Fetch the top gainers, losers, and most actively traded for the current trading day.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
    },
    "get_market_news_sentiment": {
        "function": get_market_news_sentiment,
        "description": "Fetch market news and sentiment data for given ticker/s for the last 3 days.",
        "parameters": {
            "type": "object",
            "properties": {
                "tickers": {"type": "string", "description": "Comma-separated list of stock/crypto/forex symbols. Stock symbols in format SYMBOL, but crypto or forex must CRYPTO:XXX or FOREX:XXX"},
            },
            "required": ["tickers"],
            "additionalProperties": False
        }
    },
    "get_fred_data": {
        "function": get_fred_data,
        "description": "Fetch various economic data from the FRED API.",
        "parameters": {
            "type": "object",
            "properties": {
                "series_id": {"type": "string", "description": "The FRED series ID (e.g., 'GDP', 'UNRATE', 'FEDFUNDS', etc)."},
            },
            "required": ["series_id"],
            "additionalProperties": False
        }
    },
}

