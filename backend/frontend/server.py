from flask import Flask, send_from_directory, jsonify, request
import plaid
import os
import sys
import signal
import threading
from werkzeug.serving import make_server

# Add the root directory to Python path to import APIKeyManager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from EncryptionKeyStorage.API_key_manager import APIKeyManager

class ServerThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.server = make_server('127.0.0.1', 8000, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

def create_app():
    # Get the directory containing this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    app = Flask(__name__, static_url_path='', static_folder=current_dir)
    
    # Configure CORS properly
    app.config['CORS_HEADERS'] = 'Content-Type'
    
    # Initialize API Key Manager
    key_manager = APIKeyManager()

    try:
        # Configure Plaid client
        from plaid.api.plaid_api import PlaidApi
        from plaid.api_client import ApiClient
        from plaid.configuration import Configuration

        configuration = Configuration(
            host='https://sandbox.plaid.com',
            api_key={
                'clientId': key_manager.get_api_key('p_clientid'),
                'secret': key_manager.get_api_key('p_secret')
            }
        )
        api_client = ApiClient(configuration)
        plaid_client = PlaidApi(api_client)
        print("Plaid client initialized successfully")
    except Exception as e:
        print(f"Error initializing Plaid client: {str(e)}")
        raise

    # Store server instance
    app.server_thread = None

    # Serve static files
    @app.route('/')
    def serve_index():
        return send_from_directory(current_dir, 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        return send_from_directory(current_dir, path)

    # Enable CORS
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin in ['http://localhost:8000', 'http://localhost:5001']:
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    # Handle OPTIONS requests
    @app.route('/', methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def handle_options(path=None):
        response = app.make_default_options_response()
        origin = request.headers.get('Origin')
        if origin in ['http://localhost:8000', 'http://localhost:5001']:
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    # Plaid endpoints
    @app.route('/create_link_token', methods=['POST'])
    def create_link_token():
        try:
            from plaid.model.link_token_create_request import LinkTokenCreateRequest
            from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
            from plaid.model.products import Products
            from plaid.model.country_code import CountryCode

            # Create the link token request
            request = LinkTokenCreateRequest(
                products=[Products("auth"), Products("transactions")],
                client_name="Fynn Test App",
                country_codes=[CountryCode("US")],
                language="en",
                user=LinkTokenCreateRequestUser(
                    client_user_id="test-user"
                ),
                redirect_uri="http://localhost:8000"  # Hardcoded for testing
            )
            
            response = plaid_client.link_token_create(request)
            print("Link token created successfully")
            return jsonify(response.to_dict())
        except Exception as e:
            print(f"Error creating link token: {str(e)}")
            return jsonify({"error": str(e)}), 400

    @app.route('/exchange_public_token', methods=['POST'])
    def exchange_public_token():
        try:
            from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
            
            public_token = request.json['public_token']
            request_data = ItemPublicTokenExchangeRequest(
                public_token=public_token
            )
            
            exchange_response = plaid_client.item_public_token_exchange(request_data)
            # In a real application, you would save these tokens securely
            access_token = exchange_response['access_token']
            item_id = exchange_response['item_id']
            print("Public token exchanged successfully")
            return jsonify({"status": "success"})
        except Exception as e:
            print(f"Error exchanging public token: {str(e)}")
            return jsonify({"error": str(e)}), 400

    @app.route('/cleanup', methods=['POST'])
    def cleanup():
        """Handle cleanup when client disconnects"""
        if app.server_thread:
            # Schedule the shutdown after responding to the client
            threading.Thread(target=app.server_thread.shutdown).start()
        return jsonify({"status": "cleanup_initiated"})

    return app

def signal_handler(signum, frame):
    """Handle shutdown on CTRL+C"""
    print("\nShutting down server...")
    if app.server_thread:
        app.server_thread.shutdown()
    sys.exit(0)

if __name__ == '__main__':
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and configure the app
    app = create_app()
    
    # Start server in a separate thread
    port = 8000
    print(f"Starting server on port {port}...")
    print(f"Open http://localhost:{port} in your browser")
    print("Server will automatically shut down when you close the browser tab")
    print("Press CTRL+C to stop the server manually")
    
    server_thread = ServerThread(app)
    app.server_thread = server_thread
    server_thread.start()
    
    # Keep the main thread alive
    try:
        while True:
            signal.pause()
    except (KeyboardInterrupt, SystemExit):
        print("\nShutting down server...") 