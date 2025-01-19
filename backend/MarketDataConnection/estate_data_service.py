import requests
from typing import Dict, Any, List, Optional
from EncryptionKeyStorage.API_key_manager import APIKeyManager
from UserDataCollection.user_data_collection import UserDataCollection
import numpy as np
from datetime import datetime, timedelta

class EstateDataService:
    _instance = None
    BASE_URL = "https://api.rentcast.io/v1"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EstateDataService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.api_key_manager = APIKeyManager()
        self.user_data = UserDataCollection()
        self.api_key = self.api_key_manager.get_api_key('rentcast')
        self.headers = {
            "accept": "application/json",
            "X-Api-Key": self.api_key
        }
        self._initialized = True

    def _get_user_zip_code(self) -> str:
        """Get the current user's zip code from UserDataCollection."""
        zip_code = self.user_data.get_zip_code()
        if zip_code == "Field not present.":
            raise ValueError("User zip code not set. Please set a zip code to get local market data.")
        return zip_code

    def get_market_stats(self, property_type: str = "residential") -> Dict[str, Any]:
        """
        Get detailed market statistics for the user's area.
        
        Args:
            property_type: Type of property ("residential", "multifamily", "condo")
            
        Returns:
            Dictionary containing market statistics and trends
        """
        zip_code = self._get_user_zip_code()
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/market-stats",
                headers=self.headers,
                params={
                    "zip": zip_code,
                    "propertyType": property_type
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Process and structure the data
            return {
                "market_overview": {
                    "median_rent": data.get("rentMedian"),
                    "median_price": data.get("priceMedian"),
                    "price_to_rent_ratio": data.get("priceRentRatio"),
                    "rental_yield": data.get("rentalYield"),
                    "days_on_market": data.get("daysOnMarket"),
                    "rental_vacancy_rate": data.get("vacancyRate")
                },
                "trends": {
                    "rent_trend": data.get("rentTrend"),
                    "price_trend": data.get("priceTrend"),
                    "inventory_trend": data.get("inventoryTrend")
                },
                "comparative": {
                    "rent_percentile": data.get("rentPercentile"),
                    "price_percentile": data.get("pricePercentile")
                }
            }
        except requests.RequestException as e:
            raise Exception(f"Error fetching market stats: {str(e)}")

    def get_rental_listings(self, max_price: Optional[float] = None, min_beds: int = 1) -> List[Dict[str, Any]]:
        """
        Get active rental listings in the user's area with smart filtering.
        
        Args:
            max_price: Maximum monthly rent (optional)
            min_beds: Minimum number of bedrooms
            
        Returns:
            List of rental listings with details
        """
        zip_code = self._get_user_zip_code()
        
        try:
            params = {
                "zip": zip_code,
                "minBeds": min_beds,
                "status": "Active",
                "limit": 50  # Adjust as needed
            }
            if max_price:
                params["maxPrice"] = max_price
                
            response = requests.get(
                f"{self.BASE_URL}/rental-listings",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            listings = response.json()
            
            return [{
                "address": listing.get("address"),
                "price": listing.get("price"),
                "bedrooms": listing.get("bedrooms"),
                "bathrooms": listing.get("bathrooms"),
                "sqft": listing.get("squareFootage"),
                "price_per_sqft": listing.get("pricePerSquareFoot"),
                "days_on_market": listing.get("daysOnMarket"),
                "property_type": listing.get("propertyType"),
                "year_built": listing.get("yearBuilt"),
                "url": listing.get("listingUrl")
            } for listing in listings]
            
        except requests.RequestException as e:
            raise Exception(f"Error fetching rental listings: {str(e)}")

    def get_property_listings(self, max_price: Optional[float] = None, min_beds: int = 2) -> List[Dict[str, Any]]:
        """
        Get active property listings for sale in the user's area.
        
        Args:
            max_price: Maximum property price (optional)
            min_beds: Minimum number of bedrooms
            
        Returns:
            List of property listings with details
        """
        zip_code = self._get_user_zip_code()
        
        try:
            params = {
                "zip": zip_code,
                "minBeds": min_beds,
                "status": "Active",
                "limit": 50  # Adjust as needed
            }
            if max_price:
                params["maxPrice"] = max_price
                
            response = requests.get(
                f"{self.BASE_URL}/sales-listings",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            listings = response.json()
            
            return [{
                "address": listing.get("address"),
                "price": listing.get("price"),
                "bedrooms": listing.get("bedrooms"),
                "bathrooms": listing.get("bathrooms"),
                "sqft": listing.get("squareFootage"),
                "price_per_sqft": listing.get("pricePerSquareFoot"),
                "days_on_market": listing.get("daysOnMarket"),
                "property_type": listing.get("propertyType"),
                "year_built": listing.get("yearBuilt"),
                "url": listing.get("listingUrl")
            } for listing in listings]
            
        except requests.RequestException as e:
            raise Exception(f"Error fetching property listings: {str(e)}")

    def analyze_investment_potential(self, property_price: float, expected_rent: float) -> Dict[str, Any]:
        """
        Analyze the investment potential of a property.
        
        Args:
            property_price: Purchase price of the property
            expected_rent: Expected monthly rental income
            
        Returns:
            Dictionary containing investment analysis metrics
        """
        # Get market data for comparison
        market_stats = self.get_market_stats()
        
        # Calculate key metrics
        annual_rent = expected_rent * 12
        gross_yield = (annual_rent / property_price) * 100
        
        # Estimate expenses (typical percentages)
        property_tax = property_price * 0.015  # 1.5% annual
        insurance = property_price * 0.005     # 0.5% annual
        maintenance = annual_rent * 0.10       # 10% of rent
        vacancy_cost = annual_rent * (market_stats["market_overview"]["rental_vacancy_rate"] / 100)
        
        # Calculate net metrics
        total_expenses = property_tax + insurance + maintenance + vacancy_cost
        net_income = annual_rent - total_expenses
        net_yield = (net_income / property_price) * 100
        
        # Compare to market averages
        market_yield = market_stats["market_overview"]["rental_yield"]
        price_to_rent = property_price / annual_rent
        market_price_to_rent = market_stats["market_overview"]["price_to_rent_ratio"]
        
        return {
            "investment_metrics": {
                "gross_yield": round(gross_yield, 2),
                "net_yield": round(net_yield, 2),
                "price_to_rent_ratio": round(price_to_rent, 2),
                "estimated_annual_return": round(net_yield + 2, 2)  # Assuming 2% appreciation
            },
            "estimated_costs": {
                "annual_property_tax": round(property_tax, 2),
                "annual_insurance": round(insurance, 2),
                "annual_maintenance": round(maintenance, 2),
                "vacancy_cost": round(vacancy_cost, 2),
                "total_expenses": round(total_expenses, 2)
            },
            "market_comparison": {
                "market_yield_difference": round(gross_yield - market_yield, 2),
                "price_to_rent_difference": round(market_price_to_rent - price_to_rent, 2),
                "relative_value": "above_market" if gross_yield > market_yield else "below_market"
            },
            "recommendation": self._generate_investment_recommendation(
                gross_yield, market_yield, price_to_rent, market_price_to_rent
            )
        }

# EstateDataService.py

    def get_affordability_analysis(self) -> Dict[str, Any]:
        """
        Analyze what properties the user can afford based on their income
        and credit score only (assets portion removed).
        """

        # Get user financial data
        income = self.user_data.get_income()
        credit_score = self.user_data.get_credit_score()

        if income == "Field not present.":
            raise ValueError("User income not set. Please set income for affordability analysis.")

        # Default credit score to 680 if not present
        credit_score = int(credit_score) if credit_score != "Field not present." else 680

        # Calculate affordability metrics
        monthly_income = float(income) / 12
        max_monthly_payment = monthly_income * 0.28  # 28% DTI ratio

        # Estimate max home price based solely on monthly payment
        interest_rate = self._estimate_interest_rate(credit_score)
        max_home_price = self._calculate_max_loan(max_monthly_payment, interest_rate, 30)

        # Get market data for comparison
        market_stats = self.get_market_stats()
        median_price = market_stats["market_overview"]["median_price"]

        return {
            "affordability_metrics": {
                "max_home_price": round(max_home_price, 2),
                "max_monthly_payment": round(max_monthly_payment, 2),
                "estimated_interest_rate": round(interest_rate, 2),
            },
            "market_comparison": {
                "median_home_price": median_price,
                "price_difference": round(max_home_price - median_price, 2),
                "affordability_index": round(max_home_price / median_price, 2),
            },
            "recommendations": self._generate_affordability_recommendation(
                max_home_price, median_price, credit_score
            ),
            # Provide up to 5 sample listings under the max_home_price
            "sample_listings": self.get_property_listings(max_price=max_home_price)[:5]
        }


    def _generate_affordability_recommendation(
        self, max_price: float, median_price: float, credit_score: int
    ) -> Dict[str, Any]:
        """
        Generate personalized recommendations based on affordability analysis.
        (Assets/down_payment logic removed.)
        """
        recommendations = []

        # Market position analysis
        if max_price < median_price:
            recommendations.append({
                "type": "market_position",
                "message": "You may be priced out of median homes in this area",
                "action_items": [
                    "Consider nearby areas with lower median prices",
                    "Look for below-market opportunities",
                    "Consider smaller properties or condos"
                ]
            })

        # Credit score recommendations
        if credit_score < 740:
            recommendations.append({
                "type": "credit_improvement",
                "message": "Improving your credit score could lower your interest rate",
                "action_items": [
                    "Work on improving credit score",
                    "Pay down existing debt",
                    "Check for credit report errors"
                ]
            })

        summary_str = (
            "Focus on " + ", ".join([r["type"].replace("_", " ") for r in recommendations])
            if recommendations else "No specific recommendations"
        )

        return {
            "recommendations": recommendations,
            "summary": summary_str
        }

    def _estimate_interest_rate(self, credit_score: int) -> float:
        """Estimate mortgage interest rate based on credit score."""
        if credit_score >= 760:
            return 0.0425  # Base rate
        elif credit_score >= 700:
            return 0.0450
        elif credit_score >= 660:
            return 0.0475
        else:
            return 0.0525

    def _calculate_max_loan(self, monthly_payment: float, interest_rate: float, years: int) -> float:
        """Calculate maximum loan amount based on monthly payment."""
        monthly_rate = interest_rate / 12
        num_payments = years * 12
        max_loan = monthly_payment * ((1 - (1 + monthly_rate)**-num_payments) / monthly_rate)
        return max_loan

    def _generate_investment_recommendation(
        self, gross_yield: float, market_yield: float, 
        price_to_rent: float, market_price_to_rent: float
    ) -> Dict[str, Any]:
        """Generate investment recommendations based on metrics."""
        score = 0
        reasons = []
        
        # Score the investment potential
        if gross_yield > market_yield:
            score += 2
            reasons.append("Above market rental yield")
        if price_to_rent < market_price_to_rent:
            score += 2
            reasons.append("Better than market price-to-rent ratio")
        if gross_yield > 8:
            score += 1
            reasons.append("High gross yield potential")
        
        # Generate recommendation
        if score >= 4:
            recommendation = "Strong investment opportunity"
        elif score >= 2:
            recommendation = "Moderate investment opportunity"
        else:
            recommendation = "Exercise caution"
            
        return {
            "score": score,
            "recommendation": recommendation,
            "reasons": reasons
        }