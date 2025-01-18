from google.cloud import secretmanager
import firebase_admin
from firebase_admin import credentials, firestore
from cryptography.fernet import Fernet
import hashlib
import base64
import os
from EncryptionKeyStorage.API_key_manager import APIKeyManager

def store_market_api_keys(project_id: str, alpha_vantage_key: str, rentcast_key: str, fred_key: str):
    """Store market data API keys in Google Cloud Secret Manager and Firebase."""
    try:
        # Initialize Firebase
        cred = credentials.Certificate(APIKeyManager.get_firebase_path())
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        # Initialize Firestore
        db = firestore.client()
        
        # Create Secret Manager client
        client = secretmanager.SecretManagerServiceClient(
            credentials=cred.get_credential()
        )
        
        # Generate new Fernet key
        fernet_key = Fernet.generate_key()
        fernet = Fernet(fernet_key)
        
        # Generate salt for Firebase hashing
        firebase_salt = base64.b64encode(os.urandom(16)).decode()
        
        # Store Fernet key in Secret Manager
        parent = f"projects/{project_id}"
        fernet_secret = client.create_secret(
            request={
                "parent": parent,
                "secret_id": "MARKET_DATA_FERNET_KEY",
                "secret": {"replication": {"automatic": {}}},
            }
        )
        
        client.add_secret_version(
            request={
                "parent": fernet_secret.name,
                "payload": {"data": fernet_key},
            }
        )
        
        # Store Firebase salt in Secret Manager
        salt_secret = client.create_secret(
            request={
                "parent": parent,
                "secret_id": "MARKET_DATA_FIREBASE_SALT",
                "secret": {"replication": {"automatic": {}}},
            }
        )
        
        client.add_secret_version(
            request={
                "parent": salt_secret.name,
                "payload": {"data": firebase_salt.encode()},
            }
        )
        
        # Function to create Firebase-compatible hash
        def create_firebase_hash(value: str) -> str:
            key = hashlib.pbkdf2_hmac(
                'sha256',
                value.encode(),
                firebase_salt.encode(),
                100000
            )
            return base64.b64encode(key).decode()
        
        # Encrypt and store each API key
        api_keys = {
            'alpha_vantage': alpha_vantage_key,
            'rentcast': rentcast_key,
            'fred': fred_key
        }
        
        encrypted_keys = {}
        for key_name, api_key in api_keys.items():
            # First layer: Fernet encryption
            fernet_encrypted = fernet.encrypt(api_key.encode()).decode()
            # Second layer: Firebase hash
            firebase_hashed = create_firebase_hash(fernet_encrypted)
            encrypted_keys[key_name] = firebase_hashed
        
        # Store in Firebase
        db.collection('credentials').document('market_data').set(
            encrypted_keys,
            merge=True
        )
        
        print("Successfully stored market data API keys!")
        
    except Exception as e:
        print(f"Error storing market data API keys: {str(e)}")
        raise

if __name__ == "__main__":
    # You'll need to run this script with your actual API keys
    store_market_api_keys(
        project_id="a",  # Your GCP project ID
        alpha_vantage_key="a",
        rentcast_key="a",
        fred_key="a"
    ) 