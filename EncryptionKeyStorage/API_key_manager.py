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
            cred = credentials.Certificate('/Users/liambouayad/Documents/Documents/Sensitive_Data/fynnance-5031a-firebase-adminsdk-9mn1g-87d7537a7c.json')
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()
        self.secret_client = secretmanager.SecretManagerServiceClient()
        self.fernet = self._initialize_encryption()
        self._initialized = True
    
    def _get_secret(self, secret_name: str) -> str:
        """Retrieve a secret from Google Cloud Secret Manager."""
        try:
            name = f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/secrets/{secret_name}/versions/latest"
            response = self.secret_client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            print(f"Error retrieving secret {secret_name}: {str(e)}")
            raise
    
    def _initialize_encryption(self) -> Fernet:
        """Initialize Fernet encryption with key from Secret Manager."""
        try:
            encryption_key = self._get_secret('MARKET_DATA_FERNET_KEY')
            return Fernet(encryption_key.encode())
        except Exception as e:
            print(f"Error initializing encryption: {str(e)}")
            raise
    
    @lru_cache(maxsize=3)  # Cache the three API keys
    def get_api_key(self, service: Literal['alpha_vantage', 'rentcast', 'fred']) -> str:
        """
        Retrieve and decrypt an API key from Firebase.
        Uses caching to avoid unnecessary decryption operations.
        
        Args:
            service: The service to get the API key for ('alpha_vantage', 'rentcast', or 'fred')
            
        Returns:
            str: The decrypted API key
        """
        try:
            # Get encrypted credentials from Firebase
            creds_doc = self.db.collection('credentials').document('market_data').get()
            if not creds_doc.exists:
                raise ValueError("Market data credentials not found in Firebase")
            
            creds_data = creds_doc.to_dict()
            firebase_hashed_key = creds_data.get(service)
            
            if not firebase_hashed_key:
                raise ValueError(f"API key for {service} not found")
            
            # First layer: Get Fernet-encrypted value
            fernet_encrypted_key = firebase_hashed_key
            
            # Second layer: Decrypt with Fernet
            api_key = self.fernet.decrypt(fernet_encrypted_key.encode()).decode()
            
            return api_key
            
        except Exception as e:
            print(f"Error retrieving API key for {service}: {str(e)}")
            raise

if __name__ == "__main__":
    os.environ['GOOGLE_CLOUD_PROJECT'] = '258766016727'
    manager = APIKeyManager()
    
    # Quick test of all services
    for service in ['alpha_vantage', 'rentcast', 'fred']:
        try:
            key = manager.get_api_key(service)
            print(f"✅ {service}: {key[:4]}{'*' * (len(key) - 4)}")
        except Exception as e:
            print(f"❌ {service}: {str(e)}") 