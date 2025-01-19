from flask import Flask, request, jsonify, session, Response
from flask_cors import CORS
from firebase_admin import auth
from functools import wraps
from user_data_collection import UserDataCollection
import os
import plaid
from plaid.api import plaid_api
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from PlaidConnection.plaid_credentials_manager import PlaidCredentialsManager
from PlaidConnection.plaid_data_service import get_user_financial_profile
import openai
from EncryptionKeyStorage.API_key_manager import APIKeyManager

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure CORS
CORS(app, 
     origins=['http://localhost:5173'],
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'OPTIONS'],
     expose_headers=['Content-Type'],
     max_age=600)

# Configure session and security headers
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

# Constants for Plaid
PLAID_ENV = 'https://sandbox.plaid.com'
PLAID_REDIRECT_URI = 'https://localhost:5173'
FIREBASE_PROJECT_ID = 'fynnance-5031a'

# Initialize Plaid credentials manager
credentials_manager = PlaidCredentialsManager()

# Initialize OpenAI with our API key
openai.api_key = APIKeyManager.get_api_key('openai')

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
            session['firebase_user_id'] = decoded_token['uid']
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Invalid authentication token'}), 401

    return decorated_function

# Required field getters
@app.route('/api/user/first_name', methods=['GET'])
@require_auth
def get_first_name():
    try:
        user_data = UserDataCollection()
        return jsonify({'first_name': user_data.get_first_name()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/last_name', methods=['GET'])
@require_auth
def get_last_name():
    try:
        user_data = UserDataCollection()
        return jsonify({'last_name': user_data.get_last_name()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/email', methods=['GET'])
@require_auth
def get_email():
    try:
        user_data = UserDataCollection()
        return jsonify({'email': user_data.get_email()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/date_of_birth', methods=['GET'])
@require_auth
def get_date_of_birth():
    try:
        user_data = UserDataCollection()
        dob = user_data.get_date_of_birth()
        return jsonify({'date_of_birth': dob.isoformat() if dob else None})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Optional field getters
@app.route('/api/user/income', methods=['GET'])
@require_auth
def get_income():
    try:
        user_data = UserDataCollection()
        return jsonify({'income': user_data.get_income()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/zip_code', methods=['GET'])
@require_auth
def get_zip_code():
    try:
        user_data = UserDataCollection()
        return jsonify({'zip_code': user_data.get_zip_code()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/credit_score', methods=['GET'])
@require_auth
def get_credit_score():
    try:
        user_data = UserDataCollection()
        return jsonify({'credit_score': user_data.get_credit_score()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Optional field setters
@app.route('/api/user/income', methods=['POST'])
@require_auth
def set_income():
    try:
        data = request.get_json()
        if 'income' not in data:
            return jsonify({'error': 'Income value is required'}), 400
            
        income = float(data['income'])
        user_data = UserDataCollection()
        user_data.set_income(income)
        return jsonify({'message': 'Income updated successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/zip_code', methods=['POST'])
@require_auth
def set_zip_code():
    try:
        data = request.get_json()
        if 'zip_code' not in data:
            return jsonify({'error': 'ZIP code is required'}), 400
            
        zip_code = str(data['zip_code'])
        user_data = UserDataCollection()
        user_data.set_zip_code(zip_code)
        return jsonify({'message': 'ZIP code updated successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/credit_score', methods=['POST'])
@require_auth
def set_credit_score():
    try:
        data = request.get_json()
        if 'credit_score' not in data:
            return jsonify({'error': 'Credit score is required'}), 400
            
        credit_score = int(data['credit_score'])
        user_data = UserDataCollection()
        user_data.set_credit_score(credit_score)
        return jsonify({'message': 'Credit score updated successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/first_name', methods=['POST'])
@require_auth
def set_first_name():
    try:
        data = request.get_json()
        if 'first_name' not in data:
            return jsonify({'error': 'First name is required'}), 400
            
        first_name = str(data['first_name'])
        user_data = UserDataCollection()
        user_data.set_first_name(first_name)
        return jsonify({'message': 'First name updated successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/last_name', methods=['POST'])
@require_auth
def set_last_name():
    try:
        data = request.get_json()
        if 'last_name' not in data:
            return jsonify({'error': 'Last name is required'}), 400
            
        last_name = str(data['last_name'])
        user_data = UserDataCollection()
        user_data.set_last_name(last_name)
        return jsonify({'message': 'Last name updated successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/email', methods=['POST'])
@require_auth
def set_email():
    try:
        data = request.get_json()
        if 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400
            
        email = str(data['email'])
        user_data = UserDataCollection()
        user_data.set_email(email)
        return jsonify({'message': 'Email updated successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/date_of_birth', methods=['POST'])
@require_auth
def set_date_of_birth():
    try:
        data = request.get_json()
        if 'date_of_birth' not in data:
            return jsonify({'error': 'Date of birth is required'}), 400
            
        from datetime import datetime
        try:
            dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
            
        user_data = UserDataCollection()
        user_data.set_date_of_birth(dob)
        return jsonify({'message': 'Date of birth updated successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/assets', methods=['GET'])
@require_auth
def get_assets():
    try:
        user_data = UserDataCollection()
        return jsonify({'assets': user_data.get_assets()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/assets', methods=['POST'])
@require_auth
def set_assets():
    try:
        data = request.get_json()
        if 'assets' not in data:
            return jsonify({'error': 'Assets value is required'}), 400
            
        assets = float(data['assets'])
        user_data = UserDataCollection()
        user_data.set_assets(assets)
        return jsonify({'message': 'Assets updated successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# GPT Data endpoints
@app.route('/api/user/goals', methods=['GET'])
@require_auth
def get_goals():
    try:
        user_data = UserDataCollection()
        return jsonify({'goals': user_data.get_goals()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/goals', methods=['POST'])
@require_auth
def set_goals():
    try:
        data = request.get_json()
        if 'goals' not in data:
            return jsonify({'error': 'Goals are required'}), 400
            
        goals = str(data['goals'])
        user_data = UserDataCollection()
        user_data.set_goals(goals)
        return jsonify({'message': 'Goals updated successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/preferences', methods=['GET'])
@require_auth
def get_preferences():
    try:
        user_data = UserDataCollection()
        return jsonify({'preferences': user_data.get_preferences()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/preferences', methods=['POST'])
@require_auth
def set_preferences():
    try:
        data = request.get_json()
        if 'preferences' not in data:
            return jsonify({'error': 'Preferences are required'}), 400
            
        preferences = str(data['preferences'])
        user_data = UserDataCollection()
        user_data.set_preferences(preferences)
        return jsonify({'message': 'Preferences updated successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add Plaid routes
@app.route('/api/create_link_token', methods=['POST'])
@require_auth
def create_link_token():
    try:
        user_id = session.get('firebase_user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401

        plaid_client = credentials_manager.create_plaid_client()
        
        request_data = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(
                client_user_id=user_id
            ),
            client_name="Fynn",
            products=[Products("auth"), Products("transactions"), Products("liabilities"), Products("investments")],
            country_codes=[CountryCode('US')],
            language='en',
            redirect_uri=PLAID_REDIRECT_URI
        )
        
        response = plaid_client.link_token_create(request_data)
        
        if not response or not response.get('link_token'):
            return jsonify({'error': 'Failed to create link token'}), 500
            
        return jsonify({
            'link_token': response['link_token'],
            'expiration': response.get('expiration')
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to create link token',
            'details': str(e)
        }), 500

@app.route('/api/exchange_public_token', methods=['POST'])
@require_auth
def exchange_public_token():
    try:
        data = request.get_json()
        public_token = data.get('public_token')
        user_id = session.get('firebase_user_id')
        
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        if not public_token:
            return jsonify({'error': 'Public token is required'}), 400
            
        plaid_client = credentials_manager.create_plaid_client()
        
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        exchange_response = plaid_client.item_public_token_exchange(exchange_request)
        
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']
        
        credentials_manager.store_user_access_token(user_id, access_token, item_id)
        
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
        except Exception:
            return jsonify({
                'success': True,
                'item_id': item_id,
                'warning': 'Connected successfully but failed to fetch initial account data'
            })
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error during token exchange',
            'details': str(e)
        }), 500

@app.route('/api/financial_profile', methods=['GET'])
@require_auth
def get_financial_profile():
    try:
        transactions_days = request.args.get('transactions_days', default=30, type=int)
        profile = get_user_financial_profile(transactions_days=transactions_days)
        return jsonify(profile)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stream_gpt_response', methods=['POST'])
@require_auth
def stream_gpt_response():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')

        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        def generate():
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    stream=True
                )

                for chunk in response:
                    if chunk and hasattr(chunk.choices[0].delta, 'content'):
                        content = chunk.choices[0].delta.content
                        if content:
                            yield f"data: {content}\n\n"

            except Exception as e:
                yield f"data: Error: {str(e)}\n\n"

        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )

    except Exception as e:
        return jsonify({
            'error': 'Failed to process GPT request',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
