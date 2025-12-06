##
# Initial Config
##
import os
from dotenv import load_dotenv

load_dotenv()

SALT = os.environ.get('SALT', 'default-salt-change-in-production')
TITLE = os.environ.get('TITLE', 'My Sandbox')
# Security: Generate a random secret key if not provided
import secrets
SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_urlsafe(32)
if not os.environ.get('SECRET_KEY'):
    print("WARNING: SECRET_KEY not set in environment. Using generated key. Set SECRET_KEY in production!")
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'todobox.db')
DATABASE_DEFAULT = os.environ.get('DATABASE_DEFAULT', 'sqlite') # sqlite, mysql, or postgres

# Todo Encryption Configuration
# Set to 'true' to enable encryption of todo data (name, details, details_html)
# When enabled, database administrators cannot read todo content in raw database
TODO_ENCRYPTION_ENABLED = os.environ.get('TODO_ENCRYPTION_ENABLED', 'false').lower() == 'true'

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
GOOGLE_DISCOVERY_URL = 'https://accounts.google.com/.well-known/openid-configuration'

# Google OAuth UX and security
# Default to showing the Google account chooser to avoid silent auto-login
GOOGLE_OAUTH_PROMPT = os.environ.get('GOOGLE_OAUTH_PROMPT', 'select_account')  # e.g., 'select_account', 'consent', or 'select_account consent'

# OAuth redirect URL
OAUTH_REDIRECT_URI = os.environ.get('OAUTH_REDIRECT_URI', 'http://localhost:5000/auth/callback/google')

# Email/SMTP Configuration (for sharing invitations)
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')  # App-specific password for Gmail
SMTP_FROM_EMAIL = os.environ.get('SMTP_FROM_EMAIL', '')

# Reverse Proxy Configuration (for running behind load balancers, tunnels, etc.)
# Set these values to the number of trusted proxy layers for each header type
PROXY_X_FOR = int(os.environ.get('PROXY_X_FOR', '1'))  # X-Forwarded-For header trust level
PROXY_X_PROTO = int(os.environ.get('PROXY_X_PROTO', '1'))  # X-Forwarded-Proto header trust level
PROXY_X_HOST = int(os.environ.get('PROXY_X_HOST', '1'))  # X-Forwarded-Host header trust level
PROXY_X_PREFIX = int(os.environ.get('PROXY_X_PREFIX', '1'))  # X-Forwarded-Prefix header trust level

# Cookie & URL settings for HTTPS behind Cloudflare
PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME', 'https')

SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'true').lower() == 'true'
SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'true').lower() == 'true'
SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')  # 'Lax' | 'Strict' | 'None'
# Optional cookie domain (e.g., .example.com); leave unset unless needed
SESSION_COOKIE_DOMAIN = os.environ.get('SESSION_COOKIE_DOMAIN') or None

REMEMBER_COOKIE_SECURE = os.environ.get('REMEMBER_COOKIE_SECURE', 'true').lower() == 'true'
REMEMBER_COOKIE_HTTPONLY = os.environ.get('REMEMBER_COOKIE_HTTPONLY', 'true').lower() == 'true'
REMEMBER_COOKIE_SAMESITE = os.environ.get('REMEMBER_COOKIE_SAMESITE', 'Lax')

# PWA Debug Button (show only if enabled)
PWA_DEBUG = os.environ.get('PWA_DEBUG', 'false').lower() == 'true'

# Flask Debug Mode
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
