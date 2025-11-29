#!/usr/bin/env python3
"""
Interactive user management script for TodoBox
Usage: python3 todomanage.py
"""

import sys
import getpass
import secrets
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main menu for user management"""
    
    print("\n" + "="*60)
    print("  TodoBox - User Management".center(60))
    print("="*60 + "\n")
    
    while True:
        print("\nOptions:")
        print("  1) Create user")
        print("  2) List users")
        print("  3) Assign user to admin")
        print("  4) Delete user")
        print("  5) Generate SECRET_KEY and SALT")
        print("  6) Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            create_user()
        elif choice == '2':
            list_users()
        elif choice == '3':
            assign_admin()
        elif choice == '4':
            delete_user()
        elif choice == '5':
            generate_secrets()
        elif choice == '6':
            print("\n✅ Exiting.\n")
            sys.exit(0)
        else:
            print("\n❌ Invalid option. Please select 1-6.")

def create_user():
    """Create a new user with optional admin privileges"""
    from app import app, db
    from app.models import User
    
    with app.app_context():
        print("\n\n" + "-"*60)
        print("  Create New User")
        print("-"*60)
        
        username = get_valid_username()
        email = get_valid_email()
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

def list_users():
    """List all users in the database"""
    from app import app, db
    from app.models import User
    
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("\n⚠️  No users found in database.")
            return
        
        print("\n\n" + "="*80)
        print("  Users".center(80))
        print("="*80)
        print(f"{'ID':<5} {'Username':<15} {'Email':<25} {'Full Name':<15} {'Admin':<6} {'Blocked':<8}")
        print("-"*80)
        
        for user in users:
            fullname = user.fullname or '(not set)'
            email = user.email or '(no email)'
            is_admin = 'Yes' if user.is_system_admin() else 'No'
            is_blocked = 'Yes' if user.is_blocked else 'No'
            print(f"{user.id:<5} {user.username:<15} {email:<25} {fullname:<15} {is_admin:<6} {is_blocked:<8}")
        
        print("="*80)
        print(f"\nTotal users: {len(users)}")

def assign_admin():
    """Assign or remove admin privileges for a user"""
    from app import app, db
    from app.models import User
    
    with app.app_context():
        print("\n\n" + "-"*60)
        print("  Assign User to Admin")
        print("-"*60)
        
        # Get username
        username = input("\nEnter username: ").strip()
        
        if not username:
            print("\n❌ Username cannot be empty.")
            return False
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"\n❌ User '{username}' not found.")
            return False
        
        # Show current status
        current_admin = user.is_system_admin()
        print(f"\nUser: {user.username}")
        print(f"Email: {user.email or '(no email)'}")
        print(f"Current admin status: {'Yes' if current_admin else 'No'}")
        
        # Ask for new status
        if current_admin:
            action = input("\nRemove admin privileges? [y/N]: ").strip().lower()
            new_admin = action != 'y'
        else:
            action = input("\nAssign admin privileges? [Y/n]: ").strip().lower()
            new_admin = action != 'n'
        
        # No change needed
        if new_admin == user.is_system_admin():
            print("\n⚠️  No change needed.")
            return False
        
        # Confirm
        action_desc = "assign admin to" if new_admin else "remove admin from"
        if not input(f"\nConfirm {action_desc} user '{username}'? [Y/n]: ").strip().lower() == 'n':
            # Update user
            try:
                user.is_admin = new_admin
                db.session.commit()
                
                status = "assigned" if new_admin else "removed"
                print(f"\n✅ Admin privileges {status} for user '{username}'!")
                return True
            except Exception as e:
                print(f"\n❌ Error updating user: {e}")
                db.session.rollback()
                return False
        else:
            print("\n❌ Operation cancelled.")
            return False

def delete_user():
    """Delete a user from the database"""
    from app import app, db
    from app.models import User
    
    with app.app_context():
        print("\n\n" + "-"*60)
        print("  Delete User")
        print("-"*60)
        
        # Get username
        username = input("\nEnter username to delete: ").strip()
        
        if not username:
            print("\n❌ Username cannot be empty.")
            return False
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"\n❌ User '{username}' not found.")
            return False
        
        # Show user details
        print(f"\nUser details:")
        print(f"  ID: {user.id}")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email or '(no email)'}")
        print(f"  Full Name: {user.fullname or '(not set)'}")
        print(f"  Admin: {'Yes' if user.is_system_admin() else 'No'}")
        
        # Confirm deletion
        print("\n⚠️  WARNING: This action cannot be undone!")
        confirm = input(f"\nAre you sure you want to delete user '{username}'? [y/N]: ").strip().lower()
        
        if confirm != 'y':
            print("\n❌ User deletion cancelled.")
            return False
        
        # Double confirm for admin users
        if user.is_system_admin():
            print("\n⚠️  WARNING: This user has admin privileges!")
            confirm2 = input("Type 'DELETE' to confirm: ").strip()
            if confirm2 != 'DELETE':
                print("\n❌ User deletion cancelled.")
                return False
        
        # Delete user
        try:
            db.session.delete(user)
            db.session.commit()
            print(f"\n✅ User '{username}' deleted successfully!")
            return True
        except Exception as e:
            print(f"\n❌ Error deleting user: {e}")
            db.session.rollback()
            return False

def generate_secrets():
    """Generate cryptographically secure SECRET_KEY and SALT"""
    
    print("\n\n" + "-"*60)
    print("  Generate SECRET_KEY and SALT")
    print("-"*60)
    
    # Generate secure random values
    secret_key = secrets.token_hex(32)  # 64 character hex string (256 bits)
    salt = secrets.token_hex(16)  # 32 character hex string (128 bits)
    
    print("\n⚠️  IMPORTANT: Store these values securely!")
    print("   These values should be set in your .flaskenv file.")
    print("   Never commit these values to version control.\n")
    
    print("-" * 60)
    print("Generated values:\n")
    print(f"SECRET_KEY={secret_key}")
    print(f"SALT={salt}")
    print("-" * 60)
    
    # Ask if user wants to see the instructions
    show_help = input("\nShow instructions for updating .flaskenv? [y/N]: ").strip().lower()
    
    if show_help == 'y':
        print("\n" + "="*60)
        print("  Instructions")
        print("="*60)
        print("""
