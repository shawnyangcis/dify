#!/usr/bin/env python3
"""
Mock SSO Server for testing Dify Custom SSO Integration
This server simulates an OAuth 2.0 provider for local testing
"""

import json
import uuid
from urllib.parse import parse_qs, urlencode, urlparse
from flask import Flask, request, redirect, render_template_string, jsonify
import secrets
import time

app = Flask(__name__)

# In-memory storage for authorization codes and tokens
auth_codes = {}
access_tokens = {}

# Mock user database
MOCK_USERS = {
    "test@company.com": {
        "id": "12345",
        "sub": "12345", 
        "name": "Test User",
        "email": "test@company.com",
        "company": "Test Company Ltd",
        "username": "testuser"
    },
    "admin@company.com": {
        "id": "67890",
        "sub": "67890",
        "name": "Admin User", 
        "email": "admin@company.com",
        "company": "Test Company Ltd",
        "username": "admin"
    }
}

# OAuth 2.0 Configuration
OAUTH_CONFIG = {
    "client_id": "test_client_id",
    "client_secret": "test_client_secret"
}

@app.route('/')
def home():
    return """
    <h1>Mock SSO Server</h1>
    <p>This is a test OAuth 2.0 server for Dify SSO integration testing.</p>
    <h2>Available Test Users:</h2>
    <ul>
        <li>test@company.com - Test User (Test Company Ltd)</li>
        <li>admin@company.com - Admin User (Test Company Ltd)</li>
    </ul>
    <h2>OAuth Endpoints:</h2>
    <ul>
        <li><strong>Authorization:</strong> <code>/oauth/authorize</code></li>
        <li><strong>Token:</strong> <code>/oauth/token</code></li>
        <li><strong>UserInfo:</strong> <code>/oauth/userinfo</code></li>
    </ul>
    """

