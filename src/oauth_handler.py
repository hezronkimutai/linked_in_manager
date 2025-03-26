import os
import json
import asyncio
from typing import Optional, Dict
from fastapi import FastAPI, HTTPException
from cryptography.fernet import Fernet
import uvicorn
import aiohttp
from datetime import datetime, timedelta
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse, parse_qs

class OAuthHandler:
    def __init__(self):
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.linkedin_username = os.getenv('LINKEDIN_USERNAME')
        self.linkedin_password = os.getenv('LINKEDIN_PASSWORD')
        self.redirect_uri = os.getenv('REDIRECT_URI', 'http://localhost:8000/callback')
        self.token_file = '.linkedin_tokens.enc'
        
        # Validate required environment variables
        print("Checking environment variables...")
        missing_vars = []
        invalid_vars = []
        
        for var in ['LINKEDIN_CLIENT_ID', 'LINKEDIN_CLIENT_SECRET', 'LINKEDIN_USERNAME', 'LINKEDIN_PASSWORD']:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            elif value.startswith(' ') or value.endswith(' '):
                invalid_vars.append(var)
                # Strip whitespace and update environment variable
                os.environ[var] = value.strip()
                print(f"Fixed whitespace in {var}")
                
        if missing_vars:
            print(f"Missing required environment variables: {', '.join(missing_vars)}")
        if invalid_vars:
            print(f"Found and fixed whitespace in variables: {', '.join(invalid_vars)}")
        
        # Handle encryption key
        env_key = os.getenv('TOKEN_ENCRYPTION_KEY')
        if env_key:
            try:
                # Validate the provided key
                self.encryption_key = base64.urlsafe_b64decode(env_key)
                if len(self.encryption_key) != 32:
                    raise ValueError("Invalid key length")
            except Exception:
                # If provided key is invalid, generate a new one
                self.encryption_key = Fernet.generate_key()
        else:
            # Generate a new key if none provided
            self.encryption_key = Fernet.generate_key()
            
        self.cipher_suite = Fernet(self.encryption_key)
        self.app = FastAPI()
        self.setup_routes()
        
    def setup_routes(self):
        @self.app.get("/callback")
        async def callback(code: str):
            try:
                await self.get_access_token(code)
                return {"message": "Authorization successful! You can close this window."}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

    async def automated_authorization(self) -> Optional[str]:
        """Perform automated authorization using Selenium"""
        if not all([self.linkedin_username, self.linkedin_password]):
            print("LinkedIn credentials not found in environment variables.")
            return await self.manual_authorization()

        print("Starting automated authorization...")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Required for CI environment
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-data-dir=/tmp/chrome-data')  # Specify unique user data directory
        options.add_argument('--remote-debugging-port=9222')  # Add debugging port
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            print("Initializing Chrome WebDriver...")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("WebDriver initialized successfully")
            
            # Navigate to LinkedIn authorization URL
            scope = "openid profile w_member_social email"  # Standardized scope
            auth_url = (
                f"https://www.linkedin.com/oauth/v2/authorization"
                f"?response_type=code"
                f"&client_id={self.client_id}"
                f"&redirect_uri={self.redirect_uri}"
                f"&scope={scope}"
            )
            print(f"Navigating to authorization URL...")
            driver.get(auth_url)

            try:
                print("Waiting for login form...")
                # Wait for and fill in login form
                username_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                username_field.send_keys(self.linkedin_username)
                print("Username entered...")
                
                password_field = driver.find_element(By.ID, "password")
                password_field.send_keys(self.linkedin_password)
                print("Password entered...")
                
                submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                submit_button.click()
                print("Login form submitted...")

                # Wait for redirect to callback URL
                print("Waiting for redirect...")
                wait = WebDriverWait(driver, 20)
                wait.until(lambda driver: self.redirect_uri in driver.current_url)
                print(f"Current URL after redirect: {driver.current_url}")
            except Exception as e:
                print(f"Error during login process: {str(e)}")
                raise
            
            try:
                # Extract authorization code from URL
                current_url = driver.current_url
                print(f"Parsing URL for auth code: {current_url}")
                
                parsed_url = urlparse(current_url)
                query_params = parse_qs(parsed_url.query)
                print(f"Query parameters: {query_params}")
                
                auth_code = query_params.get('code', [None])[0]
                if auth_code:
                    print("Successfully extracted authorization code")
                else:
                    print("No authorization code found in URL")
                    if 'error' in query_params:
                        print(f"OAuth error: {query_params['error']}")
                
                driver.quit()
                print("Browser session closed")
                
                if auth_code:
                    # Get access token using the authorization code
                    print("Exchanging authorization code for access token...")
                    token_data = await self.get_access_token(auth_code)
                    return token_data.get('access_token')
                
                return None
            except Exception as e:
                print(f"Error extracting authorization code: {str(e)}")
                return None
            
        except Exception as e:
            print(f"Automated authorization failed: {str(e)}")
            print("Falling back to manual authorization...")
            return await self.manual_authorization()

    async def manual_authorization(self):
        """Fall back to manual authorization process"""
        scope = "openid profile w_member_social email"
        auth_url = (
            f"https://www.linkedin.com/oauth/v2/authorization"
            f"?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope={scope}"
        )
        print(f"Please visit this URL to authorize the application: {auth_url}")
        
        config = uvicorn.Config(self.app, host="0.0.0.0", port=8000, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

    async def get_access_token(self, auth_code: str) -> Dict:
        """Exchange authorization code for access token"""
        async with aiohttp.ClientSession() as session:
            data = {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': self.redirect_uri,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            async with session.post('https://www.linkedin.com/oauth/v2/accessToken', data=data) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get access token: {await response.text()}")
                
                token_data = await response.json()
                token_data['timestamp'] = datetime.now().isoformat()
                await self.save_tokens(token_data)
                return token_data

    async def refresh_token(self, refresh_token: str) -> Dict:
        """Refresh the access token using the refresh token"""
        async with aiohttp.ClientSession() as session:
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            async with session.post('https://www.linkedin.com/oauth/v2/accessToken', data=data) as response:
                if response.status != 200:
                    raise Exception(f"Failed to refresh token: {await response.text()}")
                
                token_data = await response.json()
                token_data['timestamp'] = datetime.now().isoformat()
                await self.save_tokens(token_data)
                return token_data

    async def save_tokens(self, token_data: Dict) -> None:
        """Save tokens securely"""
        encrypted_data = self.cipher_suite.encrypt(json.dumps(token_data).encode())
        with open(self.token_file, 'wb') as f:
            f.write(encrypted_data)

    async def load_tokens(self) -> Optional[Dict]:
        """Load and validate stored tokens"""
        try:
            if not os.path.exists(self.token_file):
                return None
                
            with open(self.token_file, 'rb') as f:
                encrypted_data = f.read()
                
            token_data = json.loads(self.cipher_suite.decrypt(encrypted_data))
            token_timestamp = datetime.fromisoformat(token_data['timestamp'])
            
            # Check if token is expired (assuming 60-day expiration)
            if datetime.now() - token_timestamp > timedelta(days=60):
                if 'refresh_token' in token_data:
                    return await self.refresh_token(token_data['refresh_token'])
                return None
                
            return token_data
        except Exception as e:
            print(f"Error loading tokens: {e}")
            return None

    async def get_valid_token(self) -> Optional[str]:
        """Get a valid access token, refreshing if necessary"""
        token_data = await self.load_tokens()
        
        if not token_data:
            return await self.automated_authorization()
            
        return token_data.get('access_token')

# Example usage
async def main():
    oauth_handler = OAuthHandler()
    token = await oauth_handler.get_valid_token()
    if token:
        print("Valid token obtained!")
    else:
        print("Authorization failed.")

if __name__ == "__main__":
    asyncio.run(main())