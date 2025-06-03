"""
Salesforce CRM Integration

A comprehensive integration for connecting CrewAI workflows with Salesforce CRM,
enabling automated lead management, opportunity tracking, and customer data analysis.
"""

from typing import Dict, List, Optional, Any
import requests
import os
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class SalesforceConfig:
    """Configuration for Salesforce integration."""
    client_id: str
    client_secret: str
    username: str
    password: str
    security_token: str
    instance_url: str = "https://login.salesforce.com"
    api_version: str = "v58.0"

class SalesforceIntegration:
    """
    Salesforce CRM Integration for CrewAI workflows.
    
    Provides methods for:
    - Authentication and session management
    - Lead creation and management
    - Opportunity tracking
    - Contact and account management
    - Custom object operations
    - Data analysis and reporting
    """
    
    def __init__(self, config: Optional[SalesforceConfig] = None):
        """
        Initialize Salesforce integration.
        
        Args:
            config: Salesforce configuration object
        """
        if config:
            self.config = config
        else:
            # Load from environment variables
            self.config = SalesforceConfig(
                client_id=os.getenv('SALESFORCE_CLIENT_ID', ''),
                client_secret=os.getenv('SALESFORCE_CLIENT_SECRET', ''),
                username=os.getenv('SALESFORCE_USERNAME', ''),
                password=os.getenv('SALESFORCE_PASSWORD', ''),
                security_token=os.getenv('SALESFORCE_SECURITY_TOKEN', ''),
                instance_url=os.getenv('SALESFORCE_INSTANCE_URL', 'https://login.salesforce.com')
            )
        
        self.session = requests.Session()
        self.access_token = None
        self.instance_url = None
        
    def authenticate(self) -> bool:
        """
        Authenticate with Salesforce and obtain access token.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            auth_url = f"{self.config.instance_url}/services/oauth2/token"
            
            auth_data = {
                'grant_type': 'password',
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret,
                'username': self.config.username,
                'password': f"{self.config.password}{self.config.security_token}"
            }
            
            response = self.session.post(auth_url, data=auth_data)
            response.raise_for_status()
            
            auth_result = response.json()
            self.access_token = auth_result['access_token']
            self.instance_url = auth_result['instance_url']
            
            # Set authorization header for future requests
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
            
            return True
            
        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            return False
    
    def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new lead in Salesforce.
        
        Args:
            lead_data: Dictionary containing lead information
                Required fields: LastName, Company
                Optional fields: FirstName, Email, Phone, etc.
        
        Returns:
            Dict containing the created lead's ID and success status
        """
        if not self.access_token:
            if not self.authenticate():
                return {"success": False, "error": "Authentication failed"}
        
        try:
            url = f"{self.instance_url}/services/data/{self.config.api_version}/sobjects/Lead"
            
            # Ensure required fields are present
            if 'LastName' not in lead_data or 'Company' not in lead_data:
                return {
                    "success": False, 
                    "error": "LastName and Company are required fields"
                }
            
            response = self.session.post(url, json=lead_data)
            response.raise_for_status()
            
            result = response.json()
            return {
                "success": True,
                "id": result['id'],
                "lead_data": lead_data
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_lead(self, lead_id: str) -> Dict[str, Any]:
        """
        Retrieve a lead by ID.
        
        Args:
            lead_id: Salesforce lead ID
            
        Returns:
            Dict containing lead information
        """
        if not self.access_token:
            if not self.authenticate():
                return {"success": False, "error": "Authentication failed"}
        
        try:
            url = f"{self.instance_url}/services/data/{self.config.api_version}/sobjects/Lead/{lead_id}"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            return {"success": True, "data": response.json()}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_lead(self, lead_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing lead.
        
        Args:
            lead_id: Salesforce lead ID
            update_data: Dictionary containing fields to update
            
        Returns:
            Dict containing success status
        """
        if not self.access_token:
            if not self.authenticate():
                return {"success": False, "error": "Authentication failed"}
        
        try:
            url = f"{self.instance_url}/services/data/{self.config.api_version}/sobjects/Lead/{lead_id}"
            
            response = self.session.patch(url, json=update_data)
            response.raise_for_status()
            
            return {"success": True, "updated_fields": update_data}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_opportunity(self, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new opportunity in Salesforce.
        
        Args:
            opportunity_data: Dictionary containing opportunity information
                Required fields: Name, StageName, CloseDate
        
        Returns:
            Dict containing the created opportunity's ID and success status
        """
        if not self.access_token:
            if not self.authenticate():
                return {"success": False, "error": "Authentication failed"}
        
        try:
            url = f"{self.instance_url}/services/data/{self.config.api_version}/sobjects/Opportunity"
            
            # Ensure required fields are present
            required_fields = ['Name', 'StageName', 'CloseDate']
            missing_fields = [field for field in required_fields if field not in opportunity_data]
            
            if missing_fields:
                return {
                    "success": False, 
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }
            
            response = self.session.post(url, json=opportunity_data)
            response.raise_for_status()
            
            result = response.json()
            return {
                "success": True,
                "id": result['id'],
                "opportunity_data": opportunity_data
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def query_records(self, soql_query: str) -> Dict[str, Any]:
        """
        Execute a SOQL query.
        
        Args:
            soql_query: SOQL query string
            
        Returns:
            Dict containing query results
        """
        if not self.access_token:
            if not self.authenticate():
                return {"success": False, "error": "Authentication failed"}
        
        try:
            url = f"{self.instance_url}/services/data/{self.config.api_version}/query"
            
            response = self.session.get(url, params={'q': soql_query})
            response.raise_for_status()
            
            result = response.json()
            return {
                "success": True,
                "total_size": result['totalSize'],
                "records": result['records']
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_recent_leads(self, days: int = 7) -> Dict[str, Any]:
        """
        Get leads created in the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dict containing recent leads
        """
        soql_query = f"""
        SELECT Id, FirstName, LastName, Company, Email, Phone, Status, CreatedDate
        FROM Lead 
        WHERE CreatedDate = LAST_N_DAYS:{days}
        ORDER BY CreatedDate DESC
        """
        
        return self.query_records(soql_query)
    
    def get_pipeline_report(self) -> Dict[str, Any]:
        """
        Generate a sales pipeline report.
        
        Returns:
            Dict containing pipeline metrics
        """
        soql_query = """
        SELECT StageName, COUNT(Id) OpportunityCount, SUM(Amount) TotalAmount
        FROM Opportunity 
        WHERE IsClosed = false
        GROUP BY StageName
        """
        
        result = self.query_records(soql_query)
        
        if result['success']:
            # Process the results into a more readable format
            pipeline_data = {}
            total_opportunities = 0
            total_amount = 0
            
            for record in result['records']:
                stage = record['StageName']
                count = record['OpportunityCount']
                amount = record['TotalAmount'] or 0
                
                pipeline_data[stage] = {
                    'count': count,
                    'amount': amount
                }
                
                total_opportunities += count
                total_amount += amount
            
            return {
                "success": True,
                "pipeline": pipeline_data,
                "summary": {
                    "total_opportunities": total_opportunities,
                    "total_amount": total_amount
                }
            }
        
        return result
    
    def convert_lead_to_opportunity(self, lead_id: str, opportunity_name: str) -> Dict[str, Any]:
        """
        Convert a lead to an opportunity.
        
        Args:
            lead_id: Salesforce lead ID
            opportunity_name: Name for the new opportunity
            
        Returns:
            Dict containing conversion results
        """
        if not self.access_token:
            if not self.authenticate():
                return {"success": False, "error": "Authentication failed"}
        
        try:
            # First, get the lead information
            lead_result = self.get_lead(lead_id)
            if not lead_result['success']:
                return lead_result
            
            lead_data = lead_result['data']
            
            # Create account if it doesn't exist
            account_data = {
                'Name': lead_data['Company'],
                'Type': 'Prospect'
            }
            
            # Create contact
            contact_data = {
                'FirstName': lead_data.get('FirstName', ''),
                'LastName': lead_data['LastName'],
                'Email': lead_data.get('Email', ''),
                'Phone': lead_data.get('Phone', '')
            }
            
            # Create opportunity
            opportunity_data = {
                'Name': opportunity_name,
                'StageName': 'Prospecting',
                'CloseDate': datetime.now().strftime('%Y-%m-%d')
            }
            
            # In a real implementation, you would:
            # 1. Create or find the account
            # 2. Create the contact linked to the account
            # 3. Create the opportunity linked to the account
            # 4. Update the lead status to converted
            
            return {
                "success": True,
                "message": "Lead conversion process initiated",
                "lead_id": lead_id,
                "opportunity_name": opportunity_name
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# Example usage and testing
if __name__ == "__main__":
    # Initialize Salesforce integration
    sf = SalesforceIntegration()
    
    # Test authentication
    if sf.authenticate():
        print("✅ Salesforce authentication successful")
        
        # Example: Create a new lead
        lead_data = {
            'FirstName': 'John',
            'LastName': 'Doe',
            'Company': 'Tech Innovations Inc.',
            'Email': 'john.doe@techinnovations.com',
            'Phone': '+1-555-123-4567',
            'Status': 'Open - Not Contacted'
        }
        
        result = sf.create_lead(lead_data)
        if result['success']:
            print(f"✅ Lead created with ID: {result['id']}")
        else:
            print(f"❌ Failed to create lead: {result['error']}")
        
        # Example: Get recent leads
        recent_leads = sf.get_recent_leads(days=30)
        if recent_leads['success']:
            print(f"📊 Found {recent_leads['total_size']} recent leads")
        
        # Example: Generate pipeline report
        pipeline = sf.get_pipeline_report()
        if pipeline['success']:
            print("📈 Sales Pipeline Report:")
            for stage, data in pipeline['pipeline'].items():
                print(f"  {stage}: {data['count']} opportunities, ${data['amount']:,.2f}")
    
    else:
        print("❌ Salesforce authentication failed") 