@app.route('/oauth/authorize', methods=['GET'])
def authorize():
    """OAuth 2.0 Authorization Endpoint"""
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')
    response_type = request.args.get('response_type', 'code')
    state = request.args.get('state', '')
    scope = request.args.get('scope', '')
    
    print(f"Authorization request: client_id={client_id}, redirect_uri={redirect_uri}")
    
    if not client_id or not redirect_uri:
        return "Missing client_id or redirect_uri", 400
    
    if client_id != OAUTH_CONFIG['client_id']:
        return "Invalid client_id", 400
        
    if response_type != 'code':
        return "Only 'code' response_type is supported", 400
    
    # Show login form
    login_form = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mock SSO Login</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            select, button { width: 100%; padding: 10px; font-size: 16px; }
            button { background: #007cba; color: white; border: none; cursor: pointer; margin-top: 20px; }
            button:hover { background: #005a87; }
            .info { background: #f0f8ff; padding: 15px; border-left: 4px solid #007cba; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h2>Mock SSO Server - Login</h2>
        <div class="info">
            <strong>Testing Dify SSO Integration</strong><br>
            Client ID: {{ client_id }}<br>
            Redirect URI: {{ redirect_uri }}
        </div>
        
        <form method="POST" action="/oauth/authorize">
            <input type="hidden" name="client_id" value="{{ client_id }}">
            <input type="hidden" name="redirect_uri" value="{{ redirect_uri }}">
            <input type="hidden" name="response_type" value="{{ response_type }}">
            <input type="hidden" name="state" value="{{ state }}">
            <input type="hidden" name="scope" value="{{ scope }}">
            
            <div class="form-group">
                <label for="user_email">Select Test User:</label>
                <select name="user_email" id="user_email" required>
                    <option value="">-- Select a user --</option>
                    <option value="test@company.com">test@company.com (Test User)</option>
                    <option value="admin@company.com">admin@company.com (Admin User)</option>
                </select>
            </div>
            
            <button type="submit">Login & Authorize</button>
        </form>
        
        <div class="info">
            <strong>Note:</strong> This is a mock server for testing. In production, 
            users would enter their real credentials here.
        </div>
    </body>
    </html>
    """
    
    return render_template_string(login_form, 
                                client_id=client_id,
                                redirect_uri=redirect_uri,
                                response_type=response_type,
                                state=state,
                                scope=scope)

@app.route('/oauth/authorize', methods=['POST'])
def authorize_post():
    """Handle authorization form submission"""
    client_id = request.form.get('client_id')
    redirect_uri = request.form.get('redirect_uri')
    state = request.form.get('state', '')
    user_email = request.form.get('user_email')
    
    if not user_email or user_email not in MOCK_USERS:
        return "Invalid user selected", 400
    
    # Generate authorization code
    auth_code = secrets.token_urlsafe(32)
    auth_codes[auth_code] = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'user_email': user_email,
        'expires_at': time.time() + 600,  # 10 minutes
        'used': False
    }
    
    print(f"Generated auth code: {auth_code} for user: {user_email}")
    
    # Redirect back to client
    params = {'code': auth_code}
    if state:
        params['state'] = state
        
    callback_url = f"{redirect_uri}?{urlencode(params)}"
    print(f"Redirecting to: {callback_url}")
    
    return redirect(callback_url)

@app.route('/oauth/token', methods=['POST'])
def token():
    """OAuth 2.0 Token Endpoint"""
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    grant_type = request.form.get('grant_type')
    code = request.form.get('code')
    redirect_uri = request.form.get('redirect_uri')
    
    print(f"Token request: client_id={client_id}, grant_type={grant_type}, code={code}")
    
    if grant_type != 'authorization_code':
        return jsonify({'error': 'unsupported_grant_type'}), 400
    
    if client_id != OAUTH_CONFIG['client_id'] or client_secret != OAUTH_CONFIG['client_secret']:
        return jsonify({'error': 'invalid_client'}), 401
    
    if not code or code not in auth_codes:
        return jsonify({'error': 'invalid_grant'}), 400
    
    auth_data = auth_codes[code]
    
    # Check if code is expired or already used
    if time.time() > auth_data['expires_at'] or auth_data['used']:
        return jsonify({'error': 'invalid_grant'}), 400
    
    if auth_data['client_id'] != client_id or auth_data['redirect_uri'] != redirect_uri:
        return jsonify({'error': 'invalid_grant'}), 400
    
    # Mark code as used
    auth_data['used'] = True
    
    # Generate access token
    access_token = secrets.token_urlsafe(64)
    access_tokens[access_token] = {
        'user_email': auth_data['user_email'],
        'expires_at': time.time() + 3600,  # 1 hour
        'scope': 'aaabbbccc'
    }
    
    print(f"Generated access token for user: {auth_data['user_email']}")
    
    return jsonify({
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires_in': 3600,
        'scope': 'aaabbbccc'
    })

@app.route('/oauth/userinfo', methods=['GET'])
def userinfo():
    """OAuth 2.0 UserInfo Endpoint"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'invalid_request'}), 400
    
    access_token = auth_header[7:]  # Remove 'Bearer ' prefix
    
    if access_token not in access_tokens:
        return jsonify({'error': 'invalid_token'}), 401
    
    token_data = access_tokens[access_token]
    
    # Check if token is expired
    if time.time() > token_data['expires_at']:
        return jsonify({'error': 'invalid_token'}), 401
    
    user_email = token_data['user_email']
    user_info = MOCK_USERS.get(user_email)
    
    if not user_info:
        return jsonify({'error': 'invalid_token'}), 401
    
    print(f"Returning user info for: {user_email}")
    
    # Return user information
    return jsonify(user_info)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'Mock SSO Server',
        'endpoints': {
            'authorize': '/oauth/authorize',
            'token': '/oauth/token', 
            'userinfo': '/oauth/userinfo'
        }
    })

if __name__ == '__main__':
    print("🚀 Starting Mock SSO Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🔧 OAuth Client ID: test_client_id")
    print("🔑 OAuth Client Secret: test_client_secret")
    print("👥 Test users: test@company.com, admin@company.com")
    print("")
    app.run(host='0.0.0.0', port=8000, debug=True)