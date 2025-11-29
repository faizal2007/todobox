#!/usr/bin/env python3
"""
Interactive user creation script for TodoBox first-time setup
Usage: python3 create_user.py
"""

import os
import sys
import getpass
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Interactive first-time user creation"""
    
    print("\n" + "="*60)
    print("  TodoBox - First Time User Creation".center(60))
    print("="*60 + "\n")
    
    # Import Flask app here to ensure environment is loaded
    from app import app, db
    from app.models import User
    
    with app.app_context():
        # Check if admin already exists
        existing_admin = User.query.filter_by(username='admin').first()
        
        if existing_admin:
            print("⚠️  Admin user already exists!")
            print(f"   Username: {existing_admin.username}")
            print(f"   Email: {existing_admin.email}")
            print("\nOptions:")
            print("  1) Reset admin password")
            print("  2) Create a different user")
            print("  3) Exit")
            
            choice = input("\nSelect option (1-3): ").strip()
            
            if choice == '1':
                reset_admin_password(existing_admin)
            elif choice == '2':
                create_new_user()
            else:
                print("\n✅ Exiting without changes.\n")
                sys.exit(0)
        else:
            print("No admin user found. Creating first-time admin user...\n")
            create_first_admin_user()
    
    print("\n" + "="*60)
    print("✅ User creation completed successfully!".center(60))
    print("="*60 + "\n")

def create_first_admin_user():
    """Create the initial admin user with guided prompts"""
    from app import app, db
    from app.models import User
    
    with app.app_context():
        print("Creating ADMIN user (first-time setup)")
        print("-" * 60)
        
        # Use default admin or get custom
        use_default = input("\nUse default admin user? (username: admin, email: admin@examples.com) [Y/n]: ").strip().lower()
        
        if use_default != 'n':
            username = 'admin'
            email = 'admin@examples.com'
            print(f"\n✓ Username: {username}")
            print(f"✓ Email: {email}")
        else:
            username = get_valid_username()
            email = get_valid_email(username)
        
        # Get password
        password = get_valid_password()
        
        # Ask about admin privileges (default to Yes for first-time admin setup)
        make_admin = input("\nAssign admin privileges? [Y/n]: ").strip().lower()
        is_admin = make_admin != 'n'
        
        # Confirm
        print("\n" + "-" * 60)
        print("Confirm user details:")
        print(f"  Username: {username}")
        print(f"  Email: {email}")
        print(f"  Password: {'*' * len(password)}")
        print(f"  Admin: {'Yes' if is_admin else 'No'}")
        print("-" * 60)
        
        confirm = input("\nCreate this user? [Y/n]: ").strip().lower()
        
        if confirm == 'n':
            print("\n❌ User creation cancelled.")
            return False
        
        # Create user
        try:
            user = User(username=username, email=email)
            user.is_admin = is_admin
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            admin_status = " (admin)" if is_admin else ""
            print(f"\n✅ Admin user '{username}'{admin_status} created successfully!")
            return True
        except Exception as e:
            print(f"\n❌ Error creating user: {e}")
            db.session.rollback()
            return False

def create_new_user():
    """Create a new user with optional admin privileges"""
    from app import app, db
    from app.models import User
    
    with app.app_context():
        print("\n\nCreating NEW user")
        print("-" * 60)
        
        username = get_valid_username()
        email = get_valid_email(username)
        password = get_valid_password()
        fullname = input("\nFull name (optional) []: ").strip()
        
        # Ask about admin privileges
        make_admin = input("\nAssign admin privileges? [y/N]: ").strip().lower()
        is_admin = make_admin == 'y'
        
        # Confirm
        print("\n" + "-" * 60)
        print("Confirm user details:")
        print(f"  Username: {username}")
        print(f"  Email: {email}")
        print(f"  Full Name: {fullname if fullname else '(not set)'}")
        print(f"  Password: {'*' * len(password)}")
        print(f"  Admin: {'Yes' if is_admin else 'No'}")
        print("-" * 60)
        
        confirm = input("\nCreate this user? [Y/n]: ").strip().lower()
        
        if confirm == 'n':
            print("\n❌ User creation cancelled.")
            return False
        
        # Create user
        try:
            user = User(username=username, email=email)
            if fullname:
                user.fullname = fullname
            user.is_admin = is_admin
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            admin_status = " (admin)" if is_admin else ""
            print(f"\n✅ User '{username}'{admin_status} created successfully!")
            return True
        except Exception as e:
            print(f"\n❌ Error creating user: {e}")
            db.session.rollback()
            return False

def reset_admin_password(user):
    """Reset the admin user password"""
    from app import app, db
    
    with app.app_context():
        print("\n\nResetting admin password")
        print("-" * 60)
        print(f"Current admin user: {user.username}")
        
        # Verify current password
        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts:
            current_password = getpass.getpass("Enter current password to verify: ")
            
            if user.check_password(current_password):
                print("✓ Password verified")
                break
            else:
                attempts += 1
                remaining = max_attempts - attempts
                print(f"✗ Incorrect password. Attempts remaining: {remaining}")
                
                if attempts >= max_attempts:
                    print("\n❌ Too many failed attempts. Exiting.")
                    return False
        
        # Get new password
        new_password = get_valid_password("new")
        
        # Confirm
        print("\n" + "-" * 60)
        print("Password change summary:")
        print(f"  Username: {user.username}")
        print(f"  New password: {'*' * len(new_password)}")
        print("-" * 60)
        
        confirm = input("\nChange password? [Y/n]: ").strip().lower()
        
        if confirm == 'n':
            print("\n❌ Password change cancelled.")
            return False
        
        # Update password
        try:
            user.set_password(new_password)
            db.session.commit()
            print(f"\n✅ Password for '{user.username}' updated successfully!")
            return True
        except Exception as e:
            print(f"\n❌ Error updating password: {e}")
            db.session.rollback()
            return False

def get_valid_username():
    """Get and validate username"""
    from app import app, db
    from app.models import User
    
    while True:
        username = input("\nUsername: ").strip()
        
        # Validation
        if not username:
            print("❌ Username cannot be empty")
            continue
        
        if len(username) < 3:
            print("❌ Username must be at least 3 characters")
            continue
        
        if len(username) > 64:
            print("❌ Username must be at most 64 characters")
            continue
        
        if not username.replace('_', '').replace('-', '').isalnum():
            print("❌ Username can only contain letters, numbers, _, and -")
            continue
        
        # Check uniqueness
        with app.app_context():
            existing = User.query.filter_by(username=username).first()
            if existing:
                print(f"❌ Username '{username}' already exists")
                continue
        
        print(f"✓ Username '{username}' is valid")
        return username

def get_valid_email(username=''):
    """Get and validate email"""
    from app import app, db
    from app.models import User
    import re
    
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    while True:
        email = input("\nEmail: ").strip()
        
        # Validation
        if not email:
            print("❌ Email cannot be empty")
            continue
        
        if not re.match(email_regex, email):
            print("❌ Invalid email format")
            continue
        
        if len(email) > 120:
            print("❌ Email must be at most 120 characters")
            continue
        
        # Check uniqueness
        with app.app_context():
            existing = User.query.filter_by(email=email).first()
            if existing:
                print(f"❌ Email '{email}' is already registered")
                continue
        
        print(f"✓ Email '{email}' is valid")
        return email

def get_valid_password(type_desc=''):
    """Get and validate password"""
    password_label = f"{type_desc} password" if type_desc else "password"
    
    while True:
        password = getpass.getpass(f"\nEnter {password_label}: ")
        
        if not password:
            print("❌ Password cannot be empty")
            continue
        
        if len(password) < 8:
            print("❌ Password must be at least 8 characters")
            continue
        
        if len(password) > 128:
            print("❌ Password must be at most 128 characters")
            continue
        
        # Confirm password
        password_confirm = getpass.getpass(f"Confirm {password_label}: ")
        
        if password != password_confirm:
            print("❌ Passwords do not match")
            continue
        
        print(f"✓ Password is valid (strength: moderate)")
        return password

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)
