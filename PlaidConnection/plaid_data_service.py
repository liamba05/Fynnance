"""
Service module for retrieving Plaid data.
This module contains all the functions for fetching specific data from Plaid,
using the credentials manager and session management from the API.
"""

from plaid.api import plaid_api
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.liabilities_get_request import LiabilitiesGetRequest
from .plaid_credentials_manager import PlaidCredentialsManager
from flask import session
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional, Any
import numpy as np
from collections import defaultdict

# Initialize the credentials manager (Singleton)
credentials_manager = PlaidCredentialsManager()

def _calculate_loan_predictions(loan: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Calculate loan payoff predictions and scenarios.
    
    Args:
        loan: Dictionary containing loan details with at least:
             - current_balance
             - interest_rate
             - minimum_payment
    
    Returns:
        Dictionary containing payoff predictions and scenarios, or None if required data is missing
    """
    current_balance = loan.get('current_balance')
    interest_rate = loan.get('interest_rate')
    minimum_payment = loan.get('minimum_payment')
    
    if not all([current_balance, interest_rate, minimum_payment]):
        return None
    
    try:
        # Calculate amortization schedule
        monthly_rate = interest_rate / 12 / 100
        
        # Handle edge cases where the minimum payment might be too low
        payment_to_interest = minimum_payment / (current_balance * monthly_rate)
        if payment_to_interest <= 1:
            return {
                'error': 'Minimum payment too low to pay off loan',
                'minimum_required': round(current_balance * monthly_rate + 100, 2)  # Add buffer for principal
            }
        
        # Calculate remaining payments
        remaining_payments = np.log(minimum_payment / (minimum_payment - current_balance * monthly_rate)) / np.log(1 + monthly_rate)
        remaining_payments = int(np.ceil(remaining_payments))
        
        total_to_pay = minimum_payment * remaining_payments
        total_interest = total_to_pay - current_balance
        
        # Calculate accelerated payoff scenarios
        accelerated_scenarios = []
        for additional_amount in [100, 200, 500]:
            new_payment = minimum_payment + additional_amount
            new_remaining_payments = np.log(new_payment / (new_payment - current_balance * monthly_rate)) / np.log(1 + monthly_rate)
            new_remaining_payments = int(np.ceil(new_remaining_payments))
            
            new_total = new_payment * new_remaining_payments
            interest_savings = total_to_pay - new_total
            
            accelerated_scenarios.append({
                'additional_monthly': additional_amount,
                'new_payment': new_payment,
                'new_payoff_date': (datetime.now() + timedelta(days=30 * new_remaining_payments)).date().isoformat(),
                'months_saved': remaining_payments - new_remaining_payments,
                'interest_savings': interest_savings,
                'total_to_pay': new_total
            })
        
        return {
            'total_to_pay': total_to_pay,
            'total_interest': total_interest,
            'payoff_date': (datetime.now() + timedelta(days=30 * remaining_payments)).date().isoformat(),
            'monthly_payment': minimum_payment,
            'remaining_payments': remaining_payments,
            'monthly_interest': current_balance * monthly_rate,
            'monthly_principal': minimum_payment - (current_balance * monthly_rate),
            'accelerated_payoff': accelerated_scenarios
        }
        
    except Exception as e:
        return {
            'error': f'Error calculating predictions: {str(e)}',
            'current_balance': current_balance,
            'interest_rate': interest_rate,
            'minimum_payment': minimum_payment
        }

def _analyze_recurring_transactions(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze transactions to identify recurring payment patterns.
    
    Args:
        transactions: List of transaction dictionaries with at least:
                     - date
                     - amount
                     - name/merchant_name
                     - category
    
    Returns:
        Dictionary containing recurring payment analysis
    """
    # Group transactions by merchant/description
    merchant_transactions = defaultdict(list)
    for transaction in transactions:
        key = transaction.get('merchant_name') or transaction['name']
        merchant_transactions[key].append({
            'date': datetime.strptime(transaction['date'], '%Y-%m-%d'),
            'amount': abs(transaction['amount']),  # Use absolute value for consistency
            'category': transaction.get('category', ['uncategorized'])[0]
        })
    
    recurring_payments = []
    for merchant, trans in merchant_transactions.items():
        if len(trans) < 2:  # Need at least 2 transactions to detect pattern
            continue
        
        # Sort transactions by date
        trans.sort(key=lambda x: x['date'])
        
        # Check for consistent amount
        amounts = [t['amount'] for t in trans]
        amount_mean = np.mean(amounts)
        amount_std = np.std(amounts)
        amount_variance = amount_std / amount_mean if amount_mean > 0 else float('inf')
        
        # Check for regular intervals
        intervals = [(trans[i+1]['date'] - trans[i]['date']).days for i in range(len(trans)-1)]
        if not intervals:
            continue
            
        interval_mean = np.mean(intervals)
        interval_std = np.std(intervals)
        interval_variance = interval_std / interval_mean if interval_mean > 0 else float('inf')
        
        # Determine if recurring based on consistency thresholds
        if amount_variance < 0.1 and interval_variance < 0.3:  # Adjust thresholds as needed
            # Determine frequency based on average interval
            avg_interval = np.mean(intervals)
            frequency = (
                'monthly' if 25 <= avg_interval <= 35 else
                'weekly' if 5 <= avg_interval <= 9 else
                'biweekly' if 12 <= avg_interval <= 16 else
                'quarterly' if 85 <= avg_interval <= 95 else
                'unknown'
            )
            
            # Calculate confidence score based on:
            # - Amount consistency
            # - Interval consistency
            # - Number of occurrences (more occurrences = higher confidence)
            # - Recent activity (more recent = higher confidence)
            amount_confidence = 1 - min(amount_variance, 1)
            interval_confidence = 1 - min(interval_variance, 1)
            occurrence_confidence = min(len(trans) / 12, 1)  # Max out at 12 occurrences
            
            days_since_last = (datetime.now().date() - trans[-1]['date'].date()).days
            recency_confidence = max(0, 1 - (days_since_last / 180))  # Decay over 6 months
            
            confidence = (
                amount_confidence * 0.4 +
                interval_confidence * 0.3 +
                occurrence_confidence * 0.2 +
                recency_confidence * 0.1
            )
            
            # Predict next payment date
            last_date = trans[-1]['date']
            next_payment = last_date + timedelta(days=round(avg_interval))
            
            recurring_payments.append({
                'name': merchant,
                'amount': round(amount_mean, 2),
                'frequency': frequency,
                'category': trans[0]['category'],
                'last_payment': last_date.date().isoformat(),
                'next_payment': next_payment.date().isoformat(),
                'confidence': round(confidence, 3),
                'occurrences': len(trans),
                'average_interval_days': round(avg_interval, 1),
                'amount_consistency': round(amount_confidence, 3),
                'timing_consistency': round(interval_confidence, 3),
                'payment_history': [
                    {
                        'date': t['date'].date().isoformat(),
                        'amount': round(t['amount'], 2)
                    }
                    for t in trans[-3:]  # Include last 3 payments
                ]
            })
    
    # Sort by confidence
    recurring_payments.sort(key=lambda x: x['confidence'], reverse=True)
    
    # Calculate category summaries
    category_totals = defaultdict(float)
    for payment in recurring_payments:
        if payment['confidence'] >= 0.7:  # Only include high-confidence payments
            category_totals[payment['category']] += payment['amount']
    
    total_monthly = sum(
        p['amount'] * (30 / p['average_interval_days'])
        for p in recurring_payments
        if p['confidence'] >= 0.7
    )
    
    return {
        'recurring_payments': recurring_payments,
        'summary': {
            'total_monthly_recurring': round(total_monthly, 2),
            'total_payments_detected': len(recurring_payments),
            'high_confidence_payments': len([p for p in recurring_payments if p['confidence'] >= 0.7]),
            'categories': {
                category: {
                    'monthly_total': round(amount, 2),
                    'percentage': round(amount / sum(category_totals.values()) * 100, 1) if category_totals else 0
                }
                for category, amount in category_totals.items()
            }
        }
    }

def get_current_user_id() -> str:
    """Get the current user's Firebase Auth UID from the session."""
    if 'firebase_user_id' not in session:
        raise ValueError("No authenticated Firebase user found in session")
    return session['firebase_user_id']

def get_plaid_data(func):
    """
    Decorator to handle common Plaid data retrieval patterns:
    - Gets Firebase Auth UID from session
    - Gets access token
    - Creates Plaid client
    - Handles common exceptions
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Get current user's Firebase Auth UID from session
            firebase_user_id = get_current_user_id()
            
            # Get user's access token
            result = credentials_manager.get_user_access_token(firebase_user_id)
            if not result:
                raise ValueError("No Plaid access token found for user")
            
            access_token, item_id = result
            
            # Create Plaid client using credentials manager
            plaid_client = credentials_manager.create_plaid_client()
            
            # Call the actual function with the prepared data
            return func(plaid_client=plaid_client, access_token=access_token, *args, **kwargs)
            
        except ValueError as e:
            # Handle expected errors (like missing tokens)
            raise ValueError(f"Error getting Plaid data: {str(e)}")
        except Exception as e:
            # Handle unexpected errors
            raise Exception(f"Unexpected error getting Plaid data: {str(e)}")
    
    return wrapper

@get_plaid_data
def get_investment_holdings(plaid_client: plaid_api.PlaidApi, access_token: str) -> Dict[str, Any]:
    """
    Get all investment holdings for the current user.
    Returns a dictionary containing accounts, holdings, and securities information.
    """
    try:
        # Make the holdings request
        request = InvestmentsHoldingsGetRequest(access_token=access_token)
        response = plaid_client.investments_holdings_get(request)
        
        # Format the response
        result = {
            'accounts': [],
            'holdings': [],
            'securities': []
        }
        
        # Format accounts
        for account in response['accounts']:
            if account['type'] == 'investment':
                result['accounts'].append({
                    'account_id': account['account_id'],
                    'name': account['name'],
                    'subtype': account['subtype'],
                    'current_balance': account['balances']['current'],
                    'mask': account.get('mask'),
                    'official_name': account.get('official_name')
                })
        
        # Format holdings
        for holding in response['holdings']:
            formatted_holding = {
                'account_id': holding['account_id'],
                'security_id': holding['security_id'],
                'quantity': holding['quantity'],
                'cost_basis': holding.get('cost_basis'),
                'institution_value': holding['institution_value'],
                'institution_price': holding['institution_price'],
                'currency_code': holding.get('iso_currency_code', 'USD')
            }
            result['holdings'].append(formatted_holding)
        
        # Format securities
        for security in response['securities']:
            formatted_security = {
                'security_id': security['security_id'],
                'name': security['name'],
                'ticker_symbol': security.get('ticker_symbol'),
                'type': security['type'],
                'close_price': security.get('close_price'),
                'close_price_as_of': security.get('close_price_as_of'),
                'currency_code': security.get('iso_currency_code', 'USD')
            }
            result['securities'].append(formatted_security)
        
        return result
        
    except Exception as e:
        if 'NO_INVESTMENT_ACCOUNTS' in str(e):
            return {
                'accounts': [],
                'holdings': [],
                'securities': [],
                'error': 'NO_INVESTMENT_ACCOUNTS',
                'message': 'User has no connected investment accounts.'
            }
        raise

@get_plaid_data
def get_account_balances(plaid_client: plaid_api.PlaidApi, access_token: str) -> List[Dict[str, Any]]:
    """Get all account balances for the current user."""
    request = AccountsGetRequest(access_token=access_token)
    response = plaid_client.accounts_get(request)
    
    return [{
        'account_id': account['account_id'],
        'name': account['name'],
        'type': account['type'],
        'subtype': account['subtype'],
        'current_balance': account['balances']['current'],
        'available_balance': account['balances'].get('available'),
        'currency_code': account['balances'].get('iso_currency_code', 'USD'),
        'mask': account.get('mask'),
        'official_name': account.get('official_name')
    } for account in response['accounts']]

@get_plaid_data
def get_transactions(
    plaid_client: plaid_api.PlaidApi, 
    access_token: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """Get transactions for the current user within the specified date range."""
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).date()
    if not end_date:
        end_date = datetime.now().date()
        
    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date
    )
    response = plaid_client.transactions_get(request)
    
    return [{
        'transaction_id': transaction['transaction_id'],
        'account_id': transaction['account_id'],
        'date': transaction['date'],
        'name': transaction['name'],
        'amount': transaction['amount'],
        'currency_code': transaction.get('iso_currency_code', 'USD'),
        'category': transaction.get('category', []),
        'category_id': transaction.get('category_id'),
        'pending': transaction['pending'],
        'merchant_name': transaction.get('merchant_name'),
        'payment_channel': transaction.get('payment_channel'),
        'authorized_date': transaction.get('authorized_date')
    } for transaction in response['transactions']]

@get_plaid_data
def get_recurring_payments(
    plaid_client: plaid_api.PlaidApi, 
    access_token: str,
    lookback_days: int = 180
) -> Dict[str, Any]:
    """
    Analyze transaction history to identify and categorize recurring payments.
    Returns structured data about payment patterns.
    
    Args:
        plaid_client: The Plaid API client
        access_token: The user's access token
        lookback_days: Number of days to analyze for patterns (default: 180)
    
    Returns:
        Dictionary containing recurring payment analysis
    """
    try:
        # Get transaction history
        start_date = (datetime.now() - timedelta(days=lookback_days))
        transactions = get_transactions(
            plaid_client=plaid_client,
            access_token=access_token,
            start_date=start_date
        )
        
        # Analyze recurring patterns
        recurring_analysis = _analyze_recurring_transactions(transactions)
        
        return {
            **recurring_analysis,
            'metadata': {
                'analysis_period_days': lookback_days,
                'start_date': start_date.date().isoformat(),
                'end_date': datetime.now().date().isoformat(),
                'generated_at': datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise Exception(f"Error analyzing recurring payments: {str(e)}")

@get_plaid_data
def get_mortgage_data(plaid_client: plaid_api.PlaidApi, access_token: str) -> Dict[str, Any]:
    """Get mortgage-specific liability data with payoff predictions for the current user."""
    try:
        request = LiabilitiesGetRequest(access_token=access_token)
        response = plaid_client.liabilities_get(request)
        
        if 'mortgage' not in response['liabilities']:
            return {
                'has_mortgage': False,
                'mortgages': [],
                'message': 'No mortgage accounts found.'
            }
        
        mortgages = response['liabilities']['mortgage']
        mortgage_accounts = [
            acc for acc in response['accounts'] 
            if acc['account_id'] in [m['account_id'] for m in mortgages]
        ]
        
        formatted_mortgages = []
        predictions = []
        for mortgage in mortgages:
            formatted_mortgage = {
                'account_id': mortgage['account_id'],
                'account_number': mortgage.get('account_number'),
                'current_balance': mortgage.get('current_balance'),
                'original_principal': mortgage.get('origination_principal_amount'),
                'loan_term': mortgage.get('loan_term'),
                'interest_rate': mortgage.get('interest_rate', {}).get('percentage'),
                'last_payment_amount': mortgage.get('last_payment_amount'),
                'last_payment_date': mortgage.get('last_payment_date'),
                'next_payment_due_date': mortgage.get('next_monthly_payment_due_date'),
                'next_payment_amount': mortgage.get('next_monthly_payment'),
                'maturity_date': mortgage.get('maturity_date'),
                'property_address': mortgage.get('property_address'),
                'has_pmi': mortgage.get('has_pmi', False),
                'has_escrow': mortgage.get('has_escrow', False),
                'loan_type': mortgage.get('loan_type'),
                'origination_date': mortgage.get('origination_date'),
                'minimum_payment': mortgage.get('next_monthly_payment')  # For prediction calculation
            }
            
            # Add payoff predictions
            prediction = _calculate_loan_predictions(formatted_mortgage)
            if prediction:
                formatted_mortgage['payoff_predictions'] = prediction
                predictions.append({
                    'mortgage_id': formatted_mortgage['account_id'],
                    'predictions': prediction
                })
            
            formatted_mortgages.append(formatted_mortgage)
        
        return {
            'has_mortgage': True,
            'mortgages': formatted_mortgages,
            'accounts': mortgage_accounts,
            'total_mortgage_balance': sum(m.get('current_balance', 0) for m in formatted_mortgages),
            'payoff_analysis': {
                'total_to_pay': sum(p['predictions']['total_to_pay'] for p in predictions),
                'total_interest': sum(p['predictions']['total_interest'] for p in predictions),
                'average_interest_rate': sum(m['interest_rate'] for m in formatted_mortgages if m.get('interest_rate')) / 
                                      len([m for m in formatted_mortgages if m.get('interest_rate')]) if formatted_mortgages else 0,
                'total_monthly_payments': sum(m.get('next_payment_amount', 0) for m in formatted_mortgages)
            } if predictions else None
        }
        
    except Exception as e:
        if 'NO_LIABILITY_ACCOUNTS' in str(e):
            return {
                'has_mortgage': False,
                'mortgages': [],
                'message': 'No mortgage accounts found.'
            }
        raise

@get_plaid_data
def get_credit_data(plaid_client: plaid_api.PlaidApi, access_token: str) -> Dict[str, Any]:
    """Get credit card-specific liability data for the current user."""
    try:
        request = LiabilitiesGetRequest(access_token=access_token)
        response = plaid_client.liabilities_get(request)
        
        if 'credit' not in response['liabilities']:
            return {
                'has_credit_cards': False,
                'credit_cards': [],
                'message': 'No credit card accounts found.'
            }
        
        credit_cards = response['liabilities']['credit']
        credit_accounts = [
            acc for acc in response['accounts'] 
            if acc['account_id'] in [c['account_id'] for c in credit_cards]
        ]
        
        formatted_cards = []
        for card in credit_cards:
            formatted_card = {
                'account_id': card['account_id'],
                'name': next((acc['name'] for acc in credit_accounts if acc['account_id'] == card['account_id']), None),
                'last_statement_balance': card.get('last_statement_balance'),
                'current_balance': card.get('current_balance'),
                'last_payment_amount': card.get('last_payment_amount'),
                'last_payment_date': card.get('last_payment_date'),
                'next_payment_due_date': card.get('next_payment_due_date'),
                'minimum_payment': card.get('minimum_payment_amount'),
                'credit_limit': card.get('credit_limit'),
                'interest_rates': [
                    {
                        'type': apr['apr_type'],
                        'rate': apr['apr_percentage'],
                        'balance_subject': apr.get('balance_subject_to_apr', 0)
                    }
                    for apr in card.get('aprs', [])
                ],
                'is_overdue': card.get('is_overdue', False)
            }
            formatted_cards.append(formatted_card)
        
        return {
            'has_credit_cards': True,
            'credit_cards': formatted_cards,
            'accounts': credit_accounts,
            'summary': {
                'total_credit_used': sum(c.get('current_balance', 0) for c in formatted_cards),
                'total_credit_limit': sum(c.get('credit_limit', 0) for c in formatted_cards),
                'total_minimum_payments': sum(c.get('minimum_payment', 0) for c in formatted_cards),
                'utilization_rate': sum(c.get('current_balance', 0) for c in formatted_cards) / 
                                  sum(c.get('credit_limit', 1) for c in formatted_cards) * 100
                                  if any(c.get('credit_limit', 0) > 0 for c in formatted_cards) else 0
            }
        }
        
    except Exception as e:
        if 'NO_LIABILITY_ACCOUNTS' in str(e):
            return {
                'has_credit_cards': False,
                'credit_cards': [],
                'message': 'No credit card accounts found.'
            }
        raise

@get_plaid_data
def get_loan_data(plaid_client: plaid_api.PlaidApi, access_token: str) -> Dict[str, Any]:
    """Get loan/debt-specific liability data (excluding mortgages) for the current user."""
    try:
        request = LiabilitiesGetRequest(access_token=access_token)
        response = plaid_client.liabilities_get(request)
        
        if 'student' not in response['liabilities'] and 'loan' not in response.get('liabilities', {}):
            return {
                'has_loans': False,
                'loans': [],
                'message': 'No loan accounts found.'
            }
        
        # Combine student loans and other loans
        student_loans = response['liabilities'].get('student', [])
        other_loans = response['liabilities'].get('loan', [])
        all_loans = student_loans + other_loans
        
        loan_accounts = [
            acc for acc in response['accounts'] 
            if acc['account_id'] in [l['account_id'] for l in all_loans]
        ]
        
        formatted_loans = []
        for loan in all_loans:
            formatted_loan = {
                'account_id': loan['account_id'],
                'name': next((acc['name'] for acc in loan_accounts if acc['account_id'] == loan['account_id']), None),
                'loan_type': 'student' if loan in student_loans else 'personal',
                'current_balance': loan.get('outstanding_principal_balance', loan.get('current_balance')),
                'original_principal': loan.get('origination_principal_amount'),
                'interest_rate': loan.get('interest_rate_percentage'),
                'last_payment_amount': loan.get('last_payment_amount'),
                'last_payment_date': loan.get('last_payment_date'),
                'next_payment_due_date': loan.get('next_payment_due_date'),
                'minimum_payment': loan.get('minimum_payment_amount'),
                'loan_status': loan.get('loan_status', {}).get('type'),
                'origination_date': loan.get('origination_date'),
                'expected_payoff_date': loan.get('expected_payoff_date'),
                'payment_history': loan.get('payment_history', []),
                'guarantor': loan.get('guarantor'),
                'is_overdue': loan.get('is_overdue', False)
            }
            
            # Add student loan specific fields
            if loan in student_loans:
                formatted_loan.update({
                    'repayment_plan': loan.get('repayment_plan', {}).get('type'),
                    'repayment_plan_description': loan.get('repayment_plan', {}).get('description'),
                    'servicer_address': loan.get('servicer_address'),
                    'is_federal': loan.get('is_federal', None)
                })
            
            formatted_loans.append(formatted_loan)
        
        return {
            'has_loans': True,
            'loans': formatted_loans,
            'accounts': loan_accounts,
            'summary': {
                'total_loan_balance': sum(l.get('current_balance', 0) for l in formatted_loans),
                'total_minimum_payments': sum(l.get('minimum_payment', 0) for l in formatted_loans),
                'loans_by_type': {
                    'student': len([l for l in formatted_loans if l['loan_type'] == 'student']),
                    'personal': len([l for l in formatted_loans if l['loan_type'] == 'personal'])
                },
                'federal_loans': len([l for l in formatted_loans if l.get('is_federal', False)]),
                'private_loans': len([l for l in formatted_loans if l.get('is_federal') is False])
            }
        }
        
    except Exception as e:
        if 'NO_LIABILITY_ACCOUNTS' in str(e):
            return {
                'has_loans': False,
                'loans': [],
                'message': 'No loan accounts found.'
            }
        raise

@get_plaid_data
def get_liabilities(plaid_client: plaid_api.PlaidApi, access_token: str) -> Dict[str, Any]:
    """Get all liabilities for the current user, organized by type."""
    try:
        # Get all liability types
        mortgages = get_mortgage_data(plaid_client=plaid_client, access_token=access_token)
        credit_cards = get_credit_data(plaid_client=plaid_client, access_token=access_token)
        loans = get_loan_data(plaid_client=plaid_client, access_token=access_token)
        
        # Calculate total debt
        total_debt = (
            mortgages.get('total_mortgage_balance', 0) +
            credit_cards.get('summary', {}).get('total_credit_used', 0) +
            loans.get('summary', {}).get('total_loan_balance', 0)
        )
        
        # Calculate total minimum payments
        total_minimum_payments = (
            sum(m.get('next_payment_amount', 0) for m in mortgages.get('mortgages', [])) +
            credit_cards.get('summary', {}).get('total_minimum_payments', 0) +
            loans.get('summary', {}).get('total_minimum_payments', 0)
        )
        
        return {
            'summary': {
                'total_debt': total_debt,
                'total_minimum_payments': total_minimum_payments,
                'has_mortgages': mortgages['has_mortgage'],
                'has_credit_cards': credit_cards['has_credit_cards'],
                'has_loans': loans['has_loans']
            },
            'mortgages': mortgages,
            'credit_cards': credit_cards,
            'loans': loans
        }
        
    except Exception as e:
        if 'NO_LIABILITY_ACCOUNTS' in str(e):
            return {
                'summary': {
                    'total_debt': 0,
                    'total_minimum_payments': 0,
                    'has_mortgages': False,
                    'has_credit_cards': False,
                    'has_loans': False
                },
                'mortgages': {'has_mortgage': False, 'mortgages': []},
                'credit_cards': {'has_credit_cards': False, 'credit_cards': []},
                'loans': {'has_loans': False, 'loans': []},
                'error': 'NO_LIABILITY_ACCOUNTS',
                'message': 'User has no connected liability accounts.'
            }
        raise

@get_plaid_data
def get_user_financial_profile(
    plaid_client: plaid_api.PlaidApi, 
    access_token: str,
    transactions_days: int = 30
) -> Dict[str, Any]:
    """
    Get a comprehensive financial profile for the current user.
    Aggregates all available financial data into a single structured response.
    
    Args:
        plaid_client: The Plaid API client
        access_token: The user's access token
        transactions_days: Number of days of transaction history to include (default: 30)
    
    Returns:
        A dictionary containing all user financial data structured by category
    """
    try:
        # Get all data concurrently (if using async in the future)
        accounts = get_account_balances(plaid_client=plaid_client, access_token=access_token)
        holdings = get_investment_holdings(plaid_client=plaid_client, access_token=access_token)
        start_date = (datetime.now() - timedelta(days=transactions_days))
        transactions = get_transactions(
            plaid_client=plaid_client, 
            access_token=access_token,
            start_date=start_date
        )
        liabilities = get_liabilities(plaid_client=plaid_client, access_token=access_token)

        # Calculate summary statistics
        total_balances = {
            'checking': sum(acct['current_balance'] for acct in accounts if acct['type'] == 'depository' and acct['subtype'] == 'checking'),
            'savings': sum(acct['current_balance'] for acct in accounts if acct['type'] == 'depository' and acct['subtype'] == 'savings'),
            'investment': sum(acct['current_balance'] for acct in accounts if acct['type'] == 'investment'),
            'credit': sum(acct['current_balance'] for acct in accounts if acct['type'] == 'credit'),
            'loan': sum(acct['current_balance'] for acct in accounts if acct['type'] == 'loan'),
        }

        # Calculate investment summary if available
        investment_summary = None
        if holdings and 'holdings' in holdings and holdings['holdings']:
            investment_summary = {
                'total_investment_value': sum(holding['institution_value'] for holding in holdings['holdings']),
                'total_securities': len(holdings['securities']),
                'total_holdings': len(holdings['holdings']),
                'accounts': len(holdings['accounts']),
            }

        # Process transactions
        recent_transactions = transactions[:min(len(transactions), 10)]  # Last 10 transactions
        transaction_summary = {
            'total_transactions': len(transactions),
            'total_spend': sum(t['amount'] for t in transactions if t['amount'] > 0),
            'total_income': abs(sum(t['amount'] for t in transactions if t['amount'] < 0)),
            'categories': {}
        }
        
        # Summarize transactions by category
        for transaction in transactions:
            category = transaction.get('category', ['uncategorized'])[0]
            if category not in transaction_summary['categories']:
                transaction_summary['categories'][category] = {
                    'count': 0,
                    'total_amount': 0
                }
            transaction_summary['categories'][category]['count'] += 1
            transaction_summary['categories'][category]['total_amount'] += transaction['amount']

        # Structure the comprehensive response
        return {
            'summary': {
                'total_balances': total_balances,
                'net_worth': (
                    total_balances['checking'] + 
                    total_balances['savings'] + 
                    total_balances['investment'] - 
                    total_balances['credit'] - 
                    total_balances['loan']
                ),
                'accounts_summary': {
                    'total_accounts': len(accounts),
                    'accounts_by_type': {
                        account_type: len([a for a in accounts if a['type'] == account_type])
                        for account_type in set(account['type'] for account in accounts)
                    }
                }
            },
            'accounts': {
                'all_accounts': accounts,
                'by_type': {
                    account_type: [a for a in accounts if a['type'] == account_type]
                    for account_type in set(account['type'] for account in accounts)
                }
            },
            'investments': {
                'summary': investment_summary,
                'details': holdings if holdings and not holdings.get('error') else None
            },
            'transactions': {
                'summary': transaction_summary,
                'recent_transactions': recent_transactions
            },
            'liabilities': {
                'summary': {
                    'has_liabilities': bool(liabilities and not liabilities.get('error')),
                    'types_present': list(liabilities.get('liabilities', {}).keys()) if liabilities and not liabilities.get('error') else []
                },
                'details': liabilities if liabilities and not liabilities.get('error') else None
            },
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'transactions_days_included': transactions_days
            }
        }
        
    except Exception as e:
        raise Exception(f"Error generating user financial profile: {str(e)}") 