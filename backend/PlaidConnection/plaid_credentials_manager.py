from google.cloud import secretmanager
import firebase_admin
from firebase_admin import credentials, firestore
from cryptography.fernet import Fernet
import os
from functools import lru_cache
from typing import Optional, Tuple
import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from EncryptionKeyStorage.API_key_manager import APIKeyManager

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
            cred = credentials.Certificate('/Users/liambouayad/Documents/Documents/Sensitive_Data/fynnance-5031a-firebase-adminsdk-9mn1g-87d7537a7c.json')
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()
        self.api_key_manager = APIKeyManager()
        self.fernet = self.api_key_manager.fernet
        self._initialized = True

    def get_plaid_credentials(self) -> Tuple[str, str]:
        """Get Plaid client ID and secret."""
        try:
            client_id = self.api_key_manager.get_api_key('p_clientid')
            secret = self.api_key_manager.get_api_key('p_secret')
            return client_id, secret
        except Exception as e:
            print(f"Error retrieving Plaid credentials: {str(e)}")
            raise

    def store_user_access_token(self, user_id: str, access_token: str, item_id: str = None) -> None:
        """
        Store a user's Plaid access token securely in Firestore.
        The access token is encrypted using the Fernet key from GCP.
        
        Args:
            user_id: The unique identifier for the user (e.g., Firebase Auth UID)
            access_token: The Plaid access token to store
            item_id: Optional Plaid item ID associated with the access token
        """
        try:
            # Encrypt the access token using Fernet
            encrypted_token = self.fernet.encrypt(access_token.encode()).decode()
            
            # Prepare data to store
            data = {
                'access_token': encrypted_token,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            if item_id:
                data['item_id'] = item_id
            
            # Store in Firestore under the user's document
            user_ref = self.db.collection('users').document(user_id)
            plaid_data_ref = user_ref.collection('plaid_data').document('access_tokens')
            
            # Store the encrypted token and update user metadata
            batch = self.db.batch()
            batch.set(plaid_data_ref, data, merge=True)
            batch.update(user_ref, {
                'has_plaid_connection': True,
                'last_plaid_update': firestore.SERVER_TIMESTAMP
            })
            batch.commit()
            
            print(f"Successfully stored encrypted access token for user '{user_id}'")
            
        except Exception as e:
            print(f"Error storing access token: {str(e)}")
            raise

    def get_user_access_token(self, user_id: str) -> Optional[Tuple[str, str]]:
        """
        Retrieve and decrypt a user's Plaid access token from Firestore.
        
        Args:
            user_id: The unique identifier for the user (e.g., Firebase Auth UID)
            
        Returns:
            Optional[Tuple[str, str]]: A tuple of (access_token, item_id) if found, None otherwise
        """
        try:
            # Get the encrypted token from Firestore
            plaid_data_ref = self.db.collection('users').document(user_id).collection('plaid_data').document('access_tokens')
            doc = plaid_data_ref.get()
            
            if not doc.exists:
                print(f"No Plaid access token found for user '{user_id}'")
                return None
            
            data = doc.to_dict()
            encrypted_token = data.get('access_token')
            item_id = data.get('item_id')
            
            if not encrypted_token:
                print(f"No access token found in Plaid data for user '{user_id}'")
                return None
            
            # Decrypt the access token using Fernet
            access_token = self.fernet.decrypt(encrypted_token.encode()).decode()
            
            print(f"Successfully retrieved and decrypted access token for user '{user_id}'")
            
            return access_token, item_id
            
        except Exception as e:
            print(f"Error retrieving access token: {str(e)}")
            raise

    def remove_user_access_token(self, user_id: str) -> None:
        """
        Remove a user's Plaid access token and related data.
        
        Args:
            user_id: The unique identifier for the user
        """
        try:
            # Get references to the documents
            user_ref = self.db.collection('users').document(user_id)
            plaid_data_ref = user_ref.collection('plaid_data').document('access_tokens')
            
            # Delete the access token and update user metadata
            batch = self.db.batch()
            batch.delete(plaid_data_ref)
            batch.update(user_ref, {
                'has_plaid_connection': False,
                'last_plaid_update': firestore.SERVER_TIMESTAMP
            })
            batch.commit()
            
            print(f"Successfully removed Plaid access token for user '{user_id}'")
            
        except Exception as e:
            print(f"Error removing access token: {str(e)}")
            raise

if __name__ == "__main__":
    # Test the manager with a dummy token
    PROJECT_ID = "258766016727"
    os.environ['GOOGLE_CLOUD_PROJECT'] = PROJECT_ID
    
    manager = PlaidCredentialsManager()
    test_user_id = "test_user_123"  # This would normally be a Firebase Auth UID
    test_token = "access-sandbox-12345"
    test_item_id = "item-sandbox-12345"
    
    print("\nTesting Plaid Credentials Manager:")
    
    # First create the user document
    print("1. Creating test user document...")
    user_ref = manager.db.collection('users').document(test_user_id)
    user_ref.set({
        'created_at': firestore.SERVER_TIMESTAMP,
        'has_plaid_connection': False
    })
    
    print("2. Storing test access token...")
    manager.store_user_access_token(test_user_id, test_token, test_item_id)
    
    print("\n3. Retrieving test access token...")
    result = manager.get_user_access_token(test_user_id)
    if result:
        retrieved_token, retrieved_item_id = result
        print(f"Retrieved token: {retrieved_token}")
        print(f"Retrieved item ID: {retrieved_item_id}")
        assert retrieved_token == test_token, "Token mismatch!"
        assert retrieved_item_id == test_item_id, "Item ID mismatch!"
    
    print("\n4. Removing test access token...")
    manager.remove_user_access_token(test_user_id)
    
    print("\n5. Verifying removal...")
    result = manager.get_user_access_token(test_user_id)
    assert result is None, "Token was not properly removed!"
    
    # Clean up test user
    print("\n6. Cleaning up test user...")
    user_ref.delete()
    
    print("\nAll tests passed successfully!") 