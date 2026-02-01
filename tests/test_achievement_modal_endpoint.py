"""
Tests for the achievement modal detail endpoint
Tests the /api/todo/<int:todo_id>/details endpoint added for modal functionality
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db
from app.models import User, Todo, Tracker, Status

# Using app fixture from conftest.py for proper database isolation


@pytest.fixture
def client(app):
    """Create a test client for the application."""
    return app.test_client()


@pytest.fixture
def auth_user(client, app):
    """Create and login a test user."""
    with app.app_context():
        user = User(email='testmodal@example.com', fullname='Modal Test User')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Login
        client.post('/login', data={
            'email': 'testmodal@example.com',
            'password': 'password123'
        })
        
        return client, user
    
"""
Simple test to verify the achievement modal endpoint is registered and functions
"""

def test_achievement_modal_endpoint_registered(app):
    """Verify /api/todo/<int:todo_id>/details endpoint is registered"""
    
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    
    # Check that the endpoint exists
    detail_route_found = any('api/todo' in r and 'details' in r for r in routes)
    assert detail_route_found, "Endpoint /api/todo/<int:todo_id>/details not found in routes"


def test_achievement_modal_endpoint_requires_auth(app, client):
    """Verify endpoint requires authentication"""
    
    # Try to access without login - should get 401
    response = client.get('/api/todo/1/details')
    assert response.status_code == 401, "Endpoint should require authentication"
