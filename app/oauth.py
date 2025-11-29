"""
Google OAuth2 Authentication Handler
"""

import os
import requests
import json
from flask import current_app, url_for, session
from google.auth.transport.requests import Request
from google.oauth2.id_token import verify_oauth2_token
from app.models import User
from app import db

def get_google_provider_config():
    """Fetch Google OAuth configuration"""
    return requests.get(current_app.config['GOOGLE_DISCOVERY_URL']).json()

def get_oauth_redirect_uri():
    """Get the OAuth redirect URI from config or generate dynamically"""
    # Use explicitly configured redirect URI if available (for reverse proxy scenarios)
    configured_uri = current_app.config.get('OAUTH_REDIRECT_URI')
    # Use configured URI if it's set and not a localhost/127.0.0.1 address (HTTP or HTTPS)
    local_prefixes = (
        'http://localhost', 'https://localhost',
        'http://127.0.0.1', 'https://127.0.0.1'
    )
    if configured_uri and not configured_uri.startswith(local_prefixes):
        return configured_uri
    # Fall back to dynamically generated URL
    return url_for("oauth_callback_google", _external=True)

def generate_google_auth_url():
    """Generate Google OAuth authentication URL"""
    google_provider_cfg = get_google_provider_config()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    
    request_uri = (
        authorization_endpoint
        + "?"
        + "client_id={}&response_type={}&scope={}&redirect_uri={}&access_type={}".format(
            current_app.config['GOOGLE_CLIENT_ID'],
            "code",
            "openid email profile",
            get_oauth_redirect_uri(),
            "offline"
        )
    )
    return request_uri

def process_google_callback(code):
    """
    Process Google OAuth callback and return user info
    Returns: tuple (user, is_new_user)
    """
    try:
        google_provider_cfg = get_google_provider_config()
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        # Exchange authorization code for token
        token_request_body = {
            "code": code,
            "client_id": current_app.config['GOOGLE_CLIENT_ID'],
            "client_secret": current_app.config['GOOGLE_CLIENT_SECRET'],
            "redirect_uri": get_oauth_redirect_uri(),
            "grant_type": "authorization_code",
        }
        
        token_response = requests.post(token_endpoint, data=token_request_body)
        tokens = token_response.json()
        
        if "error" in tokens:
            return None, False
            
        id_token = tokens.get("id_token")
        
        # Verify and decode the token
        try:
            id_info = verify_oauth2_token(id_token, Request(), current_app.config['GOOGLE_CLIENT_ID'])
        except ValueError:
            # Token verification failed
            return None, False
        
        # Extract user information
        email = id_info.get("email")
        name = id_info.get("name", "")
        google_id = id_info.get("sub")
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user:
            # Update OAuth info if not already set
            if not existing_user.oauth_provider:
                existing_user.oauth_provider = "google"
                existing_user.oauth_id = google_id
                db.session.commit()  # type: ignore[attr-defined]
            return existing_user, False
        
        # Create new user
        # Extract username from email (part before @)
        username = email.split('@')[0]
        
        # Ensure unique username
        base_username = username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1
        
        new_user = User(
            username=username,
            email=email,
            oauth_provider="google",
            oauth_id=google_id
        )
        
        if name:
            new_user.fullname = name
        
        db.session.add(new_user)  # type: ignore[attr-defined]
        db.session.commit()  # type: ignore[attr-defined]
        
        return new_user, True
        
    except Exception as e:
        print(f"Error processing Google callback: {str(e)}")
        return None, False
