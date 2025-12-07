# Google OAuth2 Setup Guide

This guide explains how to set up Google OAuth2 authentication for the application.

## Step 1: Install Dependencies

First, install the required packages:

```bash
pip install -r requirements.txt
```yaml

The following packages are required for OAuth:

- Flask-OAuthlib==0.9.7
- google-auth-oauthlib==1.2.0
- google-auth==2.26.0
- requests==2.31.0

## Step 2: Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API:
   - Navigate to "APIs & Services" → "Library"
   - Search for "Google+ API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:5000/auth/callback/google` (for development)
     - `https://yourdomain.com/auth/callback/google` (for production)
   - Click "Create"

## Step 3: Configure Environment Variables

Add the following to your `.flaskenv` or `.env` file:

```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
OAUTH_REDIRECT_URI=http://localhost:5000/auth/callback/google
```yaml

For production:

```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
OAUTH_REDIRECT_URI=https://yourdomain.com/auth/callback/google
```yaml

## Step 4: Run Database Migration

If you're updating an existing database, you need to add the new columns to the User table:

```bash
flask db migrate -m "Add OAuth columns to User model"
flask db upgrade
```yaml

For fresh installations, the columns will be created automatically.

## Step 5: Test the Integration

### 1. Start the Flask development server

```bash
python todobox.py
```python

#### 2. Navigate to the login page: `http://localhost:5000/login`

#### 3. Click "Sign in with Google"

#### 4. You'll be redirected to Google for authentication

#### 5. After successful authentication, you'll be logged in and redirected to your dashboard

## Features

### First-Time Users

- New users who sign in with Google will have an account automatically created
- Their email becomes their unique identifier
- Username is generated from their email (e.g., <john.doe@gmail.com> → john.doe)
- They can update their profile on the account page

### Existing Users

- Users who registered with password can add Google OAuth by signing in with Google using the same email
- The system will recognize the email and link the accounts

### Account Security

- Users authenticated via Google cannot change their password (OAuth-managed)
- Users can still manage other account details (username, full name, email)
- Password-only users can optionally add Google OAuth to their account

## OAuth Routes

- `GET /auth/login/google` - Initiates Google OAuth login
- `GET /auth/callback/google` - Google OAuth callback (handled automatically)

## Troubleshooting

### "Invalid Client" Error

- Verify that `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are correct
- Check that the redirect URI matches exactly (including http/https)

### "Redirect URI Mismatch" Error

- Go to Google Cloud Console
- Verify the authorized redirect URI in OAuth settings matches the one in your environment

### Token Verification Failed

- Ensure `google-auth-oauthlib` is installed: `pip install google-auth-oauthlib`
- Check that credentials haven't expired

### User Not Created

- Check application logs for error messages
- Verify database has the new `oauth_provider` and `oauth_id` columns
- Run migrations if upgrading: `flask db upgrade`

## Security Considerations

1. **Never commit credentials**: Keep `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in environment variables only
2. **HTTPS in Production**: Always use HTTPS in production
3. **Token Storage**: Tokens are not stored; only user info is saved
4. **Email Verification**: Google verifies email, so no additional verification needed

## Database Schema Changes

The User model now includes:

- `oauth_provider` (String): OAuth provider name ('google' or None)
- `oauth_id` (String): Provider-specific user ID (Google's subject ID)

These fields allow linking multiple OAuth providers in the future.

## Future Enhancements

Potential features to add:

- GitHub OAuth
- Facebook OAuth
- Microsoft OAuth
- Account linking (multiple OAuth providers per user)
- OAuth token refresh for API access
