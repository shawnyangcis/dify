# Custom SSO Integration Guide for Dify

This guide explains how to configure and use the custom Single Sign-On (SSO) functionality that has been added to Dify.

## Overview

The custom SSO integration allows Dify to authenticate users through any OAuth 2.0-compatible SSO provider. This implementation supports:

- OAuth 2.0 Authorization Code flow
- Automatic user creation and login
- User attribute synchronization (email and company)
- Flexible configuration for different environments

## Configuration

### 1. Environment Variables

Add the following configuration to your `.env` file or set as environment variables:

```bash
# Enable custom SSO functionality
SSO_ENABLED=true

# SSO OAuth endpoints
SSO_AUTH_ENDPOINT=http://wm.stg.paic.com.cn/gw/oauth/v2/authorize
SSO_TOKEN_ENDPOINT=http://wm.stg.paic.com.cn/gw/oauth/v2/token
SSO_USERINFO_ENDPOINT=http://wm.stg.paic.com.cn/gw/oauth/v2/userInfo

# SSO OAuth credentials
SSO_CLIENT_ID=Ov23lirUopDC7TuZ3eeD
SSO_CLIENT_SECRET=479eac814f270a0fad2fe682a8cdbef6bc936b7f

# SSO OAuth redirect URI (must match your Dify instance URL)
SSO_REDIRECT_URI=http://gaadp.fat001.qa.pab.com/console/api/oauth/authorize/sso

# OAuth scopes (space-separated, can be empty)
SSO_SCOPES=
```

### 2. Database Migration

The implementation adds a `company` field to the accounts table. Run the database migration:

```bash
cd api
flask db upgrade
```

### 3. Configuration Notes

- **SSO_ENABLED**: Must be `true` to enable the SSO button in the login page
- **SSO_REDIRECT_URI**: Must be registered in your SSO provider and point to your Dify instance
- **All required fields**: All SSO configuration fields must be provided for the SSO option to appear
- **SSO_SCOPES**: Can be left empty if your SSO provider doesn't require specific scopes

## How It Works

### Authentication Flow

1. **User Initiation**: User clicks "Continue with SSO" button on the login page
2. **Authorization Request**: Dify redirects user to SSO provider's authorization endpoint
3. **User Authentication**: User authenticates with the SSO provider
4. **Authorization Grant**: SSO provider redirects back to Dify with authorization code
5. **Token Exchange**: Dify exchanges the code for access token
6. **User Information**: Dify retrieves user information using the access token
7. **Account Management**: Dify creates new account or updates existing account
8. **Login**: User is automatically logged into Dify

### User Data Mapping

The SSO integration maps user attributes as follows:

| SSO Attribute | Dify Field | Notes |
|---------------|------------|-------|
| `sub`, `id`, `user_id` | Account ID | Used for linking accounts |
| `name`, `username`, `display_name` | User Name | Display name in Dify |
| `email` | Email Address | Primary identifier |
| `company`, `organization` | Company | New field for organization info |

### Account Linking

- **New Users**: Automatically creates new Dify account with SSO information
- **Existing Users**: Links SSO identity to existing account (matched by email)
- **Company Sync**: Updates company information on each login

## Testing the Integration

### 1. Verify Configuration

Check that your configuration is correct by calling the system features API:

```bash
curl -X GET "http://your-dify-instance/console/api/system-features"
```

Look for `enable_custom_sso: true` in the response.

### 2. Test SSO Flow

1. **Access Login Page**: Navigate to your Dify instance login page
2. **Verify SSO Button**: Confirm "Continue with SSO" button appears
3. **Click SSO Button**: Should redirect to your SSO provider
4. **Authenticate**: Complete authentication with your SSO provider
5. **Verify Redirect**: Should return to Dify and log you in automatically

### 3. Verify User Creation

Check the database to confirm user was created correctly:

```sql
SELECT id, name, email, company, created_at 
FROM accounts 
WHERE email = 'your-sso-email@company.com';
```

### 4. Test Account Linking

1. Create a Dify account manually with the same email as your SSO account
2. Use SSO login - should link to the existing account
3. Verify company information is updated if provided by SSO

## Troubleshooting

### Common Issues

1. **SSO Button Not Appearing**
   - Check `SSO_ENABLED=true`
   - Verify all required SSO_* environment variables are set
   - Restart the Dify service

