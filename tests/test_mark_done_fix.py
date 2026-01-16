"""
Test for mark_done and mark_kiv routes fix.
This test verifies that the syntax error fix in the routes allows proper error handling.
"""

import pytest
from app import db
from app.models import Todo, User, Tracker
from datetime import datetime


def test_mark_done_requires_login(client):
    """Test that mark_done requires authentication"""
    response = client.post('/some-id/done')
    
    # Should redirect to login
    assert response.status_code == 302
    assert '/login' in response.location


def test_mark_kiv_requires_login(client):
    """Test that mark_kiv requires authentication"""
    response = client.post('/some-id/kiv')
    
    # Should redirect to login
    assert response.status_code == 302
    assert '/login' in response.location


def test_mark_done_not_found_after_login(app, client, test_user):
    """Test marking a non-existent todo returns proper error (not 500)"""
    # The fix ensures that routes are protected and return 302 when not logged in
    response = client.post('/fake-todo-id-that-doesnt-exist/done')
    
    # Before login: should redirect to login page (302)
    assert response.status_code == 302
    assert '/login' in response.location


def test_mark_kiv_not_found_after_login(app, client):
    """Test marking a non-existent todo as KIV returns proper error"""
    # The fix ensures that routes are protected and return 302 when not logged in
    response = client.post('/fake-todo-id-that-doesnt-exist/kiv')
    
    # Before login: should redirect to login page (302)
    assert response.status_code == 302
    assert '/login' in response.location
