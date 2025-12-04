#!/usr/bin/env python3
"""
Merge Readiness Test Suite for TodoBox

This test suite validates that the current branch is ready to be merged
with the master branch. It checks for:
- Critical functionality working
- No breaking changes
- All dependencies installed
- Database migrations compatible
- Configuration files valid
- API endpoints functional
"""

import pytest
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app, db
from app.models import User, Todo, Status
from app import config


class TestMergeReadiness:
    """Test suite to validate merge readiness"""
    
    def test_critical_imports_available(self):
        """Verify all critical imports are available"""
        try:
            from flask import Flask
            from flask_sqlalchemy import SQLAlchemy
            from flask_login import LoginManager
            from flask_wtf import FlaskForm
            from flask_migrate import Migrate
            import bleach
            import requests
            assert True
        except ImportError as e:
            pytest.fail(f"Critical import failed: {e}")
    
    def test_app_instance_available(self):
        """Test that app instance is successfully created"""
        assert flask_app is not None
        assert flask_app.config is not None
    
    def test_database_models_defined(self):
        """Verify all critical database models are defined"""
        assert hasattr(User, '__tablename__')
        assert hasattr(Todo, '__tablename__')
        assert hasattr(Status, '__tablename__')
    
    def test_required_configuration_keys_present(self):
        """Check that required configuration keys are defined"""
        with flask_app.app_context():
            # Check for essential config keys
            assert 'SECRET_KEY' in flask_app.config
            assert 'SQLALCHEMY_DATABASE_URI' in flask_app.config
            assert flask_app.config['SECRET_KEY'] is not None
    
    def test_routes_registered(self):
        """Verify that main routes are registered"""
        rules = [str(rule) for rule in flask_app.url_map.iter_rules()]
        
        # Check for essential routes
        assert any('/login' in rule for rule in rules)
        assert any('/api/quote' in rule for rule in rules)
        assert any('/healthz' in rule for rule in rules)
    
    def test_static_files_exist(self):
        """Verify essential static files exist"""
        base_path = Path(__file__).parent.parent / 'app' / 'static'
        
        # Check for essential static files
        assert (base_path / 'service-worker.js').exists()
        assert (base_path / 'manifest.json').exists()
        assert (base_path / 'css').is_dir()
    
    def test_template_files_exist(self):
        """Verify essential template files exist"""
        base_path = Path(__file__).parent.parent / 'app' / 'templates'
        
        # Check for essential templates
        assert (base_path / 'base.html').exists()
        assert (base_path / 'login.html').exists()
        assert (base_path / 'main.html').exists()
    
    def test_requirements_file_valid(self):
        """Check that requirements.txt is valid and parseable"""
        req_file = Path(__file__).parent.parent / 'requirements.txt'
        assert req_file.exists()
        
        with open(req_file) as f:
            lines = f.readlines()
            # Should have multiple dependencies
            assert len(lines) > 10
            # Check for key dependencies
            content = ''.join(lines)
            assert 'Flask' in content
            assert 'SQLAlchemy' in content


