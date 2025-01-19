"""
Test module for Plaid data collection functionality.
Tests all methods for retrieving and processing Plaid data.
"""

import unittest
import sys
import os
from datetime import datetime, timedelta
from flask import Flask, session
import json
from pprint import pprint

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PlaidConnection.plaid_data_service import (
    get_investment_holdings,
    get_account_balances,
    get_transactions,
    get_liabilities,
    get_user_financial_profile
)
from PlaidConnection.plaid_credentials_manager import PlaidCredentialsManager

def print_schema(title: str, data: dict) -> None:
    """Helper function to print JSON schemas in a readable format."""
    print("\n" + "="*80)
    print(f"{title} Schema:")
    print("="*80)
    pprint(data, indent=2, width=80)
    print("="*80 + "\n")

class TestPlaidDataCollection(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Set up Flask app and context
        self.app = Flask(__name__)
        self.app.secret_key = 'test-secret-key'  # Required for session
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.request_context = self.app.test_request_context()
        self.request_context.push()
        
        # Set up the session with a real user ID
        session['firebase_user_id'] = 'xEdRMQ3IdQOrR29g4gsddIRt1V23'
        
        # Get credentials manager
        self.credentials_manager = PlaidCredentialsManager()
        
        # Get Plaid client and access token
        client_id, secret = self.credentials_manager.get_plaid_credentials()
        self.plaid_client = self.credentials_manager.create_plaid_client(client_id, secret)
        
        # Get access token for the test user
        result = self.credentials_manager.get_user_access_token(session['firebase_user_id'])
        if not result:
            raise ValueError("No Plaid access token found for test user")
        self.access_token, self.item_id = result
        
    def tearDown(self):
        """Clean up after each test method."""
        self.request_context.pop()
        self.app_context.pop()

    def test_investment_holdings(self):
        """Test investment holdings data retrieval"""
        result = get_investment_holdings(plaid_client=self.plaid_client)
        print_schema("Investment Holdings", result)
        self.assertIsInstance(result, dict)
        self.assertIn('accounts', result)
        self.assertIn('holdings', result)

    def test_account_balances(self):
        """Test account balances data retrieval"""
        result = get_account_balances(plaid_client=self.plaid_client)
        print_schema("Account Balances", result)
        self.assertIsInstance(result, list)
        if result:
            self.assertIn('name', result[0])
            self.assertIn('type', result[0])
            self.assertIn('balance', result[0])

    def test_transactions(self):
        """Test transactions data retrieval"""
        result = get_transactions(
            plaid_client=self.plaid_client,
            start_date=(datetime.now() - timedelta(days=30)).date(),
            end_date=datetime.now().date()
        )
        print_schema("Transactions", result)
        self.assertIsInstance(result, list)
        if result:
            self.assertIn('name', result[0])
            self.assertIn('amount', result[0])

    def test_liabilities(self):
        """Test all liabilities data retrieval"""
        result = get_liabilities(plaid_client=self.plaid_client)
        print_schema("Liabilities", result)
        self.assertIsInstance(result, dict)
        self.assertIn('credit_cards', result)
        self.assertIn('student_loans', result)
        self.assertIn('mortgages', result)

    def test_user_financial_profile(self):
        """Test comprehensive financial profile retrieval"""
        result = get_user_financial_profile(
            plaid_client=self.plaid_client,
            transactions_days=30
        )
        print_schema("User Financial Profile", result)
        self.assertIsInstance(result, dict)
        self.assertIn('accounts', result)
        self.assertIn('balances', result)
        self.assertIn('investments', result)
        self.assertIn('liabilities', result)
        self.assertIn('transactions', result)
        self.assertIn('summary', result)

if __name__ == '__main__':
    unittest.main() 