2. **Redirect URI Mismatch**
   - Ensure `SSO_REDIRECT_URI` matches exactly what's registered with SSO provider
   - Check for trailing slashes or protocol mismatches

3. **Token Exchange Failures**
   - Verify `SSO_CLIENT_ID` and `SSO_CLIENT_SECRET` are correct
   - Check `SSO_TOKEN_ENDPOINT` URL is accessible from Dify server
   - Review server logs for detailed error messages

4. **User Information Errors**
   - Verify `SSO_USERINFO_ENDPOINT` returns expected user attributes
   - Check if additional scopes are needed in `SSO_SCOPES`

### Debug Logging

Enable debug logging to see detailed OAuth flow information:

```bash
LOG_LEVEL=DEBUG
```

Check the logs at `/app/logs/server.log` for OAuth-related messages.

### Manual Testing with cURL

Test your SSO endpoints manually:

```bash
# Test authorization endpoint
curl -I "http://wm.stg.paic.com.cn/gw/oauth/v2/authorize?client_id=Ov23lirUopDC7TuZ3eeD&response_type=code&redirect_uri=http://gaadp.fat001.qa.pab.com/console/api/oauth/authorize/sso"

# Test token endpoint (after getting authorization code)
curl -X POST "http://wm.stg.paic.com.cn/gw/oauth/v2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=Ov23lirUopDC7TuZ3eeD&client_secret=479eac814f270a0fad2fe682a8cdbef6bc936b7f&code=YOUR_CODE&grant_type=authorization_code&redirect_uri=http://gaadp.fat001.qa.pab.com/console/api/oauth/authorize/sso"
```

## Security Considerations

1. **HTTPS**: Use HTTPS for production deployments
2. **Client Secret**: Keep `SSO_CLIENT_SECRET` secure and rotate regularly
3. **Redirect URI**: Register exact redirect URI with SSO provider
4. **Scope Limitation**: Request minimal necessary scopes from SSO provider

## Environment-Specific Configuration

### Development Environment

```bash
SSO_ENABLED=true
SSO_AUTH_ENDPOINT=http://wm.stg.paic.com.cn/gw/oauth/v2/authorize
SSO_TOKEN_ENDPOINT=http://wm.stg.paic.com.cn/gw/oauth/v2/token
SSO_USERINFO_ENDPOINT=http://wm.stg.paic.com.cn/gw/oauth/v2/userInfo
SSO_CLIENT_ID=Ov23lirUopDC7TuZ3eeD
SSO_CLIENT_SECRET=479eac814f270a0fad2fe682a8cdbef6bc936b7f
SSO_REDIRECT_URI=http://localhost:3000/console/api/oauth/authorize/sso
SSO_SCOPES=
```

### Production Environment

```bash
SSO_ENABLED=true
SSO_AUTH_ENDPOINT=http://wm.prod.paic.com.cn/gw/oauth/v2/authorize
SSO_TOKEN_ENDPOINT=http://wm.prod.paic.com.cn/gw/oauth/v2/token
SSO_USERINFO_ENDPOINT=http://wm.prod.paic.com.cn/gw/oauth/v2/userInfo
SSO_CLIENT_ID=PROD_CLIENT_ID
SSO_CLIENT_SECRET=PROD_CLIENT_SECRET
SSO_REDIRECT_URI=https://your-production-dify.com/console/api/oauth/authorize/sso
SSO_SCOPES=
```

## Implementation Details

### Files Modified

**Backend:**
- `api/configs/feature/__init__.py` - Added SSO configuration
- `api/libs/oauth.py` - Added CustomSSOOAuth class
- `api/controllers/console/auth/oauth.py` - Added SSO provider support
- `api/models/account.py` - Added company field
- `api/services/feature_service.py` - Added SSO feature flag
- `docker/.env.example` - Added SSO configuration examples

**Frontend:**
- `web/app/signin/components/custom-sso-auth.tsx` - SSO login button component
- `web/app/signin/normal-form.tsx` - Integrated SSO button
- `web/types/feature.ts` - Added SSO type definitions

**Database:**
- `api/migrations/versions/2025_01_16_1200-add_company_field_to_accounts.py` - Migration for company field

This implementation follows Dify's existing OAuth patterns and integrates seamlessly with the current authentication system.