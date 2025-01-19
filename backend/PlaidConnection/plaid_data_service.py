"""
Service module for retrieving Plaid data.
This module contains all the functions for fetching specific data from Plaid,
using the credentials manager and session management from the API.
"""

from plaid.api import plaid_api
from plaid.api_client import ApiClient
from plaid.configuration import Configuration
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.liabilities_get_request import LiabilitiesGetRequest
from plaid_credentials_manager import PlaidCredentialsManager
from flask import session
from datetime import datetime, timedelta, date
from functools import wraps
from typing import Dict, List, Optional, Any
import numpy as np
from collections import defaultdict
import time

# Initialize the credentials manager (Singleton)
credentials_manager = PlaidCredentialsManager()

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
    """Decorator to handle common patterns for retrieving Plaid data."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Get current user's Firebase Auth UID from session
            firebase_user_id = get_current_user_id()
            
            # Get user's access token if not provided
            if 'access_token' not in kwargs:
                result = credentials_manager.get_user_access_token(firebase_user_id)
                if not result:
                    raise ValueError("No Plaid access token found for user")
                access_token, item_id = result
                kwargs['access_token'] = access_token
            
            # Get Plaid client if not provided
            if 'plaid_client' not in kwargs:
                kwargs['plaid_client'] = credentials_manager.create_plaid_client()
            
            # Call the actual function with the prepared data
            return func(*args, **kwargs)
            
        except ValueError as e:
            # Handle expected errors (like missing tokens)
            raise ValueError(f"Error getting Plaid data: {str(e)}")
        except Exception as e:
            # Handle unexpected errors
            raise Exception(f"Unexpected error getting Plaid data: {str(e)}")
    
    return wrapper

@get_plaid_data
def get_account_balances(plaid_client: plaid_api.PlaidApi, access_token: str) -> List[Dict[str, Any]]:
    """Get all account balances for the current user."""
    request = AccountsGetRequest(access_token=access_token)
    response = plaid_client.accounts_get(request)
    
    return [{
        'name': account['name'],
        'type': str(account['type']).lower(),
        'balance': account['balances']['current']
    } for account in response['accounts']]

@get_plaid_data
def get_investment_holdings(plaid_client: plaid_api.PlaidApi, access_token: str) -> Dict[str, Any]:
    """Get investment holdings data for the current user."""
    try:
        request = InvestmentsHoldingsGetRequest(access_token=access_token)
        response = plaid_client.investments_holdings_get(request)
        
        # Create a lookup for securities by ID
        securities = {s['security_id']: s for s in response['securities']}
        
        # Format holdings with security details
        formatted_holdings = []
        for holding in response['holdings']:
            security = securities.get(holding['security_id'], {})
            cost_basis = holding.get('cost_basis', 0)
            value = holding.get('institution_value', 0)
            gain_loss = value - cost_basis if cost_basis and value else 0
            gain_loss_pct = (gain_loss / cost_basis * 100) if cost_basis else 0
            
            formatted_holding = {
                'name': security.get('name', 'Unknown'),
                'ticker': security.get('ticker_symbol', 'None'),
                'type': security.get('type', 'unknown'),
                'quantity': holding['quantity'],
                'price': holding['institution_price'],
                'value': value,
                'gain_loss': gain_loss,
                'gain_loss_pct': gain_loss_pct
            }
            formatted_holdings.append(formatted_holding)
            
        return {
            'accounts': [{'name': acc['name'], 'type': acc['type']} for acc in response['accounts']],
            'holdings': sorted(formatted_holdings, key=lambda x: x['value'], reverse=True)
        }
        
    except Exception as e:
        return {
            'accounts': [],
            'holdings': [],
            'error': str(e)
        }

@get_plaid_data
def get_transactions(plaid_client: plaid_api.PlaidApi, access_token: str, start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
    """Get transaction data for the current user."""
    time.sleep(3)
    try:
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()
            
        start_date = start_date.date() if isinstance(start_date, datetime) else start_date
        end_date = end_date.date() if isinstance(end_date, datetime) else end_date
        
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options={"include_personal_finance_category": True}
        )
        
        response = plaid_client.transactions_get(request)
        
        return [{
            'date': trans['date'],
            'name': trans['name'],
            'amount': trans['amount'],
            'category': trans.get('category', []),
            'merchant_name': trans.get('merchant_name')
        } for trans in response.get('transactions', [])]
        
    except Exception as e:
        raise Exception(f"Error getting transactions: {str(e)}")

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
def get_liabilities(plaid_client: plaid_api.PlaidApi, access_token: str) -> Dict[str, Any]:
    """Get liability data including credit cards, student loans, and mortgages."""
    try:
        request = LiabilitiesGetRequest(access_token=access_token)
        response = plaid_client.liabilities_get(request)
        
        # Format response similar to plaid_test.py
        liabilities = response['liabilities']
        formatted_response = {}
        
        if 'credit' in liabilities:
            credit_responses = []
            credit_accounts = [acc for acc in response['accounts'] if acc['type'] == 'credit']
            
            for credit in liabilities['credit']:
                # Find matching account
                account = next((acc for acc in credit_accounts 
                              if acc['account_id'] == credit['account_id']), None)
                
                subresponse = {}
                if account:
                    subresponse['name'] = account['name']
                else:
                    subresponse['name'] = f"Credit Card (ID: {credit['account_id']})"
                    
                subresponse['last_statement_balance'] = f"${credit['last_statement_balance']:,.2f}"
                if 'last_payment_amount' in credit:
                    subresponse['last_payment_amount'] = f"${credit['last_payment_amount']:,.2f}"
                if 'minimum_payment_amount' in credit:
                    subresponse['minimum_payment_amount'] = f"${credit['minimum_payment_amount']:,.2f}"
                if 'is_overdue' in credit:
                    subresponse['is_overdue'] = credit['is_overdue']
                
                # Show only the purchase APR (main interest rate)
                purchase_apr = next((apr for apr in credit['aprs'] 
                                   if apr['apr_type'] == 'purchase_apr'), None)
                if purchase_apr:
                    subresponse['purchase_apr'] = f"{purchase_apr['apr_percentage']}%"
                    subresponse['balance_subject_to_apr'] = f"${purchase_apr['balance_subject_to_apr']:,.2f}"
                
                credit_responses.append(subresponse)
        else:
            credit_responses = [{'name': "No Credit Accounts"}]
        formatted_response['credit_cards'] = credit_responses

        if 'student' in liabilities:
            student_responses = []
            for loan in liabilities['student']:
                account = next((acc for acc in response['accounts'] 
                              if acc['account_id'] == loan['account_id']), None)
                account_name = account['name'] if account else loan['account_id']
                
                subresponse = {
                    'name': account_name,
                    'last_statement_balance': f"${loan['last_statement_balance']:,.2f}"
                }
                
                if 'last_payment_amount' in loan:
                    subresponse['last_payment_amount'] = f"${loan['last_payment_amount']:,.2f}"
                if 'minimum_payment_amount' in loan:
                    subresponse['minimum_payment_amount'] = f"${loan['minimum_payment_amount']:,.2f}"
                if 'loan_status' in loan:
                    subresponse['loan_status'] = loan['loan_status']['type']
                if 'interest_rate_percentage' in loan:
                    subresponse['interest_rate_percentage'] = f"{loan['interest_rate_percentage']}%"
                if 'expected_payoff_date' in loan:
                    subresponse['expected_payoff_date'] = loan['expected_payoff_date']
                if 'origination_principal_amount' in loan:
                    subresponse['origination_principal_amount'] = f"${loan['origination_principal_amount']:,.2f}"
                
                student_responses.append(subresponse)
        else:
            student_responses = [{'name': "No Student Loans"}]
        formatted_response['student_loans'] = student_responses

        if 'mortgage' in liabilities:
            mortgage_responses = []
            for mortgage in liabilities['mortgage']:
                account = next((acc for acc in response['accounts'] 
                              if acc['account_id'] == mortgage['account_id']), None)
                account_name = account['name'] if account else mortgage['account_id']
                
                subresponse = {
                    'name': account_name
                }
                
                if 'outstanding_principal_balance' in mortgage:
                    subresponse['outstanding_principal_balance'] = f"${mortgage['outstanding_principal_balance']:,.2f}"
                if 'last_payment_amount' in mortgage:
                    subresponse['last_payment_amount'] = f"${mortgage['last_payment_amount']:,.2f}"
                if 'last_payment_date' in mortgage:
                    subresponse['last_payment_date'] = mortgage['last_payment_date']
                if 'loan_term' in mortgage:
                    subresponse['loan_term'] = mortgage['loan_term']
                if 'interest_rate' in mortgage and 'percentage' in mortgage['interest_rate']:
                    rate = mortgage['interest_rate']['percentage']
                    subresponse['interest_rate'] = f"{rate}%"
                    if 'origination_principal_amount' in mortgage:
                        principal = mortgage['origination_principal_amount']
                        subresponse['original_principal'] = f"${principal:,.2f}"
                        if rate and 'loan_term' in mortgage:
                            years = float(mortgage['loan_term'].split()[0])
                            monthly_rate = (rate/100) / 12
                            num_payments = years * 12
                            monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
                            total = monthly_payment * num_payments
                            subresponse['total_to_pay'] = f"${total:,.2f}"
                            subresponse['monthly_payment'] = f"${monthly_payment:,.2f}"
                
                mortgage_responses.append(subresponse)
        else:
            mortgage_responses = [{'name': "No Mortgages"}]
        formatted_response['mortgages'] = mortgage_responses
        
        return formatted_response
        
    except Exception as e:
        if hasattr(e, 'body') and isinstance(e.body, dict):
            error_message = e.body.get('error_message', str(e))
        else:
            error_message = str(e)
        return {
            'error': 'NO_LIABILITY_ACCOUNTS',
            'message': 'Either your bank does not support liabilities, or you do not have any liability accounts.',
            'true_message': error_message,
            'err': e
        }

@get_plaid_data
def get_user_financial_profile(transactions_days=30, **kwargs):
    """Get a comprehensive financial profile for the user."""
    try:
        # Get account balances
        accounts = get_account_balances(**kwargs)
        
        # Get transactions for the specified period
        start_date = datetime.now() - timedelta(days=transactions_days)
        transactions = get_transactions(start_date=start_date, **kwargs)
        
        # Get investment holdings
        investments = get_investment_holdings(**kwargs)
        
        # Get liabilities
        liabilities = get_liabilities(**kwargs)
        
        # Calculate totals by account type
        balances_by_type = defaultdict(float)
        for account in accounts:
            balances_by_type[str(account['type']).lower()] += account.get('balance', 0)
            
        # Calculate spending and income
        total_spending = sum(t['amount'] for t in transactions if t['amount'] > 0)
        total_income = abs(sum(t['amount'] for t in transactions if t['amount'] < 0))
        
        return {
            'accounts': accounts,
            'balances': dict(balances_by_type),
            'investments': investments.get('holdings', []),
            'liabilities': liabilities,
            'transactions': transactions,
            'summary': {
                'total_spending': total_spending,
                'total_income': total_income
            }
        }
        
    except Exception as e:
        raise Exception(f"Error generating user financial profile: {str(e)}") 