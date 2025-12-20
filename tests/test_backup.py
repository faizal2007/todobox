#!/usr/bin/env python
"""
Test script for backup functionality
"""

import sys
import os
from pathlib import Path
import json
import csv
import io

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app, db
from app.models import User, Todo, Status, KIV

def test_backup_functionality():
    """Test backup route with sample data"""
    
    print("\n📦 Testing Backup Functionality")
    print("=" * 50)
    
    with app.app_context():
        # Create test user
        test_user = User.query.filter_by(email='test_backup@test.local').first()
        if test_user:
            db.session.delete(test_user)
            db.session.commit()
        
        test_user = User(email='test_backup@test.local', fullname='Test User')
        test_user.set_password('password123')
        test_user.email_verified = True
        db.session.add(test_user)
        db.session.commit()
        
        print(f"✅ Test user created: {test_user.email}")
        
        # Create test todos
        status = Status.query.filter_by(name='Todo').first()
        if not status:
            status = Status(name='Todo')
            db.session.add(status)
            db.session.commit()
        
        for i in range(3):
            todo = Todo(name=f'Test Todo {i+1}', details=f'Details for todo {i+1}', user_id=test_user.id)
            db.session.add(todo)
        
        db.session.commit()
        print(f"✅ Created 3 test todos")
        
        # Test backup route
        with app.test_client() as client:
            # Login
            with client.session_transaction() as sess:
                from flask_login import session as flask_session
            
            # Make backup request
            response = client.get('/backup?format=json', 
                                headers={'Authorization': f'Bearer {test_user.api_token}'} if test_user.api_token else None)
            
            # Since we're not actually logged in, this would redirect
            # Let's test with the test client in authenticated mode
            with client:
                client.post('/login', data={
                    'email': 'test_backup@test.local',
                    'password': 'password123'
                }, follow_redirects=True)
                
                # Test JSON backup
                response = client.get('/backup?format=json')
                if response.status_code == 200:
                    print(f"✅ JSON backup endpoint returned 200")
                    try:
                        data = json.loads(response.data.decode('utf-8'))
                        print(f"  - Backup date: {data.get('backup_date')}")
                        print(f"  - User email: {data.get('user_email')}")
                        print(f"  - Total todos: {data.get('total_todos')}")
                        print(f"  - Todos backed up: {len(data.get('todos', []))}")
                    except Exception as e:
                        print(f"❌ Failed to parse JSON response: {e}")
                else:
                    print(f"⚠️ JSON backup endpoint returned {response.status_code}")
                
                # Test CSV backup
                response = client.get('/backup?format=csv')
                if response.status_code == 200:
                    print(f"✅ CSV backup endpoint returned 200")
                    try:
                        csv_data = response.data.decode('utf-8')
                        reader = csv.reader(io.StringIO(csv_data))
                        rows = list(reader)
                        print(f"  - CSV header: {rows[0] if rows else 'None'}")
                        print(f"  - CSV rows: {len(rows) - 1}")  # Exclude header
                    except Exception as e:
                        print(f"❌ Failed to parse CSV response: {e}")
                else:
                    print(f"⚠️ CSV backup endpoint returned {response.status_code}")
        
        # Cleanup
        db.session.delete(test_user)
        db.session.commit()
        print(f"✅ Test user cleaned up")
    
    print("=" * 50)
    print("✅ Backup functionality test completed")
    print("=" * 50 + "\n")

if __name__ == '__main__':
    try:
        test_backup_functionality()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
