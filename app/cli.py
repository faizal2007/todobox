"""
Flask CLI commands for user management
Add this to app/cli.py
"""

import click
import getpass
from app import db
from app.models import User

def create_cli(app):
    """Register CLI commands with Flask app"""
    
    @app.cli.command()
    @click.option('--username', prompt=False, help='Username')
    @click.option('--email', prompt=False, help='Email address')
    @click.option('--password', prompt=False, help='Password (will be prompted if not provided)')
    def create_user(username, email, password):
        """Create a new user (interactive prompt)"""
        
        click.echo("\n" + "="*60)
        click.echo("  MySandbox - User Creation".center(60))
        click.echo("="*60 + "\n")
        
        # Get username if not provided
        if not username:
            while True:
                username = click.prompt('Username').strip()
                if len(username) < 3:
                    click.echo('❌ Username must be at least 3 characters')
                    continue
                existing = User.query.filter_by(username=username).first()
                if existing:
                    click.echo(f'❌ Username "{username}" already exists')
                    continue
                break
        
        # Get email if not provided
        if not email:
            while True:
                email = click.prompt('Email').strip()
                existing = User.query.filter_by(email=email).first()
                if existing:
                    click.echo(f'❌ Email "{email}" already registered')
                    continue
                break
        
        # Get password if not provided
        if not password:
            while True:
                password = click.prompt('Password', hide_input=True, confirmation_prompt=True)
                if len(password) < 8:
                    click.echo('❌ Password must be at least 8 characters')
                    continue
                break
        
        # Show confirmation
        click.echo("\n" + "-"*60)
        click.echo("Confirm user details:")
        click.echo(f"  Username: {username}")
        click.echo(f"  Email: {email}")
        click.echo("-"*60)
        
        if not click.confirm('\nCreate this user?'):
            click.echo('❌ User creation cancelled.')
            return
        
        # Create user
        try:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            click.echo(f'\n✅ User "{username}" created successfully!')
            click.echo("="*60 + "\n")
            
        except Exception as e:
            click.echo(f'\n❌ Error creating user: {e}')
            db.session.rollback()
    
    @app.cli.command()
    @click.option('--username', default='admin', prompt=False, help='Username to reset')
    def reset_password(username):
        """Reset user password"""
        
        user = User.query.filter_by(username=username).first()
        if not user:
            click.echo(f'❌ User "{username}" not found')
            return
        
        click.echo(f'\n📝 Resetting password for user: {username}')
        
        # Verify identity
        current_password = click.prompt('Enter current password to verify', hide_input=True)
        if not user.check_password(current_password):
            click.echo('❌ Incorrect password')
            return
        
        # Get new password
        while True:
            new_password = click.prompt('New password', hide_input=True, confirmation_prompt=True)
            if len(new_password) < 8:
                click.echo('❌ Password must be at least 8 characters')
                continue
            break
        
        # Update password
        try:
            user.set_password(new_password)
            db.session.commit()
            click.echo(f'✅ Password for "{username}" updated successfully!')
            
        except Exception as e:
            click.echo(f'❌ Error updating password: {e}')
            db.session.rollback()
    
    @app.cli.command()
    def list_users():
        """List all users in the database"""
        
        users = User.query.all()
        
        if not users:
            click.echo('No users found')
            return
        
        click.echo("\n" + "="*60)
        click.echo("  Users".center(60))
        click.echo("="*60)
        click.echo(f"{'ID':<5} {'Username':<20} {'Email':<25} {'Full Name':<15}")
        click.echo("-"*60)
        
        for user in users:
            fullname = user.fullname or '(not set)'
            click.echo(f"{user.id:<5} {user.username:<20} {user.email:<25} {fullname:<15}")
        
        click.echo("="*60 + "\n")
    
    @app.cli.command()
    @click.option('--username', prompt=True, help='Username to delete')
    def delete_user(username):
        """Delete a user from the database"""
        
        user = User.query.filter_by(username=username).first()
        if not user:
            click.echo(f'❌ User "{username}" not found')
            return
        
        if not click.confirm(f'\n⚠️  Are you sure you want to delete user "{username}"? This cannot be undone.'):
            click.echo('❌ User deletion cancelled.')
            return
        
        try:
            db.session.delete(user)
            db.session.commit()
            click.echo(f'✅ User "{username}" deleted successfully!')
            
        except Exception as e:
            click.echo(f'❌ Error deleting user: {e}')
            db.session.rollback()
