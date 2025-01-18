"""
Flask API for Plaid integration.
Handles authentication, link token creation, and public token exchange.
All data retrieval is handled by the plaid_data_service module.
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from plaid.api import plaid_api
from plaid import ApiClient, Configuration
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid_credentials_manager import PlaidCredentialsManager
from firebase_admin import auth
import firebase_admin
from firebase_functions import https_fn, options
import os
from functools import wraps
from plaid_data_service import get_user_financial_profile

# Initialize Firebase with configuration
firebase_options = options.FirebaseOptions(
    project_id='fynnance-5031a',
    region='us-central1'
)

app = Flask(__name__)
app.secret_key = firebase_options.project_id  # Use project ID as fallback
CORS(app, supports_credentials=True)

# Constants
PLAID_ENV = 'https://sandbox.plaid.com'
PLAID_REDIRECT_URI = 'https://fynnance.com/callback'  # Custom domain

# Initialize Firebase and the credentials manager (Singleton)
if not firebase_admin._apps:
    firebase_admin.initialize_app()
credentials_manager = PlaidCredentialsManager()

def create_plaid_client():
    """Create a Plaid client using the securely stored credentials."""
    client_id, secret = credentials_manager.get_plaid_credentials()
    configuration = Configuration(
        host=os.getenv('PLAID_ENV', PLAID_ENV),
        api_key={
            'clientId': client_id,
            'secret': secret
        }
    )
    return plaid_api.PlaidApi(ApiClient(configuration))

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
        user_id = session['user_id']
        plaid_client = create_plaid_client()
        
        # Create the Link token request
        request_data = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=user_id),
            client_name="Fynn",
            products=[
                Products("auth"),
                Products("transactions")
            ],
            country_codes=[CountryCode('US')],
            language='en',
            redirect_uri=PLAID_REDIRECT_URI
        )
        
        # Create the Link token
        response = plaid_client.link_token_create(request_data)
        return jsonify({'link_token': response['link_token']})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/exchange_public_token', methods=['POST'])
@require_auth
def exchange_public_token():
    """Exchange a public token from Plaid Link for an access token."""
    try:
        data = request.get_json()
        public_token = data.get('public_token')
        user_id = session['user_id']
        
        if not public_token:
            return jsonify({'error': 'public_token is required'}), 400
            
        plaid_client = create_plaid_client()
        
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
        
        # Only return item_id to frontend, never the access token
        return jsonify({'success': True, 'item_id': item_id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

# Firebase Function handler
@https_fn.on_request(
    region=firebase_options.region,
    memory=options.MemoryOption.GB_1,  # Adjust based on your needs
    timeout_sec=540  # 9 minutes timeout
)
def api(request: https_fn.Request) -> https_fn.Response:
    """Handle all Flask routes as a Firebase Function."""
    with app.request_context(request.environ):
        return app.full_dispatch_request()

if __name__ == '__main__':
    app.run(debug=True) 