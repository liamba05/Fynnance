import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional, Union
from datetime import date
from flask import session
from EncryptionKeyStorage.API_key_manager import APIKeyManager

class UserDataCollection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserDataCollection, cls).__new__(cls)
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
        self._initialized = True

    def _get_current_user_id(self) -> str:
        """Get the current user's Firebase Auth UID from the session."""
        if 'firebase_user_id' not in session:
            raise ValueError("No authenticated Firebase user found in session")
        return session['firebase_user_id']

    # Required field getters
    def get_first_name(self) -> str:
        """Get user's first name."""
        user_id = self._get_current_user_id()
        doc = self.db.collection('users').document(user_id).get()
        if not doc.exists:
            raise ValueError(f"User {user_id} not found")
        return doc.get('firstName')

    def get_last_name(self) -> str:
        """Get user's last name."""
        user_id = self._get_current_user_id()
        doc = self.db.collection('users').document(user_id).get()
        if not doc.exists:
            raise ValueError(f"User {user_id} not found")
        return doc.get('lastName')

    def get_email(self) -> str:
        """Get user's email."""
        user_id = self._get_current_user_id()
        doc = self.db.collection('users').document(user_id).get()
        if not doc.exists:
            raise ValueError(f"User {user_id} not found")
        return doc.get('email')

    def get_password(self) -> str:
        """Get user's hashed password."""
        user_id = self._get_current_user_id()
        doc = self.db.collection('users').document(user_id).get()
        if not doc.exists:
            raise ValueError(f"User {user_id} not found")
        return doc.get('password')

    def get_date_of_birth(self) -> date:
        """Get user's date of birth."""
        user_id = self._get_current_user_id()
        doc = self.db.collection('users').document(user_id).get()
        if not doc.exists:
            raise ValueError(f"User {user_id} not found")
        dob = doc.get('date_of_birth')
        return firestore.SERVER_TIMESTAMP.to_date(dob) if dob else None

    # Optional field getters
    def get_income(self) -> Union[float, str]:
        """Get user's income if provided."""
        user_id = self._get_current_user_id()
        doc = self.db.collection('users').document(user_id).get()
        if not doc.exists:
            raise ValueError(f"User {user_id} not found")
        income = doc.get('income')
        return income if income is not None else "Field not present."

    def get_assets(self) -> Union[float, str]:
        """Get user's assets if provided."""
        user_id = self._get_current_user_id()
        doc = self.db.collection('users').document(user_id).get()
        if not doc.exists:
            raise ValueError(f"User {user_id} not found")
        assets = doc.get('assets')
        return assets if assets is not None else "Field not present."

    def get_zip_code(self) -> Union[str, str]:
        """Get user's zip code if provided."""
        user_id = self._get_current_user_id()
        doc = self.db.collection('users').document(user_id).get()
        if not doc.exists:
            raise ValueError(f"User {user_id} not found")
        zip_code = doc.get('zipCode')
        return zip_code if zip_code is not None else "Field not present."

    def get_credit_score(self) -> Union[int, str]:
        """Get user's credit score if provided."""
        user_id = self._get_current_user_id()
        doc = self.db.collection('users').document(user_id).get()
        if not doc.exists:
            raise ValueError(f"User {user_id} not found")
        credit_score = doc.get('creditScore')
        if credit_score is None:
            credit_score = doc.get('credit_score')
        return credit_score if credit_score is not None else "Field not present."

    # Optional field setters
    def set_income(self, income: float) -> None:
        """Set user's income."""
        if income < 0:
            raise ValueError("Income cannot be negative")
        user_id = self._get_current_user_id()
        self.db.collection('users').document(user_id).set({
            'income': income
        }, merge=True)

    def set_assets(self, assets: float) -> None:
        """Set user's assets."""
        if assets < 0:
            raise ValueError("Assets cannot be negative")
        user_id = self._get_current_user_id()
        self.db.collection('users').document(user_id).set({
            'assets': assets
        }, merge=True)

    def set_zip_code(self, zip_code: str) -> None:
        """Set user's zip code."""
        if not zip_code.isdigit() or len(zip_code) != 5:
            raise ValueError("Invalid ZIP code format")
        user_id = self._get_current_user_id()
        self.db.collection('users').document(user_id).set({
            'zipCode': zip_code
        }, merge=True)

    def set_credit_score(self, credit_score: int) -> None:
        """Set user's credit score."""
        if not isinstance(credit_score, int) or credit_score < 300 or credit_score > 850:
            raise ValueError("Invalid credit score. Must be an integer between 300 and 850")
        user_id = self._get_current_user_id()
        self.db.collection('users').document(user_id).set({
            'creditScore': credit_score
        }, merge=True)

    def set_first_name(self, first_name: str) -> None:
        """Set user's first name."""
        if not first_name or not first_name.strip():
            raise ValueError("First name cannot be empty")
        user_id = self._get_current_user_id()
        self.db.collection('users').document(user_id).set({
            'firstName': first_name
        }, merge=True)

    def set_last_name(self, last_name: str) -> None:
        """Set user's last name."""
        if not last_name or not last_name.strip():
            raise ValueError("Last name cannot be empty")
        user_id = self._get_current_user_id()
        self.db.collection('users').document(user_id).set({
            'lastName': last_name
        }, merge=True)

    def set_email(self, email: str) -> None:
        """Set user's email."""
        if not email or '@' not in email:
            raise ValueError("Invalid email format")
        user_id = self._get_current_user_id()
        self.db.collection('users').document(user_id).set({
            'email': email
        }, merge=True)

    def set_date_of_birth(self, dob: date) -> None:
        """Set user's date of birth."""
        if not isinstance(dob, date):
            raise ValueError("Date of birth must be a date object")
        user_id = self._get_current_user_id()
        self.db.collection('users').document(user_id).set({
            'date_of_birth': dob
        }, merge=True)

    # GPT Data getters
    def get_goals(self) -> str:
        """Get user's goals."""
        user_id = self._get_current_user_id()
        doc = self.db.collection('users').document(user_id).collection('gpt_data').document('goals').get()
        if not doc.exists:
            return ""
        return doc.get('set_goals', "")

    def get_preferences(self) -> str:
        """Get user's preferences."""
        user_id = self._get_current_user_id()
        doc = self.db.collection('users').document(user_id).collection('gpt_data').document('preferences').get()
        if not doc.exists:
            return ""
        return doc.get('preferences', "")

    def get_memories(self) -> list[str]:
        """Get user's memories as a list. Internal use only."""
        user_id = self._get_current_user_id()
        doc = self.db.collection('users').document(user_id).collection('gpt_data').document('memories').get()
        if not doc.exists:
            return []
        return doc.get('memories', [])

    def get_conclusions(self) -> str:
        """Get user's conclusions. Internal use only."""
        user_id = self._get_current_user_id()
        doc = self.db.collection('users').document(user_id).collection('gpt_data').document('conclusions').get()
        if not doc.exists:
            return ""
        return doc.get('conclusions', "")

    # GPT Data setters
    def set_goals(self, goals: str) -> None:
        """Set user's goals."""
        if not goals or not goals.strip():
            raise ValueError("Goals cannot be empty")
        user_id = self._get_current_user_id()
        self.db.collection('users').document(user_id).collection('gpt_data').document('goals').set({
            'set_goals': goals
        }, merge=True)

    def set_preferences(self, preferences: str) -> None:
        """Set user's preferences."""
        if not preferences or not preferences.strip():
            raise ValueError("Preferences cannot be empty")
        user_id = self._get_current_user_id()
        self.db.collection('users').document(user_id).collection('gpt_data').document('preferences').set({
            'preferences': preferences
        }, merge=True)

    def set_memories(self, memories: list[str]) -> None:
        """Set user's memories list. Internal use only."""
        if not isinstance(memories, list):
            raise ValueError("Memories must be a list of strings")
        if not all(isinstance(m, str) and m.strip() for m in memories):
            raise ValueError("All memories must be non-empty strings")
        
        user_id = self._get_current_user_id()
        self.db.collection('users').document(user_id).collection('gpt_data').document('memories').set({
            'memories': memories
        }, merge=True)

    def add_to_memories(self, memories: Union[str, list[str]]) -> None:
        """Append one or more memories to the user's memories list. Internal use only.
        
        Args:
            memories: Either a single memory string or a list of memory strings to add
        
        Raises:
            ValueError: If any memory string is empty or if input type is invalid
        """
        # Convert single string to list for uniform handling
        if isinstance(memories, str):
            memories = [memories]
        elif not isinstance(memories, list):
            raise ValueError("Memories must be either a string or a list of strings")
        
        # Validate all memories
        if not all(isinstance(m, str) and m.strip() for m in memories):
            raise ValueError("All memories must be non-empty strings")
        
        # Clean the memories (strip whitespace)
        memories = [m.strip() for m in memories]
        
        user_id = self._get_current_user_id()
        doc_ref = self.db.collection('users').document(user_id).collection('gpt_data').document('memories')
        doc = doc_ref.get()
        
        current_memories = []
        if doc.exists:
            current_memories = doc.get('memories', [])
        
        # Ensure we're working with a list
        if not isinstance(current_memories, list):
            current_memories = []
        
        # Add all new memories
        current_memories.extend(memories)
        
        # Update the document
        doc_ref.set({
            'memories': current_memories
        }, merge=True)

    def set_conclusions(self, conclusions: str) -> None:
        """Set user's conclusions. Internal use only."""
        if not conclusions or not conclusions.strip():
            raise ValueError("Conclusions cannot be empty")
        user_id = self._get_current_user_id()
        self.db.collection('users').document(user_id).collection('gpt_data').document('conclusions').set({
            'conclusions': conclusions
        }, merge=True)