class TestCriticalFunctionality:
    """Test critical functionality that must work before merge"""
    
    @pytest.fixture
    def app(self):
        """Create test application with in-memory database"""
        # Configure for testing
        flask_app.config['TESTING'] = True
        original_db_uri = flask_app.config['SQLALCHEMY_DATABASE_URI']
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        flask_app.config['WTF_CSRF_ENABLED'] = False
        
        with flask_app.app_context():
            db.create_all()
            # Seed status table using the model's seed method
            if Status.query.count() == 0:
                Status.seed()
                db.session.commit()
            
            yield flask_app
            
            db.session.remove()
            db.drop_all()
        
        # Restore original config
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = original_db_uri
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_healthz_endpoint_works(self, client):
        """Critical: Health check endpoint must work"""
        response = client.get('/healthz')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
    
    def test_login_page_accessible(self, client):
        """Critical: Login page must be accessible"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower()
    
    def test_api_quote_endpoint_works(self, client):
        """Critical: Quote API must work"""
        response = client.get('/api/quote')
        assert response.status_code == 200
        data = response.get_json()
        assert 'quote' in data
    
    def test_user_creation_works(self, app):
        """Critical: User creation must work"""
        with app.app_context():
            user = User(email='test@example.com', fullname='Test User')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Verify user was created
            retrieved = User.query.filter_by(email='test@example.com').first()
            assert retrieved is not None
            assert retrieved.email == 'test@example.com'
            assert retrieved.check_password('password123')
    
    def test_todo_creation_works(self, app):
        """Critical: Todo creation must work"""
        with app.app_context():
            user = User(email='todo-test@example.com', fullname='Todo Test')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Create todo using property setters
            todo = Todo()
            todo.name = 'Test Todo'
            todo.details = 'Test Details'
            todo.user_id = user.id
            db.session.add(todo)
            db.session.commit()
            
            # Verify todo was created
            retrieved = Todo.query.first()
            assert retrieved is not None
            assert retrieved.name == 'Test Todo'
            assert retrieved.user_id == user.id


class TestDatabaseCompatibility:
    """Test database schema and migration compatibility"""
    
    @pytest.fixture
    def app(self):
        """Create test application with in-memory database"""
        flask_app.config['TESTING'] = True
        original_db_uri = flask_app.config['SQLALCHEMY_DATABASE_URI']
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with flask_app.app_context():
            db.create_all()
            yield flask_app
            db.session.remove()
            db.drop_all()
        
        # Restore original config
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = original_db_uri
    
    def test_user_model_has_required_fields(self, app):
        """Verify User model has all required fields"""
        with app.app_context():
            user = User(email='schema-test@example.com', fullname='Schema Test')
            
            # Check required fields exist
            assert hasattr(user, 'id')
            assert hasattr(user, 'email')
            assert hasattr(user, 'fullname')
            assert hasattr(user, 'password_hash')
            assert hasattr(user, 'api_token')
    
    def test_todo_model_has_required_fields(self, app):
        """Verify Todo model has all required fields"""
        with app.app_context():
            # Create a user first
            user = User(email='todo-schema@example.com', fullname='Todo Schema')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Create todo using property setters
            todo = Todo()
            todo.name = 'Schema Test'
            todo.details = 'Testing schema'
            todo.user_id = user.id
            
            # Check required fields exist
            assert hasattr(todo, 'id')
            assert hasattr(todo, 'name')
            assert hasattr(todo, 'details')
            assert hasattr(todo, 'user_id')
            assert hasattr(todo, 'timestamp')
            assert hasattr(todo, 'modified')
    
    def test_status_seeding_works(self, app):
        """Verify status table can be seeded"""
        with app.app_context():
            # Use the Status model's seed method
            Status.seed()
            db.session.commit()
            
            # Verify statuses exist
            assert Status.query.count() >= 4
            statuses = Status.query.all()
            status_names = [s.name for s in statuses]
            assert 'new' in status_names
            assert 'done' in status_names


class TestAPICompatibility:
    """Test API endpoints for backward compatibility"""
    
    @pytest.fixture
    def app(self):
        """Create test application with in-memory database"""
        flask_app.config['TESTING'] = True
        original_db_uri = flask_app.config['SQLALCHEMY_DATABASE_URI']
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        flask_app.config['WTF_CSRF_ENABLED'] = False
        
        with flask_app.app_context():
            db.create_all()
            # Seed status table using the model's seed method
            if Status.query.count() == 0:
                Status.seed()
                db.session.commit()
            
            yield flask_app
            
            db.session.remove()
            db.drop_all()
        
        # Restore original config
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = original_db_uri
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    @pytest.fixture
    def authenticated_user(self, app, client):
        """Create authenticated user with API token"""
        with app.app_context():
            user = User(email='api-test@example.com', fullname='API Test')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Login
            client.post('/login', data={
                'email': 'api-test@example.com',
                'password': 'password123'
            }, follow_redirects=True)
            
            # Generate API token
            response = client.post('/api/auth/token', follow_redirects=True)
            data = response.get_json()
            token = data.get('token') if data else None
            
            return {'user': user, 'token': token, 'client': client}
    
    def test_api_auth_token_generation(self, authenticated_user):
        """Test API token generation works"""
        assert authenticated_user['token'] is not None
        assert len(authenticated_user['token']) > 0
    
    def test_api_quote_returns_json(self, client):
        """Test quote API returns valid JSON"""
        response = client.get('/api/quote')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'quote' in data


class TestSecurityCompliance:
    """Test security measures are in place"""
    
    # Common insecure secret key values to check against
    INSECURE_SECRET_KEYS = ['dev', 'development', 'secret', 'default', 'test', 'change_me']
    
    @pytest.fixture
    def app(self):
        """Create test application with in-memory database"""
        flask_app.config['TESTING'] = True
        original_db_uri = flask_app.config['SQLALCHEMY_DATABASE_URI']
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with flask_app.app_context():
            db.create_all()
            yield flask_app
            db.session.remove()
            db.drop_all()
        
        # Restore original config
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = original_db_uri
    
    def test_passwords_are_hashed(self, app):
        """Verify passwords are not stored in plaintext"""
        with app.app_context():
            user = User(email='security-test@example.com', fullname='Security Test')
            password = 'mySecurePassword123'
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            # Password should not be stored in plaintext
            assert user.password_hash is not None
            assert user.password_hash != password
            assert len(user.password_hash) > 20  # Hashed passwords are long
            
            # But check_password should work
            assert user.check_password(password)
    
    def test_api_tokens_are_unique(self, app):
        """Verify API tokens are unique per user"""
        with app.app_context():
            user1 = User(email='token1@example.com', fullname='Token Test 1')
            user1.set_password('password123')
            user1.generate_api_token()
            db.session.add(user1)
            
            user2 = User(email='token2@example.com', fullname='Token Test 2')
            user2.set_password('password123')
            user2.generate_api_token()
            db.session.add(user2)
            
            db.session.commit()
            
            # Tokens should be unique
            assert user1.api_token != user2.api_token
    
    def test_secret_key_not_default(self, app):
        """Verify secret key is not using default value"""
        with app.app_context():
            secret_key = flask_app.config.get('SECRET_KEY')
            assert secret_key is not None
            # Should not be common default values
            assert secret_key not in self.INSECURE_SECRET_KEYS


class TestDocumentation:
    """Test that documentation is present and valid"""
    
    def test_readme_exists(self):
        """Verify README.md exists"""
        readme = Path(__file__).parent.parent / 'README.md'
        assert readme.exists()
        
        # Check it has content
        with open(readme) as f:
            content = f.read()
            assert len(content) > 100
            assert 'TodoBox' in content
    
    def test_requirements_documented(self):
        """Verify requirements.txt is documented"""
        req_file = Path(__file__).parent.parent / 'requirements.txt'
        assert req_file.exists()
        
        with open(req_file) as f:
            content = f.read()
            # Should have key packages
            assert 'Flask' in content
    
    def test_testing_documentation_exists(self):
        """Verify testing documentation exists"""
        # Check for README.md (main testing guide)
        test_doc = Path(__file__).parent / 'README.md'
        assert test_doc.exists(), "tests/README.md should exist"


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