1. Open or create your .flaskenv file in the project root

2. Add or update these lines:
   SECRET_KEY=<your_generated_secret_key>
   SALT=<your_generated_salt>

3. Make sure .flaskenv is in your .gitignore file

4. For production, use environment variables instead of .flaskenv

Example .flaskenv:
   FLASK_APP=todobox.py
   SECRET_KEY={secret_key}
   SALT={salt}
   DATABASE_DEFAULT=sqlite
   DATABASE_NAME=todobox.db
""".format(secret_key=secret_key, salt=salt))
    
    print("\n✅ Secret generation complete!")
    return True

def get_valid_username():
    """Get and validate username"""
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
        existing = User.query.filter_by(username=username).first()
        if existing:
            print(f"❌ Username '{username}' already exists")
            continue
        
        print(f"✓ Username '{username}' is valid")
        return username

def get_valid_email():
    """Get and validate email"""
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
        existing = User.query.filter_by(email=email).first()
        if existing:
            print(f"❌ Email '{email}' is already registered")
            continue
        
        print(f"✓ Email '{email}' is valid")
        return email

def get_valid_password():
    """Get and validate password"""
    while True:
        password = getpass.getpass("\nEnter password: ")
        
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
        password_confirm = getpass.getpass("Confirm password: ")
        
        if password != password_confirm:
            print("❌ Passwords do not match")
            continue
        
        print("✓ Password is valid (strength: moderate)")
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
