# test_internal_methods.py

import traceback
from flask import Flask, session
import unittest
from MarketDataConnection.estate_data_service import EstateDataService
from UserDataCollection.user_data_collection import UserDataCollection

app = Flask(__name__)
app.secret_key = 'random-secret-key'  # needed for sessions

class TestDataCollection(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        session['firebase_user_id'] = "gzygMSxt67eTdVBiNOym6p4dcIn2"
        
        # Initialize test instances
        self.user_data = UserDataCollection()
        self.estate_data = EstateDataService()

    def tearDown(self):
        self.ctx.pop()

    def safe_call(self, description, func, *args, **kwargs):
        """
        Helper that calls a function safely and prints either the result or an error.
        Even if one fails, we continue testing the next.
        """
        print(f"\n--- Testing: {description} ---")
        try:
            result = func(*args, **kwargs)
            print(f"Result for {description}:\n{result}")
            return result
        except Exception as e:
            print(f"ERROR in {description}: {e}")
            traceback.print_exc()
            return None

    def test_user_data_collection(self):
        """Test UserDataCollection methods"""
        print("\n=== Testing UserDataCollection Methods ===")
        
        # Test basic user info methods
        self.safe_call("UserDataCollection.get_first_name", self.user_data.get_first_name)
        self.safe_call("UserDataCollection.get_last_name", self.user_data.get_last_name)
        self.safe_call("UserDataCollection.get_email", self.user_data.get_email)
        
        # Test financial info methods
        self.safe_call("UserDataCollection.get_income", self.user_data.get_income)
        self.safe_call("UserDataCollection.get_zip_code", self.user_data.get_zip_code)
        self.safe_call("UserDataCollection.get_credit_score", self.user_data.get_credit_score)

    def test_estate_data_service(self):
        """Test EstateDataService methods"""
        print("\n=== Testing EstateDataService Methods ===")
        
        # Test market data methods
        print("\n=== Testing EstateDataService Methods ===\n")
        
        print("--- Testing: EstateDataService.get_market_stats ---")
        result = self.estate_data.get_market_stats()
        print("Result for EstateDataService.get_market_stats:")
        print(result)
        
        print("\n--- Testing: EstateDataService.get_rental_listings (income-based) ---")
        rental_result = self.estate_data.get_rental_listings(min_beds=2)  # No max_price to test income-based filtering
        print("Result for EstateDataService.get_rental_listings (income-based):")
        print(rental_result)
        
        print("\n--- Testing: EstateDataService.get_property_listings (income-based) ---")
        property_result = self.estate_data.get_property_listings(min_beds=2)  # No max_price to test income-based filtering
        print("Result for EstateDataService.get_property_listings (income-based):")
        print(property_result)
        
        print("\n--- Testing: EstateDataService.analyze_investment_potential ---")
        investment_result = self.estate_data.analyze_investment_potential(1000000, 4000)
        print("Result for EstateDataService.analyze_investment_potential:")
        print(investment_result)
        
        print("\n--- Testing: EstateDataService.get_affordability_analysis ---")
        affordability_result = self.estate_data.get_affordability_analysis()
        print("Result for EstateDataService.get_affordability_analysis:")
        print(affordability_result)

if __name__ == "__main__":
    unittest.main(verbosity=2)
