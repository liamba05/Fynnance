from google.cloud import secretmanager
import firebase_admin
from firebase_admin import credentials
import secrets

def store_secrets_in_gcp(project_id: str, fernet_key: str, firebase_salt: str, flask_secret: str):
    """Store the Fernet key, Firebase salt, and Flask secret in Google Cloud Secret Manager."""
    try:
        # Initialize with credentials
        cred = credentials.Certificate('/Users/liambouayad/Documents/Documents/Sensitive_Data/fynnance-5031a-firebase-adminsdk-9mn1g-87d7537a7c.json')
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        # Create the Secret Manager client with the same credentials
        client = secretmanager.SecretManagerServiceClient(
            credentials=cred.get_credential()
        )
        
        # The parent resource name for the project
        parent = f"projects/{project_id}"
        
        # Add Flask secret key to Secret Manager
        flask_secret_obj = client.create_secret(
            request={
                "parent": parent,
                "secret_id": "FLASK_SECRET_KEY",
                "secret": {
                    "replication": {"automatic": {}},
                },
            }
        )
        
        client.add_secret_version(
            request={
                "parent": flask_secret_obj.name,
                "payload": {"data": flask_secret.encode()},
            }
        )
        
        # Create and store Fernet key secret
        fernet_secret = client.create_secret(
            request={
                "parent": parent,
                "secret_id": "PLAID_FERNET_KEY",
                "secret": {
                    "replication": {"automatic": {}},
                },
            }
        )
        
        # Add the secret version for Fernet key
        client.add_secret_version(
            request={
                "parent": fernet_secret.name,
                "payload": {"data": fernet_key.encode()},
            }
        )
        
        # Create and store Firebase salt secret
        salt_secret = client.create_secret(
            request={
                "parent": parent,
                "secret_id": "PLAID_FIREBASE_SALT",
                "secret": {
                    "replication": {"automatic": {}},
                },
            }
        )
        
        # Add the secret version for Firebase salt
        client.add_secret_version(
            request={
                "parent": salt_secret.name,
                "payload": {"data": firebase_salt.encode()},
            }
        )
        
        print("Successfully stored secrets in Google Cloud Secret Manager!")
        print(f"Secret paths:")
        print(f"Fernet Key: {fernet_secret.name}")
        print(f"Firebase Salt: {salt_secret.name}")
        
    except Exception as e:
        print(f"Error storing secrets: {str(e)}")
        raise

def verify_all_secrets():
    """Verify all secrets stored in Google Cloud Secret Manager."""
    try:
        # Initialize with credentials
        cred = credentials.Certificate('/Users/liambouayad/Documents/Documents/Sensitive_Data/fynnance-5031a-firebase-adminsdk-9mn1g-87d7537a7c.json')
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        client = secretmanager.SecretManagerServiceClient(
            credentials=cred.get_credential()
        )
        
        # Get all secrets
        fernet_path = "projects/258766016727/secrets/PLAID_FERNET_KEY/versions/latest"
        salt_path = "projects/258766016727/secrets/PLAID_FIREBASE_SALT/versions/latest"
        flask_path = "projects/258766016727/secrets/FLASK_SECRET_KEY/versions/latest"
        
        # Get responses
        fernet_response = client.access_secret_version(request={"name": fernet_path})
        salt_response = client.access_secret_version(request={"name": salt_path})
        flask_response = client.access_secret_version(request={"name": flask_path})
        
        # Decode secrets
        fernet_key = fernet_response.payload.data.decode()
        firebase_salt = salt_response.payload.data.decode()
        flask_secret = flask_response.payload.data.decode()
        
        print("All secrets retrieved successfully!")
        print(f"Fernet Key: {fernet_key}")
        print(f"Firebase Salt: {firebase_salt}")
        print(f"Flask Secret Key: {flask_secret}")
        
    except Exception as e:
        print(f"Error verifying secrets: {str(e)}")

def store_flask_secret(project_id: str):
    """Store just the Flask secret key in Google Cloud Secret Manager."""
    try:
        # Initialize with credentials
        cred = credentials.Certificate('/Users/liambouayad/Documents/Documents/Sensitive_Data/fynnance-5031a-firebase-adminsdk-9mn1g-87d7537a7c.json')
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        client = secretmanager.SecretManagerServiceClient(
            credentials=cred.get_credential()
        )
        
        # Generate new Flask secret
        flask_secret = secrets.token_hex(16)
        
        # Create and store Flask secret
        flask_secret_obj = client.create_secret(
            request={
                "parent": f"projects/{project_id}",
                "secret_id": "FLASK_SECRET_KEY",
                "secret": {
                    "replication": {"automatic": {}},
                },
            }
        )
        
        client.add_secret_version(
            request={
                "parent": flask_secret_obj.name,
                "payload": {"data": flask_secret.encode()},
            }
        )
        
        print("Successfully stored Flask secret key in Google Cloud Secret Manager!")
        print(f"Secret path: {flask_secret_obj.name}")
        
    except Exception as e:
        print(f"Error storing Flask secret: {str(e)}")
        raise

if __name__ == "__main__":
    verify_all_secrets()