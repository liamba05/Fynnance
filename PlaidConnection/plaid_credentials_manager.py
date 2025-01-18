from google.cloud import secretmanager
import firebase_admin
from firebase_admin import credentials, firestore
from cryptography.fernet import Fernet
import hashlib
import base64
import os
from functools import lru_cache

class PlaidCredentialsManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PlaidCredentialsManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH'))
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
            encryption_key = self._get_secret('PLAID_FERNET_KEY')
            return Fernet(encryption_key.encode())
        except Exception as e:
            print(f"Error initializing encryption: {str(e)}")
            raise

    def _create_firebase_hash(self, value: str, salt: str) -> str:
        """Create a Firebase-compatible hash of the value."""
        key = hashlib.pbkdf2_hmac(
            'sha256',
            value.encode(),
            salt.encode(),
            100000
        )
        return base64.b64encode(key).decode()

    @lru_cache(maxsize=1)
    def get_plaid_credentials(self) -> tuple:
        """
        Retrieve and decrypt Plaid credentials from Firebase.
        Uses caching to avoid unnecessary decryption operations.
        """
        try:
            # Get encrypted credentials from Firebase
            creds_doc = self.db.collection('credentials').document('plaid').get()
            if not creds_doc.exists:
                raise ValueError("Plaid credentials not found in Firebase")
            
            creds_data = creds_doc.to_dict()
            firebase_hashed_client_id = creds_data.get('client_id')
            firebase_hashed_secret = creds_data.get('secret')
            
            if not firebase_hashed_client_id or not firebase_hashed_secret:
                raise ValueError("Missing required Plaid credentials")

            # Get Firebase salt from Secret Manager
            firebase_salt = self._get_secret('PLAID_FIREBASE_SALT')
            
            # First layer: Verify Firebase hash and get Fernet-encrypted values
            fernet_encrypted_client_id = firebase_hashed_client_id
            fernet_encrypted_secret = firebase_hashed_secret
            
            # Second layer: Decrypt with Fernet
            client_id = self.fernet.decrypt(fernet_encrypted_client_id.encode()).decode()
            secret = self.fernet.decrypt(fernet_encrypted_secret.encode()).decode()
            
            return client_id, secret
        except Exception as e:
            print(f"Error decrypting credentials: {str(e)}")
            raise

    def store_user_access_token(self, user_id: str, access_token: str, item_id: str = None) -> None:
        """
        Store a user's Plaid access token securely in Firebase.
        The access token is encrypted using the same double-encryption method.
        """
        try:
            # First layer: Fernet encryption
            encrypted_token = self.fernet.encrypt(access_token.encode()).decode()
            
            # Second layer: Firebase hash with salt
            firebase_salt = self._get_secret('PLAID_FIREBASE_SALT')
            final_token = self._create_firebase_hash(encrypted_token, firebase_salt)
            
            # Store in Firebase
            data = {
                'access_token': final_token,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            if item_id:
                data['item_id'] = item_id
                
            self.db.collection('users').document(user_id).set(data, merge=True)
            
        except Exception as e:
            print(f"Error storing access token: {str(e)}")
            raise

    def get_user_access_token(self, user_id: str) -> str:
        """
        Retrieve and decrypt a user's Plaid access token from Firebase.
        """
        try:
            user_doc = self.db.collection('users').document(user_id).get()
            if not user_doc.exists:
                return None
                
            user_data = user_doc.to_dict()
            firebase_hashed_token = user_data.get('access_token')
            
            if not firebase_hashed_token:
                return None
                
            # First layer: Get Fernet-encrypted value
            fernet_encrypted_token = firebase_hashed_token
            
            # Second layer: Decrypt with Fernet
            access_token = self.fernet.decrypt(fernet_encrypted_token.encode()).decode()
            
            return access_token
            
        except Exception as e:
            print(f"Error retrieving access token: {str(e)}")
            raise 