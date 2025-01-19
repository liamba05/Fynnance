from functions import (
    get_stock_price,
    get_top_gainers_and_losers,
    get_market_news_sentiment,
    get_fred_data,
    get_top_headlines,
    get_top_news_about,
)

# from MarketDataConnection.estate_data_service import (
#     get_market_stats,
# )
# HERE YOU CAN IMPORT ANY OTHER FUNCTIONS WE WANT GPT TO BE ABLE TO CALL
# JUST ADD THEM TO THE REGISTRY BELOW IN THE SAME FORMAT, AND THEN GPT
# WILL BE ABLE TO CALL THEM TO GATHER DATA FOR ITS RESPONSES


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
    "get_top_headlines": {
        "function": get_top_headlines,
        "description": "Fetch the top news headlines.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
    },
    "get_top_news_about": {
        "function": get_top_news_about,
        "description": "Fetch the top news headlines about a specific topic.",
        "parameters": {
            "type": "object",
            "properties": {
                "query_word": {"type": "string", "description": "The topic to search for in the news ('market' or 'trump' or anything like that for example)."},
            },
            "required": ["query_word"],
            "additionalProperties": False
        }
    },
}

