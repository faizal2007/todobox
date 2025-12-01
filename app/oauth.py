"""
Google OAuth2 Authentication Handler
"""

import os
import requests
import json
import secrets
from urllib.parse import urlencode
from flask import current_app, url_for, session, request as flask_request
from google.auth.transport.requests import Request
from google.oauth2.id_token import verify_oauth2_token
from app.models import User
from app import db


class OAuthError(Exception):
    """Custom exception for OAuth errors"""
    pass


def get_google_provider_config():
    """Fetch Google OAuth configuration"""
    try:
        response = requests.get(
            current_app.config['GOOGLE_DISCOVERY_URL'],
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise OAuthError(f"Failed to fetch Google OAuth configuration: {e}")


def get_oauth_redirect_uri():
    """Get the OAuth redirect URI from config or generate dynamically.
    
    When running behind a reverse proxy (e.g., Cloudflare tunnel, ngrok, haruka-tunnel),
    the OAUTH_REDIRECT_URI should be explicitly set to the public URL.
    
    Returns:
        str: The OAuth callback redirect URI
    """
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
    # Note: This relies on ProxyFix middleware processing X-Forwarded-* headers
    generated_uri = url_for("oauth_callback_google", _external=True)
    
    # Log a warning if the generated URI looks like it might be wrong (localhost when not expected)
    if generated_uri.startswith(local_prefixes):
        # Check if we're actually behind a proxy (X-Forwarded-* headers present)
        x_forwarded_host = flask_request.headers.get('X-Forwarded-Host')
        x_forwarded_proto = flask_request.headers.get('X-Forwarded-Proto')
        if x_forwarded_host or x_forwarded_proto:
            current_app.logger.warning(
                f"OAuth redirect URI is localhost but X-Forwarded headers detected. "
                f"Consider setting OAUTH_REDIRECT_URI explicitly. "
                f"Generated: {generated_uri}, X-Forwarded-Host: {x_forwarded_host}"
            )
    
    return generated_uri


def generate_google_auth_url():
    """Generate Google OAuth authentication URL.
    
    Returns:
        str: The Google OAuth authorization URL
        
    Raises:
        OAuthError: If Google OAuth configuration cannot be fetched or is invalid
    """
    try:
        google_provider_cfg = get_google_provider_config()
        
        if "authorization_endpoint" not in google_provider_cfg:
            raise OAuthError("Invalid Google OAuth configuration: missing authorization_endpoint")
        
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        redirect_uri = get_oauth_redirect_uri()
        prompt = current_app.config.get('GOOGLE_OAUTH_PROMPT', 'select_account')
        
        # Generate and store state for CSRF protection
        state = secrets.token_urlsafe(32)
        session['oauth_state'] = state
        
        # Log the redirect URI for debugging
        current_app.logger.debug(f"OAuth redirect URI: {redirect_uri}")

        params = {
            "client_id": current_app.config['GOOGLE_CLIENT_ID'],
            "response_type": "code",
            "scope": "openid email profile",
            "redirect_uri": redirect_uri,
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": prompt,
            "state": state,
        }

        return authorization_endpoint + "?" + urlencode(params)
    except OAuthError:
        raise
    except Exception as e:
        raise OAuthError(f"Failed to generate Google auth URL: {e}")

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
        
        token_response = requests.post(token_endpoint, data=token_request_body, timeout=10)
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
        new_user = User(
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
        current_app.logger.error(f"Error processing Google callback: {e}")
        return None, False
