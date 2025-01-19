from google.cloud import secretmanager
import firebase_admin
from firebase_admin import credentials, firestore
from cryptography.fernet import Fernet
import os
from functools import lru_cache
from typing import Literal

class APIKeyManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APIKeyManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(APIKeyManager.get_firebase_path())
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()
        self.secret_client = secretmanager.SecretManagerServiceClient(
            credentials=credentials.Certificate(APIKeyManager.get_firebase_path()).get_credential()
        )
        self.fernet = self._initialize_encryption()
        self._initialized = True
    
    def _get_secret(self, secret_name: str) -> str:
        """Retrieve a secret from Google Cloud Secret Manager."""
        try:
            name = f"projects/258766016727/secrets/{secret_name}/versions/latest"
            response = self.secret_client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            print(f"Error retrieving secret {secret_name}: {str(e)}")
            raise
    
    def _initialize_encryption(self) -> Fernet:
        """Initialize Fernet encryption with key from Secret Manager."""
        try:
            encryption_key = self._get_secret('ENCRYPTION_FERNET_KEY')
            return Fernet(encryption_key.encode())
        except Exception as e:
            print(f"Error initializing encryption: {str(e)}")
            raise
    
    @lru_cache(maxsize=5)  # Cache all API keys including Plaid credentials
    def get_api_key(self, service: Literal['alpha_vantage', 'rentcast', 'fred', 'p_clientid', 'p_secret', 'openai']) -> str:
        """
        Retrieve and decrypt an API key from Firebase.
        Uses caching to avoid unnecessary decryption operations.
        
        Args:
            service: The service to get the API key for ('alpha_vantage', 'rentcast', 'fred', 'p_clientid', 'p_secret', 'openai')
            
        Returns:
            str: The decrypted API key
        """
        try:
            # Map service names to Firebase field names
            firebase_field_map = {
                'alpha_vantage': 'ALPHA_VANTAGE_KEY',
                'rentcast': 'RENTCAST_KEY',
                'fred': 'FRED_KEY',
                'p_clientid': 'PLAID_CLIENT_ID',
                'p_secret': 'PLAID_SECRET',
                'openai': 'OPENAI_KEY'
            }
            
            # Get encrypted credentials from Firebase
            creds_doc = self.db.collection('credentials').document('api_keys').get()
            if not creds_doc.exists:
                raise ValueError("API credentials not found in Firebase")
            
            creds_data = creds_doc.to_dict()
            firebase_field = firebase_field_map.get(service)
            
            if not firebase_field:
                raise ValueError(f"Invalid service: {service}")
                
            firebase_hashed_key = creds_data.get(firebase_field)
            
            if not firebase_hashed_key:
                raise ValueError(f"API key for {service} not found")
            
            # Decrypt with Fernet
            api_key = self.fernet.decrypt(firebase_hashed_key.encode()).decode()
            
            return api_key
            
        except Exception as e:
            print(f"Error retrieving API key for {service}: {str(e)}")
            raise

    def store_api_key(self, service: str, api_key: str) -> None:
        """
        Store and encrypt an API key in Firebase.
        
        Args:
            service: The service name for the API key
            api_key: The API key to encrypt and store
            
        Returns:
            None
        """
        try:
            # Map service names to Firebase field names
            firebase_field_map = {
                'alpha_vantage': 'ALPHA_VANTAGE_KEY',
                'rentcast': 'RENTCAST_KEY',
                'fred': 'FRED_KEY',
                'p_clientid': 'PLAID_CLIENT_ID',
                'p_secret': 'PLAID_SECRET',
                'openai': 'OPENAI_KEY'
            }
            
            firebase_field = firebase_field_map.get(service)
            if not firebase_field:
                raise ValueError(f"Invalid service: {service}")
            
            # Encrypt the API key
            encrypted_key = self.fernet.encrypt(api_key.encode()).decode()
            
            # Store in Firebase
            creds_ref = self.db.collection('credentials').document('api_keys')
            creds_ref.set({
                firebase_field: encrypted_key
            }, merge=True)
            
            # Clear the cache for this service
            self.get_api_key.cache_clear()
            
        except Exception as e:
            print(f"Error storing API key for {service}: {str(e)}")
            raise

    @staticmethod
    def get_firebase_path():
        return '/Users/liambouayad/Documents/Documents/Sensitive_Data/fynnance-5031a-firebase-adminsdk-9mn1g-87d7537a7c.json'

if __name__ == "__main__":
    os.environ['GOOGLE_CLOUD_PROJECT'] = '258766016727'
    manager = APIKeyManager()
    
    print(manager.get_api_key('openai'))