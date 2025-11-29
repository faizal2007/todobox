##
# Initial Config
##
import os
from dotenv import load_dotenv

load_dotenv()

SALT = os.environ.get('SALT', 'default-salt-change-in-production')
TITLE = os.environ.get('TITLE', 'My Sandbox')
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-production')
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'todobox.db')
DATABASE_DEFAULT = os.environ.get('DATABASE_DEFAULT', 'sqlite') # sqlite, mysql, or postgres

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
GOOGLE_DISCOVERY_URL = 'https://accounts.google.com/.well-known/openid-configuration'

# OAuth redirect URL
OAUTH_REDIRECT_URI = os.environ.get('OAUTH_REDIRECT_URI', 'http://localhost:5000/auth/callback/google')

# Reverse Proxy Configuration (for running behind load balancers, tunnels, etc.)
# Set these values to the number of trusted proxy layers for each header type
PROXY_X_FOR = int(os.environ.get('PROXY_X_FOR', '1'))  # X-Forwarded-For header trust level
PROXY_X_PROTO = int(os.environ.get('PROXY_X_PROTO', '1'))  # X-Forwarded-Proto header trust level
PROXY_X_HOST = int(os.environ.get('PROXY_X_HOST', '1'))  # X-Forwarded-Host header trust level
PROXY_X_PREFIX = int(os.environ.get('PROXY_X_PREFIX', '1'))  # X-Forwarded-Prefix header trust level
