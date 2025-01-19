from functions import (
    get_stock_price,
    get_top_gainers_and_losers,
    get_market_news_sentiment,
    get_fred_data,
    get_top_headlines,
    get_top_news_about,
)
from UserDataCollection.user_data_collection import UserDataCollection
from PlaidConnection.plaid_data_service import (
    get_investment_holdings,
    get_account_balances,
    get_transactions,
    get_user_financial_profile,
    get_liabilities
)
from MarketDataConnection.estate_data_service import EstateDataService

# Initialize EstateDataService for its methods
estate_service = EstateDataService()

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
    "get_user_income": {
        "function": UserDataCollection().get_income,
        "description": "Get the user's annual income.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
    },
    "get_user_credit_score": {
        "function": UserDataCollection().get_credit_score,
        "description": "Get the user's credit score.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
    },
    "get_user_zip_code": {
        "function": UserDataCollection().get_zip_code,
        "description": "Get the user's ZIP code.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
    },
    "get_user_goals": {
        "function": UserDataCollection().get_goals,
        "description": "Get the user's financial goals and objectives.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
    },
    "get_user_preferences": {
        "function": UserDataCollection().get_preferences,
        "description": "Get the user's financial preferences and risk tolerance.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
    },
    "get_investment_holdings": {
        "function": get_investment_holdings,
        "description": "Get detailed investment holdings data including securities, values, and gain/loss information.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
    },
    "get_account_balances": {
        "function": get_account_balances,
        "description": "Get current balances for all linked bank accounts.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
    },
    "get_transactions": {
        "function": get_transactions,
        "description": "Get transaction history for a specified date range.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Start date in YYYY-MM-DD format. Defaults to 30 days ago if not provided."
                },
                "end_date": {
                    "type": "string",
                    "description": "End date in YYYY-MM-DD format. Defaults to today if not provided."
                }
            },
            "required": [],
            "additionalProperties": False
        }
    },
    "get_liabilities": {
        "function": get_liabilities,
        "description": "Get the user's liabilities, including credit cards, student loans, and mortgages.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
    },
    "get_user_financial_profile": {
        "function": get_user_financial_profile,
        "description": "Get a comprehensive financial profile including accounts, investments, transactions, and summary metrics.",
        "parameters": {
            "type": "object",
            "properties": {
                "transactions_days": {
                    "type": "integer",
                    "description": "Number of days of transaction history to include (default: 30)",
                    "default": 30
                }
            },
            "required": [],
            "additionalProperties": False
        }
    },
    "get_market_stats": {
        "function": estate_service.get_market_stats,
        "description": "Get detailed real estate market statistics for a ZIP code area, including prices, rents, and market insights.",
        "parameters": {
            "type": "object",
            "properties": {
                "property_type": {
                    "type": "string",
                    "description": "Type of property ('residential', 'multifamily', 'condo'). Defaults to residential.",
                    "enum": ["residential", "multifamily", "condo"]
                },
                "zip_code": {
                    "type": "string",
                    "description": "ZIP code to analyze. If not provided, uses user's ZIP code."
                }
            },
            "required": [],
            "additionalProperties": False
        }
    },
    "get_rental_listings": {
        "function": estate_service.get_rental_listings,
        "description": "Get available rental listings with market context and affordability analysis.",
        "parameters": {
            "type": "object",
            "properties": {
                "max_price": {
                    "type": "number",
                    "description": "Maximum monthly rent. If not provided, calculated from user's income."
                },
                "min_beds": {
                    "type": "integer",
                    "description": "Minimum number of bedrooms required.",
                    "default": 1
                },
                "zip_code": {
                    "type": "string",
                    "description": "ZIP code to search in. If not provided, uses user's ZIP code."
                }
            },
            "required": [],
            "additionalProperties": False
        }
    },
    "get_property_listings": {
        "function": estate_service.get_property_listings,
        "description": "Get available properties for sale with market context and affordability analysis.",
        "parameters": {
            "type": "object",
            "properties": {
                "max_price": {
                    "type": "number",
                    "description": "Maximum property price. If not provided, calculated from user's income."
                },
                "min_beds": {
                    "type": "integer",
                    "description": "Minimum number of bedrooms required.",
                    "default": 2
                },
                "zip_code": {
                    "type": "string",
                    "description": "ZIP code to search in. If not provided, uses user's ZIP code."
                }
            },
            "required": [],
            "additionalProperties": False
        }
    },
    "analyze_investment_potential": {
        "function": estate_service.analyze_investment_potential,
        "description": "Analyze the investment potential of a property with expected rental income.",
        "parameters": {
            "type": "object",
            "properties": {
                "property_price": {
                    "type": "number",
                    "description": "Purchase price of the property."
                },
                "expected_rent": {
                    "type": "number",
                    "description": "Expected monthly rental income."
                },
                "zip_code": {
                    "type": "string",
                    "description": "ZIP code of the property. If not provided, uses user's ZIP code."
                }
            },
            "required": ["property_price", "expected_rent"],
            "additionalProperties": False
        }
    },
    "get_affordability_analysis": {
        "function": estate_service.get_affordability_analysis,
        "description": "Get comprehensive affordability analysis based on user's income, credit score, and local market.",
        "parameters": {
            "type": "object",
            "properties": {
                "zip_code": {
                    "type": "string",
                    "description": "ZIP code to analyze. If not provided, uses user's ZIP code."
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
}

