#!/bin/bash

echo "🚀 Starting Mock SSO Server for Dify Testing"
echo "============================================="

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Mock SSO Server Configuration:"
echo "   Server URL: http://localhost:8000"
echo "   Client ID: test_client_id"
echo "   Client Secret: test_client_secret"
echo ""
echo "📋 Test Users Available:"
echo "   - test@company.com (Test User at Test Company Ltd)"
echo "   - admin@company.com (Admin User at Test Company Ltd)"
echo ""
echo "🌐 OAuth 2.0 Endpoints:"
echo "   - Authorization: http://localhost:8000/oauth/authorize"
echo "   - Token: http://localhost:8000/oauth/token"
echo "   - UserInfo: http://localhost:8000/oauth/userinfo"
echo ""

# Start the server
python3 mock_sso_server.py
