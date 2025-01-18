from plaid.api import plaid_api
from plaid import ApiClient
from plaid.configuration import Configuration
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.model.liabilities_get_request import LiabilitiesGetRequest
from datetime import datetime, timedelta
import time

class PlaidService:
    def __init__(self):
        self.client = self._create_plaid_client()
    
    def _create_plaid_client(self):
        """Initialize and return a Plaid API client."""
        configuration = Configuration(
            host="https://sandbox.plaid.com",
            api_key={
                'clientId': '678953cb559345002587ec7e',
                'secret': '1dc05827da8670928df83473315054'
            }
        )
        return plaid_api.PlaidApi(ApiClient(configuration))

    def create_link_token(self, user_id):
        """Create a link token for the given user."""
        request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=user_id),
            client_name="dummy",
            products=[
                Products("auth"),
                Products("transactions"),
                Products("investments"),
                Products("liabilities"),
            ],
            country_codes=[CountryCode('US')],
            language='en'
        )
        response = self.client.link_token_create(request)
        return response['link_token']

    def get_access_token(self, institution_id='ins_109508'):
        """
        Get an access token using the Sandbox environment.
        Default institution is 'Capital One' in Sandbox.
        """
        # Create a public token using the sandbox
        pt_request = SandboxPublicTokenCreateRequest(
            institution_id=institution_id,
            initial_products=[Products("auth"), Products("transactions")],
            # options={
            #     "override_username": "custom_fynn",
            #     "override_password": "asd"
            # },
        )
        pt_response = self.client.sandbox_public_token_create(pt_request)
        
        # Exchange public token for an access token
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=pt_response['public_token']
        )
        exchange_response = self.client.item_public_token_exchange(exchange_request)
        
        return exchange_response['access_token']

    def get_accounts(self, access_token):
        """Retrieve accounts for the given access token."""
        request = AccountsGetRequest(access_token=access_token)
        response = self.client.accounts_get(request)
        return response['accounts']

    def get_transactions(self, access_token, start_date=None, end_date=None):
        """Retrieve transactions for the given access token and date range."""
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).date()
        if not end_date:
            end_date = datetime.now().date()

        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date
        )
        response = self.client.transactions_get(request)
        return response['transactions']

    def get_investment_holdings(self, access_token):
        """Retrieve investment holdings and portfolio data."""
        try:
            request = InvestmentsHoldingsGetRequest(access_token=access_token)
            return self.client.investments_holdings_get(request)
        except Exception:
            # Simplify by treating all errors as NO_INVESTMENT_ACCOUNTS
            return {
                'error': 'NO_INVESTMENT_ACCOUNTS',
                'message': 'The user has no connected investment accounts.'
            }
        
    def get_liabilities(self, access_token):
        """Retrieve liability data including credit cards, student loans, and mortgages."""
        try:
            request = LiabilitiesGetRequest(access_token=access_token)
            response = self.client.liabilities_get(request)
            return {
                'accounts': response['accounts'],
                'liabilities': response['liabilities']
            }
        except Exception as e:
            if hasattr(e, 'body') and isinstance(e.body, dict):
                error_message = e.body.get('error_message', str(e))
            else:
                error_message = str(e)
            return {
                'error': 'NO_LIABILITY_ACCOUNTS',
                'message': 'No liability accounts found for this user.'
            }
        
def format_account_summary(account):
    return (f"- {account['name']} ({account['subtype']}): "
            f"${account['balances']['current']:,.2f}")

def format_holding_details(holding, security):
    # Extract holding details
    quantity = holding['quantity']
    institution_price = holding['institution_price']
    institution_value = holding['institution_value']
    cost_basis = holding.get('cost_basis')
    
    # Extract security details
    name = security['name']
    ticker = security.get('ticker_symbol', 'N/A')
    security_type = security['type']
    
    # Format gain/loss string if cost basis available
    gain_loss_str = format_gain_loss(cost_basis, quantity, institution_value) if cost_basis else ""
    
    return (f"- {name} ({ticker}) | {security_type}\n"
            f"  Quantity: {quantity:,.4f} @ ${institution_price:,.2f} = "
            f"${institution_value:,.2f}{gain_loss_str}")

