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
        print(f"Debug - API Key: {self.api_key[:5]}...")
        self.headers = {
            "Accept": "application/json",
            "X-Api-Key": self.api_key
        }
        # Cache for market stats to reduce API calls
        self._market_stats_cache = {}
        self._initialized = True

    def _get_user_zip_code(self) -> str:
        """Get the current user's zip code from UserDataCollection."""
        zip_code = self.user_data.get_zip_code()
        if zip_code == "Field not present.":
            raise ValueError("User zip code not set. Please set a zip code to get local market data.")
        return zip_code

    def get_market_stats(self, property_type: str = "residential", use_cache: bool = True, zip_code: str = None) -> Dict[str, Any]:
        """
        Get summarized market statistics for the user's area.
        
        Args:
            property_type: Type of property ("residential", "multifamily", "condo")
            use_cache: Whether to use cached results if available
            
        Returns:
            Dictionary containing market statistics summary
        """
        zip_code = zip_code if zip_code is not None else self._get_user_zip_code()
        cache_key = f"{zip_code}_{property_type}"
        
        # Return cached results if available and requested
        if use_cache and cache_key in self._market_stats_cache:
            return self._market_stats_cache[cache_key]
        
        try:
            # Get sale listings for price data
            sale_response = requests.get(
                f"{self.BASE_URL}/listings/sale",
                headers=self.headers,
                params={
                    "zipCode": zip_code,
                    "propertyType": property_type,
                    "limit": 20
                }
            )
            sale_response.raise_for_status()
            sale_properties = sale_response.json()
            
            # Get rental listings for rent data
            rental_response = requests.get(
                f"{self.BASE_URL}/listings/rental/long-term",
                headers=self.headers,
                params={
                    "zipCode": zip_code,
                    "propertyType": property_type,
                    "limit": 20
                }
            )
            rental_response.raise_for_status()
            rental_properties = rental_response.json()
            
            # Calculate statistics
            sale_prices = [p.get('price', 0) for p in sale_properties if p.get('price')]
            rental_prices = [p.get('price', 0) for p in rental_properties if p.get('price')]
            sale_dom = [p.get('daysOnMarket', 0) for p in sale_properties if p.get('daysOnMarket')]
            
            # Calculate market metrics
            median_price = np.median(sale_prices) if sale_prices else None
            median_rent = np.median(rental_prices) if rental_prices else None
            avg_days_on_market = np.mean(sale_dom) if sale_dom else None
            
            # Calculate derived metrics
            if median_price and median_rent and median_rent > 0:
                price_to_rent = median_price / (median_rent * 12)
                rental_yield = (median_rent * 12 / median_price) * 100 if median_price > 0 else None
            else:
                price_to_rent = None
                rental_yield = None
            
            # Estimate vacancy rate
            total_rentals = len(rental_properties)
            vacant_rentals = len([p for p in rental_properties if p.get('status') == 'available'])
            vacancy_rate = (vacant_rentals / total_rentals * 100) if total_rentals > 0 else None
            
            # Market insights
            insights = []
            if price_to_rent and price_to_rent > 20:
                insights.append("Market favors renting over buying")
            elif price_to_rent and price_to_rent < 15:
                insights.append("Market favors buying over renting")
            
            if avg_days_on_market and avg_days_on_market > 90:
                insights.append("Slower market with longer selling times")
            elif avg_days_on_market and avg_days_on_market < 30:
                insights.append("Fast-moving market with quick sales")
            
            if vacancy_rate and vacancy_rate < 5:
                insights.append("Very competitive rental market")
            elif vacancy_rate and vacancy_rate > 10:
                insights.append("Higher than normal vacancy rates")
            
            result = {
                "market_summary": {
                    "median_rent": median_rent,
                    "median_price": median_price,
                    "price_to_rent_ratio": price_to_rent,
                    "rental_yield": rental_yield,
                    "days_on_market": avg_days_on_market,
                    "rental_vacancy_rate": vacancy_rate
                },
                "market_insights": insights,
                "raw_data": {
                    "sale_listings": sale_properties,
                    "rental_listings": rental_properties
                }
            }
            
            # Cache the results
            self._market_stats_cache[cache_key] = result
            return result
            
        except requests.RequestException as e:
            raise Exception(f"Error fetching market stats: {str(e)}")

    def get_rental_listings(self, max_price: Optional[float] = None, min_beds: int = 1, zip_code: str = None) -> List[Dict[str, Any]]:
        """Get rental listings from cached market stats if available."""
        market_stats = self.get_market_stats(use_cache=True, zip_code=zip_code)
        listings = market_stats["raw_data"]["rental_listings"]
        
        # Get user's income and calculate max affordable rent (30% of monthly income)
        income = self.user_data.get_income()
        if income != "Field not present.":
            monthly_income = float(income) / 12
            max_affordable_rent = monthly_income * 0.3
            # If no max_price specified, use income-based limit
            if max_price is None:
                max_price = max_affordable_rent
        
        # Filter and sort all listings by price
        all_listings = [l for l in listings if l.get('bedrooms', 0) >= min_beds]
        all_listings.sort(key=lambda x: x.get('price', float('inf')))
        
        # Get exactly 12 listings with a balanced mix
        if max_price:
            within_budget = [l for l in all_listings if l.get('price', float('inf')) <= max_price][:8]
            above_budget = [l for l in all_listings if l.get('price', float('inf')) > max_price][:4]
            filtered = (within_budget + above_budget)[:12]  # Ensure exactly 12 listings
        else:
            filtered = all_listings[:12]
        
        # Calculate market context
        all_prices = [l.get('price', 0) for l in all_listings if l.get('price')]
        price_quartiles = np.percentile(all_prices, [25, 50, 75]) if all_prices else [0, 0, 0]
        
        return {
            "market_context": {
                "price_range": {
                    "low": round(price_quartiles[0], 2),
                    "median": round(price_quartiles[1], 2),
                    "high": round(price_quartiles[2], 2)
                },
                "total_listings": len(filtered),  # Always 12 or less
                "affordable_count": len([l for l in filtered if l.get('price', float('inf')) <= max_price]) if max_price else None
            },
            "listings": [{
                "address": f"{listing.get('addressLine1', '')}, {listing.get('city', '')}",
                "price": listing.get("price"),
                "bedrooms": listing.get("bedrooms"),
                "bathrooms": listing.get("bathrooms"),
                "sqft": listing.get("squareFootage"),
                "days_on_market": listing.get("daysOnMarket"),
                "within_budget": listing.get("price", float('inf')) <= max_price if max_price else True
            } for listing in filtered]
        }

    def get_property_listings(self, max_price: Optional[float] = None, min_beds: int = 2, zip_code: str = None) -> List[Dict[str, Any]]:
        """Get property listings from cached market stats if available."""
        market_stats = self.get_market_stats(use_cache=True, zip_code=zip_code)
        listings = market_stats["raw_data"]["sale_listings"]
        
        # Get user's income and calculate max affordable home price
        income = self.user_data.get_income()
        if income != "Field not present.":
            monthly_income = float(income) / 12
            # Using standard 28% DTI ratio for housing
            max_monthly_payment = monthly_income * 0.28
            # Estimate max affordable home price if not specified
            if max_price is None:
                credit_score = self.user_data.get_credit_score()
                credit_score = int(credit_score) if credit_score != "Field not present." else 680
                interest_rate = self._estimate_interest_rate(credit_score)
                max_price = self._calculate_max_loan(max_monthly_payment, interest_rate, 30)
        
        # Filter and sort all listings by price
        all_listings = [l for l in listings if l.get('bedrooms', 0) >= min_beds]
        all_listings.sort(key=lambda x: x.get('price', float('inf')))
        
        # Get exactly 12 listings with a balanced mix
        if max_price:
            within_budget = [l for l in all_listings if l.get('price', float('inf')) <= max_price][:8]
            above_budget = [l for l in all_listings if l.get('price', float('inf')) > max_price][:4]
            filtered = (within_budget + above_budget)[:12]  # Ensure exactly 12 listings
        else:
            filtered = all_listings[:12]
        
        # Calculate market context
        all_prices = [l.get('price', 0) for l in all_listings if l.get('price')]
        price_quartiles = np.percentile(all_prices, [25, 50, 75]) if all_prices else [0, 0, 0]
        
        return {
            "market_context": {
                "price_range": {
                    "low": round(price_quartiles[0], 2),
                    "median": round(price_quartiles[1], 2),
                    "high": round(price_quartiles[2], 2)
                },
                "total_listings": len(filtered),  # Always 12 or less
                "affordable_count": len([l for l in filtered if l.get('price', float('inf')) <= max_price]) if max_price else None
            },
            "listings": [{
                "address": f"{listing.get('addressLine1', '')}, {listing.get('city', '')}",
                "price": listing.get("price"),
                "bedrooms": listing.get("bedrooms"),
                "bathrooms": listing.get("bathrooms"),
                "sqft": listing.get("squareFootage"),
                "days_on_market": listing.get("daysOnMarket"),
                "within_budget": listing.get("price", float('inf')) <= max_price if max_price else True
            } for listing in filtered]
        }

    def analyze_investment_potential(self, property_price: float, expected_rent: float, zip_code: str = None) -> Dict[str, Any]:
        """
        Analyze the investment potential of a property.
        """
        market_stats = self.get_market_stats(zip_code=zip_code)
        
        annual_rent = expected_rent * 12
        gross_yield = (annual_rent / property_price) * 100
        
        # Estimate expenses (typical percentages)
        property_tax = property_price * 0.015
        insurance = property_price * 0.005
        maintenance = annual_rent * 0.10
        vacancy_cost = annual_rent * (market_stats["market_summary"]["rental_vacancy_rate"] / 100)
        
        total_expenses = property_tax + insurance + maintenance + vacancy_cost
        net_income = annual_rent - total_expenses
        net_yield = (net_income / property_price) * 100
        
        market_yield = market_stats["market_summary"]["rental_yield"]
        price_to_rent = property_price / annual_rent
        market_price_to_rent = market_stats["market_summary"]["price_to_rent_ratio"]
        
        return {
            "summary": {
                "gross_yield": round(gross_yield, 2),
                "net_yield": round(net_yield, 2),
                "monthly_cashflow": round(net_income / 12, 2),
                "total_monthly_expenses": round(total_expenses / 12, 2)
            },
            "market_comparison": {
                "yield_vs_market": round(gross_yield - market_yield, 2),
                "price_to_rent_vs_market": round(market_price_to_rent - price_to_rent, 2)
            },
            "recommendation": self._generate_investment_recommendation(
                gross_yield, market_yield, price_to_rent, market_price_to_rent
            )
        }

    def get_affordability_analysis(self, zip_code: str = None) -> Dict[str, Any]:
        """
        Analyze what properties the user can afford based on their income and credit score.
        """
        income = self.user_data.get_income()
        credit_score = self.user_data.get_credit_score()

        if income == "Field not present.":
            raise ValueError("User income not set. Please set income for affordability analysis.")

        credit_score = int(credit_score) if credit_score != "Field not present." else 680

        monthly_income = float(income) / 12
        max_monthly_payment = monthly_income * 0.28

        interest_rate = self._estimate_interest_rate(credit_score)
        max_home_price = self._calculate_max_loan(max_monthly_payment, interest_rate, 30)

        market_stats = self.get_market_stats(zip_code=zip_code)
        median_price = market_stats["market_summary"]["median_price"]

        return {
            "summary": {
                "max_home_price": round(max_home_price, 2),
                "max_monthly_payment": round(max_monthly_payment, 2),
                "estimated_rate": round(interest_rate * 100, 2)
            },
            "market_position": {
                "vs_median": round((max_home_price / median_price - 1) * 100, 2),
                "affordable_range": f"${round(max_home_price * 0.9 / 1000)}k - ${round(max_home_price / 1000)}k"
            },
            "recommendations": self._generate_affordability_recommendation(
                max_home_price, median_price, credit_score
            )
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