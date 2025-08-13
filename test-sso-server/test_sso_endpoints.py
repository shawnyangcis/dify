#!/usr/bin/env python3
"""
SSO Endpoint Testing Script
Tests the mock SSO server endpoints to verify OAuth 2.0 flow
"""

import requests
import json
from urllib.parse import parse_qs, urlparse, urlencode

# Configuration
MOCK_SSO_BASE_URL = "http://localhost:8000"
DIFY_API_BASE_URL = "http://localhost:5001"
CLIENT_ID = "test_client_id"
CLIENT_SECRET = "test_client_secret"
REDIRECT_URI = "http://localhost:5001/console/api/oauth/authorize/sso"

def test_health_check():
    """Test if mock SSO server is running"""
    print("🏥 Testing Mock SSO Server Health...")
    try:
        response = requests.get(f"{MOCK_SSO_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Mock SSO Server is running")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Mock SSO Server not accessible: {e}")
        return False

def test_authorization_endpoint():
    """Test authorization endpoint"""
    print("\n🔐 Testing Authorization Endpoint...")
    
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'state': 'test_state_12345',
        'scope': 'openid email profile'
    }
    
    url = f"{MOCK_SSO_BASE_URL}/oauth/authorize"
    print(f"   URL: {url}")
    print(f"   Params: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=10, allow_redirects=False)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Authorization endpoint accessible (should show login form)")
            # Check if response contains the login form
            if "Select Test User" in response.text:
                print("✅ Login form is properly rendered")
            else:
                print("⚠️  Login form might not be rendering correctly")
        else:
            print(f"❌ Authorization endpoint failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Authorization request failed: {e}")

def simulate_oauth_flow():
    """Simulate complete OAuth flow (without browser interaction)"""
    print("\n🔄 Simulating OAuth Flow...")
    
    # Step 1: Get authorization URL
    auth_params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'state': 'test_state_12345',
        'scope': 'openid email profile'
    }
    
    print("   Step 1: Getting authorization URL...")
    print(f"   Auth URL: {MOCK_SSO_BASE_URL}/oauth/authorize?{urlencode(auth_params)}")
    
    # Step 2: Simulate user login (POST to authorization endpoint)
    print("   Step 2: Simulating user login...")
    login_data = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'state': 'test_state_12345',
        'scope': 'openid email profile',
        'user_email': 'test@company.com'  # Select test user
    }
    
    try:
        auth_response = requests.post(
            f"{MOCK_SSO_BASE_URL}/oauth/authorize",
            data=login_data,
            allow_redirects=False,
            timeout=10
        )
        
        if auth_response.status_code == 302:
            # Parse redirect URL to get authorization code
            location = auth_response.headers.get('Location')
            print(f"   ✅ Redirect to: {location}")
            
            parsed_url = urlparse(location)
            query_params = parse_qs(parsed_url.query)
            auth_code = query_params.get('code', [None])[0]
            state = query_params.get('state', [None])[0]
            
            if auth_code:
                print(f"   ✅ Authorization code received: {auth_code[:20]}...")
                print(f"   ✅ State parameter: {state}")
                
                # Step 3: Exchange code for token
                return test_token_exchange(auth_code)
            else:
                print("   ❌ No authorization code in redirect")
                return False
        else:
            print(f"   ❌ Authorization failed: {auth_response.status_code}")
            print(f"   Response: {auth_response.text[:200]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Authorization simulation failed: {e}")
        return False

def test_token_exchange(auth_code):
    """Test token exchange"""
    print("   Step 3: Testing token exchange...")
    
    token_data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI
    }
    
    try:
        token_response = requests.post(
            f"{MOCK_SSO_BASE_URL}/oauth/token",
            data=token_data,
            timeout=10
        )
        
        if token_response.status_code == 200:
            token_data = token_response.json()
            access_token = token_data.get('access_token')
            print(f"   ✅ Access token received: {access_token[:20]}...")
            print(f"   Token type: {token_data.get('token_type')}")
            print(f"   Expires in: {token_data.get('expires_in')} seconds")
            
            # Step 4: Test user info endpoint
            return test_user_info(access_token)
        else:
            print(f"   ❌ Token exchange failed: {token_response.status_code}")
            print(f"   Response: {token_response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Token exchange failed: {e}")
        return False

def test_user_info(access_token):
    """Test user info endpoint"""
    print("   Step 4: Testing user info endpoint...")
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        userinfo_response = requests.get(
            f"{MOCK_SSO_BASE_URL}/oauth/userinfo",
            headers=headers,
            timeout=10
        )
        
        if userinfo_response.status_code == 200:
            user_data = userinfo_response.json()
            print("   ✅ User info retrieved successfully:")
            print(f"      ID: {user_data.get('id')}")
            print(f"      Name: {user_data.get('name')}")
            print(f"      Email: {user_data.get('email')}")
            print(f"      Company: {user_data.get('company')}")
            return True
        else:
            print(f"   ❌ User info request failed: {userinfo_response.status_code}")
            print(f"   Response: {userinfo_response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ User info request failed: {e}")
        return False

def test_dify_system_features():
    """Test if Dify recognizes the SSO configuration"""
    print("\n🔧 Testing Dify System Features...")
    
    try:
        response = requests.get(
            f"{DIFY_API_BASE_URL}/console/api/system-features",
            timeout=10
        )
        
        if response.status_code == 200:
            features = response.json()
            sso_enabled = features.get('enable_custom_sso', False)
            
            print(f"   Status: {response.status_code}")
            print(f"   SSO Enabled: {sso_enabled}")
            
            if sso_enabled:
                print("   ✅ Dify recognizes SSO configuration")
                return True
            else:
                print("   ❌ SSO not enabled in Dify configuration")
                print("   Check your .env SSO_* variables")
                return False
        else:
            print(f"   ❌ Dify API not accessible: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Dify API not accessible: {e}")
        print("   Make sure Dify API server is running on localhost:5001")
        return False

def main():
    """Main testing function"""
    print("🧪 SSO Integration Testing")
    print("=" * 50)
    
    # Test sequence
    tests = [
        ("Mock SSO Server Health", test_health_check),
        ("Authorization Endpoint", test_authorization_endpoint),
        ("Complete OAuth Flow", simulate_oauth_flow),
        ("Dify System Features", test_dify_system_features)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! SSO integration is ready for testing.")
        print("\nNext steps:")
        print("1. Start the mock SSO server: ./run_mock_server.sh")
        print("2. Start Dify with the local test configuration")
        print("3. Open http://localhost:3000 and test SSO login")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check configuration and services.")

if __name__ == "__main__":
    main()