def format_gain_loss(cost_basis, quantity, institution_value):
    gain_loss = institution_value - (cost_basis * quantity)
    gain_loss_pct = (gain_loss / (cost_basis * quantity)) * 100
    return f" | G/L: ${gain_loss:,.2f} ({gain_loss_pct:,.1f}%)"


def test_plaid_integration():
    """Run a comprehensive test of Plaid integration."""
    try:
        plaid = PlaidService()
        
        print("1. Testing link token creation...")
        link_token = plaid.create_link_token("test-user-id")
        print(f"Link token created: {link_token[:40]}...")

        print("\n2. Getting access token using sandbox mode...")
        access_token = plaid.get_access_token()
        print(f"Access token received: {access_token[:40]}...")

        print("\n3. Getting account details...")
        accounts = plaid.get_accounts(access_token)
        print(f"\nFound {len(accounts)} accounts:")
        for account in accounts:
            print(f"- {account['name']} ({account['type']}): ${account['balances']['current']}")

        time.sleep(3) # wait for transactions to be processed DO NOT REMOVE

        print("\n4. Retrieving recent transactions...")
        transactions = plaid.get_transactions(access_token)
        print(f"Found {len(transactions)} transactions:")
        for transaction in transactions[:5]:  # Show first 5 transactions
            print(f"- {transaction['date']} | {transaction['name']}: ${transaction['amount']}")

        print("\n5. Retrieving investment portfolio...")
        holdings_response = plaid.get_investment_holdings(access_token)
        
        if 'error' in holdings_response:
            if holdings_response['error'] == 'NO_INVESTMENT_ACCOUNTS':
                print("The user has no connected investment accounts.")
            else:
                print(f"Error: {holdings_response['message']}")
        else:
            print("\nInvestment Accounts:")
            investment_accounts = [acc for acc in holdings_response['accounts'] 
                                if acc['type'] == 'investment']
            
            for account in investment_accounts:
                print(format_account_summary(account))

            print("\nHoldings:")
            for holding in holdings_response['holdings']:
                security = next((s for s in holdings_response['securities'] 
                              if s['security_id'] == holding['security_id']), None)
                
                if security:
                    print(format_holding_details(holding, security))

        print("\n6. Retrieving liability information...")
        liabilities_response = plaid.get_liabilities(access_token)
        
        if 'error' in liabilities_response:
            print(liabilities_response['message'])
        else:
            liabilities = liabilities_response['liabilities']
            
            if 'credit' in liabilities:
                print("\nCredit Cards:")
                # Get all credit accounts for additional details
                credit_accounts = [acc for acc in liabilities_response['accounts'] 
                                 if acc['type'] == 'credit']
                
                for credit in liabilities['credit']:
                    # Find matching account
                    account = next((acc for acc in credit_accounts 
                                  if acc['account_id'] == credit['account_id']), None)
                    
                    if account:
                        print(f"- {account['name']}")
                    else:
                        print(f"- Credit Card (Account ID: {credit['account_id']})")
                        print("  Note: Account name not available")
                        
                    print(f"  Last Statement Balance: ${credit['last_statement_balance']:,.2f}")
                    if 'last_payment_amount' in credit:
                        print(f"  Last Payment: ${credit['last_payment_amount']:,.2f}")
                    if 'minimum_payment_amount' in credit:
                        print(f"  Minimum Payment: ${credit['minimum_payment_amount']:,.2f}")
                    if 'is_overdue' in credit:
                        print(f"  Overdue: {credit['is_overdue']}")
                    
                    # Show only the purchase APR (main interest rate)
                    purchase_apr = next((apr for apr in credit['aprs'] 
                                       if apr['apr_type'] == 'purchase_apr'), None)
                    if purchase_apr:
                        print(f"  Purchase APR: {purchase_apr['apr_percentage']}%")
                        print(f"  Balance Subject to APR: ${purchase_apr['balance_subject_to_apr']:,.2f}")
            
            if 'student' in liabilities:
                print("\nStudent Loans:")
                for loan in liabilities['student']:
                    account = next((acc for acc in liabilities_response['accounts'] 
                                  if acc['account_id'] == loan['account_id']), None)
                    
                    account_name = account['name'] if account else loan['account_id']
                    print(f"- {account_name}")
                    print(f"  Current Balance: ${loan['last_statement_balance']:,.2f}")
                    if 'last_payment_amount' in loan:
                        print(f"  Last Payment: ${loan['last_payment_amount']:,.2f}")
                    if 'minimum_payment_amount' in loan:
                        print(f"  Minimum Payment: ${loan['minimum_payment_amount']:,.2f}")
                    if 'loan_status' in loan:
                        print(f"  Status: {loan['loan_status']['type']}")
                    if 'interest_rate_percentage' in loan:
                        rate = loan['interest_rate_percentage']
                        print(f"  Interest Rate: {rate}%")
                    if 'expected_payoff_date' in loan:
                        print(f"  Expected Payoff Date: {loan['expected_payoff_date']}")
                    if 'origination_principal_amount' in loan:
                        principal = loan['origination_principal_amount']
                        if rate and 'expected_payoff_date' in loan and 'origination_date' in loan:
                            # Calculate total payments (simplified)
                            years = (loan['expected_payoff_date'] - 
                                   loan['origination_date']).days / 365
                            total = principal * (1 + (rate/100 * years))
                            print(f"  Original Principal: ${principal:,.2f}")
                            print(f"  Estimated Total with Interest: ${total:,.2f}")
            
            if 'mortgage' in liabilities:
                print("\nMortgages:")
                for mortgage in liabilities['mortgage']:
                    account = next((acc for acc in liabilities_response['accounts'] 
                                  if acc['account_id'] == mortgage['account_id']), None)
                    
                    account_name = account['name'] if account else mortgage['account_id']
                    print(f"- {account_name}")
                    if 'outstanding_principal_balance' in mortgage:
                        print(f"  Outstanding Principal: ${mortgage['outstanding_principal_balance']:,.2f}")
                    if 'last_payment_amount' in mortgage:
                        print(f"  Last Payment: ${mortgage['last_payment_amount']:,.2f}")
                    if 'last_payment_date' in mortgage:
                        print(f"  Last Payment Date: {mortgage['last_payment_date']}")
                    if 'loan_term' in mortgage:
                        print(f"  Loan Term: {mortgage['loan_term']} months")
                    if 'interest_rate' in mortgage and 'percentage' in mortgage['interest_rate']:
                        rate = mortgage['interest_rate']['percentage']
                        print(f"  Interest Rate: {rate}%")
                    if 'origination_principal_amount' in mortgage:
                        principal = mortgage['origination_principal_amount']
                        if rate and 'loan_term' in mortgage:
                            # Calculate total mortgage payments
                            years = float(mortgage['loan_term'].split()[0])
                            monthly_rate = (rate/100) / 12
                            num_payments = years * 12
                            monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
                            total = monthly_payment * num_payments
                            print(f"  Original Principal: ${principal:,.2f}")
                            print(f"  Estimated Total with Interest: ${total:,.2f}")
                            print(f"  Estimated Monthly Payment: ${monthly_payment:,.2f}")
        
        print("\nPlaid integration test completed successfully.")

        return True

    except Exception as e:
        print(f"Error during Plaid testing: {str(e)}")
        import traceback
        print(traceback.format_exc())  # This will print the full error traceback
        return False

if __name__ == '__main__':
    test_plaid_integration()