from google.cloud import secretmanager
import firebase_admin
from firebase_admin import credentials, firestore
from cryptography.fernet import Fernet
import os

def store_encryption_key(project_id: str):
    """Store a single Fernet encryption key in GCP Secret Manager."""
    try:
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate('/Users/liambouayad/Documents/Documents/Sensitive_Data/fynnance-5031a-firebase-adminsdk-9mn1g-87d7537a7c.json')
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        client = secretmanager.SecretManagerServiceClient()
        
        # Generate a new Fernet key
        fernet_key = Fernet.generate_key()
        
        # Store the Fernet key in Secret Manager
        secret_id = "ENCRYPTION_FERNET_KEY"
        parent = f"projects/{project_id}"
        
        try:
            # Create the secret if it doesn't exist
            secret = client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_id,
                    "secret": {"replication": {"automatic": {}}},
                }
            )
        except Exception as e:
            # If the secret already exists, proceed to add a new version
            secret = client.secret_path(project_id, secret_id)
        
        # Add the key as a secret version
        client.add_secret_version(
            request={
                "parent": secret,
                "payload": {"data": fernet_key},
            }
        )
        
        print("Successfully stored the Fernet encryption key in Secret Manager.")
        print(f"Fernet Key Name: {secret}")
        
        return fernet_key.decode()
        
    except Exception as e:
        print(f"Error storing encryption key: {str(e)}")
        raise

def get_encryption_key(project_id: str) -> Fernet:
    """Retrieve the Fernet encryption key from GCP Secret Manager."""
    try:
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate('/Users/liambouayad/Documents/Documents/Sensitive_Data/fynnance-5031a-firebase-adminsdk-9mn1g-87d7537a7c.json')
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        # Create the Secret Manager client with the same credentials
        client = secretmanager.SecretManagerServiceClient(
            credentials=cred.get_credential()
        )
        
        secret_id = "ENCRYPTION_FERNET_KEY"
        secret_path = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        
        response = client.access_secret_version(request={"name": secret_path})
        fernet_key = response.payload.data.decode()
        
        # Initialize Fernet with the retrieved key
        fernet = Fernet(fernet_key.encode())
        
        print("Successfully retrieved the Fernet encryption key from Secret Manager.")
        
        return fernet
        
    except Exception as e:
        print(f"Error retrieving encryption key: {str(e)}")
        raise

def store_encrypted_keys(project_id: str, keys_dict: dict, fernet: Fernet):
    """Encrypt and store API keys in Firestore."""
    try:
        # Initialize Firestore client
        db = firestore.client()
        
        # Encrypt each key using Fernet
        encrypted_keys = {}
        for key_name, key_value in keys_dict.items():
            encrypted = fernet.encrypt(key_value.encode()).decode()
            encrypted_keys[key_name] = encrypted
        
        # Store encrypted keys in Firestore
        db.collection('credentials').document('api_keys').set(
            encrypted_keys,
            merge=True
        )
        
        print("\nSuccessfully stored encrypted API keys in Firestore!")
        print("Stored keys:", ", ".join(encrypted_keys.keys()))
        
    except Exception as e:
        print(f"Error storing encrypted keys: {str(e)}")
        raise

def test_decryption(project_id: str, test_key_name: str):
    """Test the decryption flow for an API key."""
    try:
        # Initialize Firestore client
        db = firestore.client()
        
        # Retrieve the encrypted key from Firestore
        creds_doc = db.collection('credentials').document('api_keys').get()
        if not creds_doc.exists:
            raise ValueError("API keys not found in Firestore.")
        
        creds_data = creds_doc.to_dict()
        encrypted_value = creds_data.get(test_key_name)
        
        if not encrypted_value:
            raise ValueError(f"Key '{test_key_name}' not found in Firestore.")
        
        # Retrieve the Fernet key from Secret Manager
        fernet = get_encryption_key(project_id)
        
        # Decrypt the value
        decrypted_key = fernet.decrypt(encrypted_value.encode()).decode()
        
        print(f"\nSuccessfully decrypted '{test_key_name}': {decrypted_key}")
        
        return decrypted_key
        
    except Exception as e:
        print(f"Error during decryption: {str(e)}")
        raise

if __name__ == "__main__":
    PROJECT_ID = "258766016727"
    
    # Uncomment the following lines **only once** to store the encryption key
    # fernet_key = store_encryption_key(PROJECT_ID)
    # print(f"Fernet Key: {fernet_key}")
    
    # Initialize Fernet with the existing key
    fernet = get_encryption_key(PROJECT_ID)
    
    # API keys to store (example)
    api_keys = {
        "ALPHA_VANTAGE_KEY": "BIIQSSO5MPS3GBO0",
        "RENTCAST_KEY": "7512ce0e75a241b49de54306ca78f38f",
        "FRED_KEY": "3fe5555089b7af1a3f7cd10df9f17726",
        "PLAID_CLIENT_ID": "678953cb559345002587ec7e",
        "PLAID_SECRET": "1dc05827da8670928df83473315054"
    }
    
    # Store encrypted API keys in Firestore
    store_encrypted_keys(PROJECT_ID, api_keys, fernet)
    
    # Test decryption of an existing key
    test_key = "ALPHA_VANTAGE_KEY"
    print(f"\nTesting decryption for '{test_key}'")
    decrypted_value = test_decryption(PROJECT_ID, test_key)
    print(f"Decrypted value: {decrypted_value}")