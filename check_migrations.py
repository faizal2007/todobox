#!/usr/bin/env python3
"""
Migration Diagnostic and Fix Script
Checks database schema against SQLAlchemy models
"""

import sys
import click
from sqlalchemy import inspect
from flask import current_app


def check_schema_alignment():
    """Check if database schema matches SQLAlchemy model definitions"""
    from app import db
    from app.models import User, Todo, Status, Tracker
    
    inspector = inspect(db.engine)
    
    issues = []
    
    # Check User table
    print("\n📋 Checking 'user' table schema...")
    user_columns = {col['name']: col for col in inspector.get_columns('user')} # type: ignore
    
    expected_columns = {
        'id': 'INTEGER',
        'username': 'VARCHAR',
        'email': 'VARCHAR',
        'fullname': 'VARCHAR',
        'password_hash': 'VARCHAR',
        'api_token': 'VARCHAR',
        'oauth_provider': 'VARCHAR',
        'oauth_id': 'VARCHAR',
    }
    
    for col_name, col_type in expected_columns.items():
        if col_name not in user_columns:
            issues.append(f"❌ Missing column: user.{col_name}")
            print(f"  ❌ Missing: {col_name} ({col_type})")
        else:
            print(f"  ✅ Found: {col_name} ({user_columns[col_name]['type']})")
    
    # Check indexes
    print("\n🔍 Checking indexes...")
    indexes = {idx['name']: idx for idx in inspector.get_indexes('user')} # pyright: ignore[reportOptionalMemberAccess]
    
    required_indexes = ['ix_user_username', 'ix_user_email', 'ix_user_api_token']
    for idx_name in required_indexes:
        if idx_name in indexes:
            print(f"  ✅ Found: {idx_name}")
        else:
            print(f"  ⚠️  Missing: {idx_name}")
    
    # Summary
    print("\n" + "="*60)
    if issues:
        print(f"❌ Found {len(issues)} schema issues:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("✅ Schema is aligned with models")
        return True


def show_migration_history():
    """Display migration history"""
    from flask_migrate import Migrate
    import os
    
    print("\n📜 Migration History:")
    print("="*60)
    
    versions_dir = os.path.join(os.path.dirname(__file__), 'migrations', 'versions')
    if os.path.exists(versions_dir):
        files = sorted([f for f in os.listdir(versions_dir) if f.endswith('.py')])
        for i, f in enumerate(files, 1):
            print(f"{i}. {f}")
    else:
        print("No migrations directory found")


def show_database_schema():
    """Display current database schema"""
    from app import db
    from sqlalchemy import text
    
    print("\n📊 Current Database Schema:")
    print("="*60)
    
    try:
        # Get database type
        db_url = str(db.engine.url) # pyright: ignore[reportOptionalMemberAccess]
        if 'mysql' in db_url:
            print(f"Database: MySQL")
            
            # Show user table structure
            result = db.session.execute( # pyright: ignore[reportAttributeAccessIssue]
                text("DESCRIBE user")
            ).fetchall()
            
            print("\nTable: user")
            print("-" * 60)
            print(f"{'Field':<20} {'Type':<30} {'Key':<5}")
            print("-" * 60)
            
            for row in result:
                field, col_type, null, key, default, extra = row
                key_str = key if key else ""
                print(f"{field:<20} {col_type:<30} {key_str:<5}")
        
        elif 'sqlite' in db_url:
            print(f"Database: SQLite")
            
            result = db.session.execute( # pyright: ignore[reportAttributeAccessIssue]
                text("PRAGMA table_info(user)")
            ).fetchall()
            
            print("\nTable: user")
            print("-" * 60)
            print(f"{'Name':<20} {'Type':<20} {'Nullable':<10}")
            print("-" * 60)
            
            for cid, name, col_type, notnull, dflt_value, pk in result:
                nullable = "NO" if notnull else "YES"
                print(f"{name:<20} {col_type:<20} {nullable:<10}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


@click.group()
def cli():
    """Migration diagnostic and fix commands"""
    pass


@cli.command()
def check():
    """Check if database schema matches models"""
    try:
        result = check_schema_alignment()
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"❌ Error checking schema: {e}")
        sys.exit(1)


@cli.command()
def history():
    """Show migration history"""
    show_migration_history()


@cli.command()
def schema():
    """Show current database schema"""
    show_database_schema()


@cli.command()
def report():
    """Full diagnostic report"""
    print("\n" + "="*60)
    print("🔧 Migration Diagnostic Report")
    print("="*60)
    
    show_migration_history()
    show_database_schema()
    check_schema_alignment()
    
    print("\n" + "="*60)
    print("✅ Report complete")
    print("="*60)


if __name__ == '__main__':
    cli()
