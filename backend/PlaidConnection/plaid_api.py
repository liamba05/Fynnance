"""
Flask API for Plaid integration.
Handles authentication, link token creation, and public token exchange.
All data retrieval is handled by the plaid_data_service module.
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import plaid
from plaid.api import plaid_api
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid_credentials_manager import PlaidCredentialsManager
from firebase_admin import auth, initialize_app
import firebase_admin
import os
from functools import wraps
from plaid_data_service import get_user_financial_profile


app = Flask(__name__)
app.secret_key = os.urandom(24)  # More secure secret key

# Configure CORS for your frontend domain
CORS(app, 
     origins=['http://localhost:8000'],
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'OPTIONS'],
     expose_headers=['Content-Type'],
     max_age=600)  # Cache preflight requests for 10 minutes

# Configure session and security headers
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

# Handle OPTIONS requests explicitly
@app.route('/api/create_link_token', methods=['OPTIONS'])
@app.route('/api/exchange_public_token', methods=['OPTIONS'])
def handle_options():
    response = app.make_default_options_response()
    return response

# Constants
PLAID_ENV = 'https://sandbox.plaid.com'
PLAID_REDIRECT_URI = 'https://localhost:8000'  # Custom domain
FIREBASE_PROJECT_ID = 'fynnance-5031a'

# Initialize Firebase
if not firebase_admin._apps:
    try:
        initialize_app()
        app.logger.info("Firebase initialized successfully")
    except Exception as e:
        app.logger.error(f"Error initializing Firebase: {str(e)}")
        raise

# Initialize the credentials manager (Singleton)
credentials_manager = PlaidCredentialsManager()

def create_plaid_client():
    """Create a Plaid client using the securely stored credentials."""
    try:
        client_id, secret = credentials_manager.get_plaid_credentials()
        
        if not client_id or not secret:
            app.logger.error("Missing Plaid credentials")
            raise ValueError("Plaid credentials not found")
            
        app.logger.info(f"Creating Plaid client with environment: {PLAID_ENV}")
        
        # Create configuration using the imported Configuration class
        configuration = Configuration(
            host=PLAID_ENV,
            api_key={
                'clientId': client_id,
                'secret': secret
            }
        )

        # Create API client using the imported ApiClient class
        api_client = ApiClient(configuration)
        
        # Create and return PlaidApi instance
        client = plaid_api.PlaidApi(api_client)
        
        # Test the client with a simple API call
        try:
            request = {
                'count': 1,
                'offset': 0,
                'country_codes': ['US']  # Add required country_codes parameter
            }
            response = client.institutions_get(request)
            app.logger.info("Plaid client created and verified successfully")
            return client
            
        except Exception as e:
            app.logger.error(f"Failed to verify Plaid client: {str(e)}")
            if hasattr(e, 'body'):
                app.logger.error(f"Plaid API error details: {e.body}")
            raise ValueError(f"Failed to verify Plaid client: {str(e)}")
        
    except Exception as e:
        app.logger.error(f"Error creating Plaid client: {str(e)}")
        raise

def require_auth(f):
    """Decorator to require Firebase authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No authentication token provided'}), 401

        id_token = auth_header.split('Bearer ')[1]
        try:
            # Verify the Firebase ID token
            decoded_token = auth.verify_id_token(id_token)
            # Store user ID in session
            session['user_id'] = decoded_token['uid']
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Invalid authentication token'}), 401

    return decorated_function

@app.route('/api/create_link_token', methods=['POST'])
@require_auth
def create_link_token():
    """Create a Plaid Link token for initializing Plaid Link in the frontend."""
    try:
        user_id = session.get('user_id')
        if not user_id:
            app.logger.error("User ID not found in session")
            return jsonify({'error': 'User not authenticated'}), 401

        app.logger.info(f"Creating link token for user: {user_id}")
        plaid_client = create_plaid_client()
        
        # Create the Link token request with account filters
        request_data = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(
                client_user_id=user_id
            ),
            client_name="Fynn",
            products=[Products("auth"), Products("transactions"), Products("liabilities")],
            country_codes=[CountryCode('US')],
            language='en',
            redirect_uri=PLAID_REDIRECT_URI
        )
        
        app.logger.info("Sending link token create request to Plaid")
        try:
            response = plaid_client.link_token_create(request_data)
            app.logger.info("Successfully created link token")
            
            if not response or not response.get('link_token'):
                app.logger.error("No link token in response")
                return jsonify({'error': 'Failed to create link token - no token in response'}), 500
                
            return jsonify({
                'link_token': response['link_token'],
                'expiration': response.get('expiration')
            })
            
        except Exception as plaid_error:
            app.logger.error(f"Plaid API error: {str(plaid_error)}")
            return jsonify({
                'error': 'Failed to create link token',
                'details': str(plaid_error)
            }), 500
        
    except Exception as e:
        app.logger.error(f"Server error creating link token: {str(e)}")
        return jsonify({
            'error': 'Failed to create link token',
            'details': str(e)
        }), 500

@app.route('/api/exchange_public_token', methods=['POST'])
@require_auth
def exchange_public_token():
    """Exchange a public token from Plaid Link for an access token."""
    try:
        data = request.get_json()
        public_token = data.get('public_token')
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        if not public_token:
            return jsonify({'error': 'Public token is required'}), 400
            
        plaid_client = create_plaid_client()
        
        try:
            # Exchange the public token for an access token
            exchange_request = ItemPublicTokenExchangeRequest(
                public_token=public_token
            )
            exchange_response = plaid_client.item_public_token_exchange(exchange_request)
            
            # Get the access token and item ID
            access_token = exchange_response['access_token']
            item_id = exchange_response['item_id']
            
            # Store the access token securely
            credentials_manager.store_user_access_token(user_id, access_token, item_id)
            
            # Get initial account data
            try:
                accounts_response = plaid_client.accounts_get({
                    'access_token': access_token
                })
                
                return jsonify({
                    'success': True,
                    'item_id': item_id,
                    'accounts': accounts_response['accounts'],
                    'numbers_available': 'auth' in exchange_response.get('consent', {}).get('scopes', [])
                })
            except Exception as acc_error:
                app.logger.error(f"Error fetching initial account data: {str(acc_error)}")
                # Still return success even if getting accounts fails
                return jsonify({
                    'success': True,
                    'item_id': item_id,
                    'warning': 'Connected successfully but failed to fetch initial account data'
                })
                
        except Exception as plaid_error:
            app.logger.error(f"Plaid API error: {str(plaid_error)}")
            return jsonify({
                'error': 'Failed to exchange public token',
                'details': str(plaid_error)
            }), 500
            
    except Exception as e:
        app.logger.error(f"Server error in token exchange: {str(e)}")
        return jsonify({
            'error': 'Internal server error during token exchange',
            'details': str(e)
        }), 500

@app.route('/api/financial_profile', methods=['GET'])
@require_auth
def get_financial_profile():
    """
    Get a comprehensive financial profile for the authenticated user.
    Query Parameters:
        transactions_days (optional): Number of days of transaction history to include (default: 30)
    """
    try:
        # Get transactions_days from query parameters, default to 30
        transactions_days = request.args.get('transactions_days', default=30, type=int)
        
        # Get the profile using the data service
        profile = get_user_financial_profile(transactions_days=transactions_days)
        
        return jsonify(profile)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 