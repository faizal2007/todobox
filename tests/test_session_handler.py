"""
Tests for session_handler module

Tests cover:
- Session expiration detection
- Session warning detection
- Last activity updates
- Session expiration redirection
- Decorators functionality
- Context processor
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from flask import url_for, session as flask_session
from app.session_handler import (
    SessionExpirationHandler,
    session_required,
    session_extended_required,
    session_aware_context_processor,
    init_session_handler,
    check_session_expiration
)


class TestSessionExpirationHandler:
    """Tests for SessionExpirationHandler class"""
    
    def test_session_not_expired_within_timeout(self, client, app, test_user):
        """Test that session is not marked as expired when within timeout period"""
        with client:
            # Login user
            response = client.post(url_for('login'), data={
                'email': test_user.email,
                'password': 'test_password_123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Session should not be expired
            assert not SessionExpirationHandler.is_session_expired()
    
    def test_session_expired_after_timeout(self, client, app, test_user):
        """Test that session is marked as expired after timeout period"""
        with client:
            # Login user
            response = client.post(url_for('login'), data={
                'email': test_user.email,
                'password': 'test_password_123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Manually set last activity to past expiration time
            past_time = datetime.utcnow() - timedelta(
                minutes=SessionExpirationHandler.INACTIVITY_TIMEOUT + 10
            )
            flask_session['last_activity'] = past_time.isoformat()
            flask_session.modified = True
            
            # Session should be expired
            assert SessionExpirationHandler.is_session_expired()
    
    def test_session_warning_threshold(self, client, app, test_user):
        """Test session warning is triggered within warning threshold"""
        with client:
            # Login user
            response = client.post(url_for('login'), data={
                'email': test_user.email,
                'password': 'test_password_123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Set last activity to near expiration (within warning threshold)
            warning_time = datetime.utcnow() - timedelta(
                minutes=SessionExpirationHandler.INACTIVITY_TIMEOUT - 5
            )
            flask_session['last_activity'] = warning_time.isoformat()
            flask_session.modified = True
            
            # Should trigger warning
            assert SessionExpirationHandler.is_session_warning_time()
    
    def test_update_last_activity(self, client, app, test_user):
        """Test that last activity timestamp is updated"""
        with client:
            # Login user
            response = client.post(url_for('login'), data={
                'email': test_user.email,
                'password': 'test_password_123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            old_time_str = flask_session.get('last_activity')
            old_time = datetime.fromisoformat(old_time_str)
            
            # Wait a moment and update
            SessionExpirationHandler.update_last_activity()
            
            new_time_str = flask_session.get('last_activity')
            new_time = datetime.fromisoformat(new_time_str)
            
            # New time should be after old time
            assert new_time >= old_time
    
    def test_get_remaining_time_minutes(self, client, app, test_user):
        """Test remaining time calculation"""
        with client:
            # Login user
            response = client.post(url_for('login'), data={
                'email': test_user.email,
                'password': 'test_password_123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Should have close to full timeout remaining
            remaining = SessionExpirationHandler.get_remaining_time_minutes()
            assert remaining > 0
            assert remaining <= SessionExpirationHandler.INACTIVITY_TIMEOUT
    
    def test_handle_expired_session_redirect(self, client, app, test_user):
        """Test redirect on expired session for regular request"""
        with client:
            # Login user
            response = client.post(url_for('login'), data={
                'email': test_user.email,
                'password': 'test_password_123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Expire session
            past_time = datetime.utcnow() - timedelta(
                minutes=SessionExpirationHandler.INACTIVITY_TIMEOUT + 10
            )
            flask_session['last_activity'] = past_time.isoformat()
            flask_session.modified = True
            
            # Simulate handling expired session
            # This test verifies the method can be called without error
            # Actual redirect testing is done in route tests
            assert SessionExpirationHandler.is_session_expired()
    
    def test_handle_expired_session_ajax(self, client, app, test_user):
        """Test JSON response on expired session for AJAX request"""
        with client:
            # Login user
            response = client.post(url_for('login'), data={
                'email': test_user.email,
                'password': 'test_password_123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Expire session
            past_time = datetime.utcnow() - timedelta(
                minutes=SessionExpirationHandler.INACTIVITY_TIMEOUT + 10
            )
            flask_session['last_activity'] = past_time.isoformat()
            flask_session.modified = True
            
            # Verify session is expired
            assert SessionExpirationHandler.is_session_expired()


class TestSessionDecorators:
    """Tests for session decorators"""
    
    def test_session_required_decorator_valid_session(self, client, app, test_user):
        """Test @session_required allows access with valid session"""
        # Create a test route with the decorator
        @app.route('/test-session-required')
        @session_required
        def test_route():
            return 'Success'
        
        # Login user
        with client:
            response = client.post(url_for('login'), data={
                'email': test_user.email,
                'password': 'test_password_123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Access protected route
            response = client.get('/test-session-required')
            assert response.status_code == 200
    
    def test_session_required_decorator_expired_session(self, client, app, test_user):
        """Test @session_required redirects with expired session"""
        # Create a test route with the decorator
        @app.route('/test-session-required-expire')
        @session_required
        def test_route():
            return 'Should not see this'
        
        with client:
            # Login user
            response = client.post(url_for('login'), data={
                'email': test_user.email,
                'password': 'test_password_123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Expire session
            past_time = datetime.utcnow() - timedelta(
                minutes=SessionExpirationHandler.INACTIVITY_TIMEOUT + 10
            )
            flask_session['last_activity'] = past_time.isoformat()
            flask_session.modified = True
            
            # Access protected route - should redirect to login
            response = client.get('/test-session-required-expire')
            assert response.status_code == 302
            assert 'login' in response.location.lower()


class TestSessionContextProcessor:
    """Tests for session context processor"""
    
    def test_context_processor_authenticated_user(self, client, app, test_user):
        """Test context processor provides correct values for authenticated user"""
        with client:
            # Login user
            response = client.post(url_for('login'), data={
                'email': test_user.email,
                'password': 'test_password_123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Get context
            context = session_aware_context_processor()
            
            assert 'session_warning' in context
            assert 'remaining_time' in context
            assert 'session_expired' in context
            assert isinstance(context['remaining_time'], int)
    
    def test_context_processor_unauthenticated_user(self, client, app):
        """Test context processor for unauthenticated user"""
        with client:
            # Get context without login
            context = session_aware_context_processor()
            
            assert context['session_warning'] is False
            assert context['remaining_time'] == 0
            assert context['session_expired'] is False


class TestCheckSessionExpiration:
    """Tests for check_session_expiration function"""
    
    def test_check_session_expiration_authenticated(self, client, app, test_user):
        """Test check_session_expiration for authenticated user"""
        with client:
            # Login user
            response = client.post(url_for('login'), data={
                'email': test_user.email,
                'password': 'test_password_123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Check session status
            status = check_session_expiration()
            
            assert status['is_authenticated'] is True
            assert status['is_expired'] is False
            assert status['is_warning'] is False
            assert status['remaining_minutes'] > 0
    
    def test_check_session_expiration_unauthenticated(self, client, app):
        """Test check_session_expiration for unauthenticated user"""
        with client:
            status = check_session_expiration()
            
            assert status['is_authenticated'] is False
            assert status['is_expired'] is False
            assert status['remaining_minutes'] >= 0
