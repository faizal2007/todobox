#!/usr/bin/env python3
"""
Interactive user management script for TodoBox
Usage: python3 todomanage.py
"""

import re
import sys
import getpass
import secrets
from pathlib import Path
import time
import psycopg2
import pymysql

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def wait_for_database(db_type, host, port, user, password, database, max_attempts=30):
    """Wait for database to be ready to accept connections."""
    print(f"⏳ Waiting for {db_type} database to be ready...")
    
    for attempt in range(max_attempts):
        try:
            if db_type == 'postgres':
                conn = psycopg2.connect(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database=database,
                    connect_timeout=5
                )
                conn.close()
            elif db_type == 'mysql':
                # Try connecting as root first (MariaDB creates root user)
                try:
                    conn = pymysql.connect(
                        host=host,
                        port=port,
                        user='root',
                        password=password,
                        connect_timeout=5
                    )
                    conn.close()
                except Exception:
                    # If root connection fails, try as the specified user
                    conn = pymysql.connect(
                        host=host,
                        port=port,
                        user=user,
                        password=password,
                        database=database,
                        connect_timeout=5
                    )
                    conn.close()
            
            print("✅ Database is ready!")
            return True
            
        except Exception as e:
            print(f"  Attempt {attempt + 1}/{max_attempts}: Database not ready yet... ({str(e)[:50]}...)")
            time.sleep(2)
    
    print(f"❌ Database failed to become ready after {max_attempts} attempts")
    return False

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
        print("  5) Install")
        print("  6) Run")
        print("  7) Generate SECRET_KEY and SALT")
        print("  8) Uninstall and cleanup")
        print("  9) Exit")
        
        choice = input("\nSelect option (1-9): ").strip()
        
        if choice == '1':
            create_user()
        elif choice == '2':
            list_users()
        elif choice == '3':
            assign_admin()
        elif choice == '4':
            delete_user()
        elif choice == '5':
            install_database()
        elif choice == '6':
            run_todobox()
        elif choice == '7':
            generate_secrets()
        elif choice == '8':
            uninstall_and_cleanup()
        elif choice == '9':
            print("\n✅ Exiting.\n")
            sys.exit(0)
        else:
            print("\n❌ Invalid option. Please select 1-9.")

def run_todobox():
    """Run the TodoBox Flask application"""
    import subprocess
    import os
    
    print("\n\n" + "="*60)
    print("  Starting TodoBox Application".center(60))
    print("="*60 + "\n")
    
    project_dir = os.path.dirname(__file__)
    
    # Check if .flaskenv exists
    flaskenv_file = os.path.join(project_dir, '.flaskenv')
    if not os.path.exists(flaskenv_file):
        print("❌ .flaskenv not found. Please run the Install option first.")
        return False
    
    # Check if database is initialized
    db_type_result = subprocess.run(
        ["grep", "DATABASE_DEFAULT", flaskenv_file],
        capture_output=True,
        text=True
    )
    
    if "sqlite" in db_type_result.stdout:
        db_file = os.path.join(project_dir, 'instance', 'todobox.db')
        if not os.path.exists(db_file):
            print("❌ SQLite database not found. Please run the Install option first.")
            return False
    
    print("📝 Configuration loaded from .flaskenv")
    print("🗄️  Database connection verified")
    
    print("\n" + "-"*60)
    print("Starting Flask development server...")
    print("-"*60 + "\n")
    
    print("ℹ️  Press Ctrl+C to stop the server\n")
    
    try:
        # Run Flask app
        subprocess.run(
            ["python", "todobox.py"],
            cwd=project_dir
        )
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped by user.")
        return True
    except Exception as e:
        print(f"\n❌ Error running application: {e}")
        return False

def install_database():
    """Install and initialize complete TodoBox system with database selection"""
    import subprocess
    import os
    import shutil
    
    print("\n\n" + "="*60)
    print("  TodoBox Installation Method".center(60))
    print("="*60)
    
    print("\nSelect installation method:")
    print("  1) Manual Installation (configure database yourself)")
    print("  2) Database Docker Installation (automated setup)")
    
    install_choice = input("\nSelect method (1-2) [1]: ").strip() or "1"
    
    if install_choice == "1":
        return install_manual()
    elif install_choice == "2":
        return install_docker()
    else:
        print("\n❌ Invalid selection. Please select 1 or 2.")
        return False

def uninstall_and_cleanup():
    """Uninstall TodoBox and cleanup configuration"""
    import subprocess
    import os
    import shutil
    
    print("\n\n" + "="*60)
    print("  TodoBox Uninstall and Cleanup".center(60))
    print("="*60)
    
    project_dir = os.path.dirname(__file__)
    
    # Check if docker-compose.yml exists (indicates Docker installation)
    docker_compose_file = os.path.join(project_dir, 'docker-compose.yml')
    if os.path.exists(docker_compose_file):
        print("\n🐳 Docker installation detected. Stopping and removing containers...")
        
        # Stop and remove containers
        try:
            result = subprocess.run(
                ["docker-compose", "down"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                print("✅ Docker containers stopped and removed")
            else:
                print(f"⚠️  Warning: Failed to stop containers: {result.stderr}")
        except Exception as e:
            print(f"⚠️  Warning: Error stopping containers: {e}")
        
        # Remove volumes
        try:
            result = subprocess.run(
                ["docker", "volume", "ls", "-q"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                volumes = [v for v in result.stdout.strip().split('\n') if v.startswith('todobox_')]
                if volumes:
                    print(f"Removing volumes: {', '.join(volumes)}")
                    result = subprocess.run(
                        ["docker", "volume", "rm"] + volumes,
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        print("✅ Docker volumes removed")
                    else:
                        print(f"⚠️  Warning: Failed to remove volumes: {result.stderr}")
        except Exception as e:
            print(f"⚠️  Warning: Error removing volumes: {e}")
        
        # Remove docker-compose.yml
        try:
            os.remove(docker_compose_file)
            print("✅ docker-compose.yml removed")
        except Exception as e:
            print(f"⚠️  Warning: Failed to remove docker-compose.yml: {e}")
    
    # Remove .flaskenv
    flaskenv_file = os.path.join(project_dir, '.flaskenv')
    if os.path.exists(flaskenv_file):
        try:
            os.remove(flaskenv_file)
            print("✅ .flaskenv removed")
        except Exception as e:
            print(f"⚠️  Warning: Failed to remove .flaskenv: {e}")
    
    # Remove instance directory
    instance_dir = os.path.join(project_dir, 'instance')
    if os.path.exists(instance_dir):
        try:
            shutil.rmtree(instance_dir)
            print("✅ instance/ directory removed")
        except Exception as e:
            print(f"⚠️  Warning: Failed to remove instance/ directory: {e}")
    
    # Remove __pycache__ directories
    for root, dirs, files in os.walk(project_dir):
        if '__pycache__' in dirs:
            pycache_dir = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_dir)
                print(f"✅ Removed {os.path.relpath(pycache_dir, project_dir)}")
            except Exception as e:
                print(f"⚠️  Warning: Failed to remove {pycache_dir}: {e}")
    
    print("\n✅ TodoBox uninstall and cleanup completed!")
    print("\nNote: Database data may still exist if using external databases.")
    print("      Manual cleanup may be required for external databases.")

def install_manual():
    """Manual installation - user sets up database themselves"""
    import subprocess
    import os
    import shutil
    
    print("\n\n" + "="*60)
    print("  TodoBox Manual Installation".center(60))
    print("="*60)
    
    print("\n📚 For detailed installation instructions, see:")
    print("   - docs/README.md       (documentation index)")
    print("   - docs/SETUP.md        (complete setup guide)")
    print("   - docs/QUICKSTART.md   (quick reference)")
    print("   - README.md            (quick start guide)")
    
    # Database selection
    print("\n" + "-"*60)
    print("Database Selection")
    print("-"*60)
    print("\nSelect database type:")
    print("  1) SQLite (default)")
    print("  2) MariaDB")
    print("  3) PostgreSQL")
    
    db_choice = input("\nSelect database (1-3) [1]: ").strip() or "1"
    
    db_config = {
        "1": ("sqlite", "SQLite"),
        "2": ("mysql", "MariaDB"),
        "3": ("postgres", "PostgreSQL")
    }
    
    if db_choice not in db_config:
        print("\n❌ Invalid selection. Please select 1-3.")
        return False
    
    db_type, db_name = db_config[db_choice]
    
    print(f"\n✓ Selected: {db_name}")
    
    # For non-SQLite databases, collect connection details
    if db_type != "sqlite":
        print("\n" + "-"*60)
        print(f"  {db_name} Configuration")
        print("-"*60)
        
        db_url = input("\nDatabase URL/Host [localhost]: ").strip() or "localhost"
        db_user = input("Database User [root]: ").strip() or "root"
        db_password = getpass.getpass("Database Password: ")
        db_database = input("Database Name [todobox]: ").strip() or "todobox"
        
        # Store configuration temporarily
        os.environ['DB_URL'] = db_url
        os.environ['DB_USER'] = db_user
        os.environ['DB_PW'] = db_password
        os.environ['DB_NAME'] = db_database
    
    # Encryption configuration
    print("\n" + "-"*60)
    print("Todo Encryption Configuration")
    print("-"*60)
    print("\nTodo encryption protects your todo data (names and details) from")
    print("being readable by database administrators. When enabled, only you")
    print("can read your todo content.")
    print("\n⚠️  Note: Once enabled, encryption cannot be easily disabled.")
    print("   Make sure you remember your SECRET_KEY and SALT values.")
    
    encryption_choice = input("\nEnable todo encryption? [y/N]: ").strip().lower()
    enable_encryption = encryption_choice in ['y', 'yes']
    
    if enable_encryption:
        print("✓ Todo encryption will be enabled")
    else:
        print("✓ Todo encryption will remain disabled (default)")
    
    project_dir = os.path.dirname(__file__)
    
    # Step 1: Install dependencies
    print("\n" + "-"*60)
    print("Step 1: Installing Python dependencies...")
    print("-"*60)
    
    requirements_file = os.path.join(project_dir, 'requirements.txt')
    if not os.path.exists(requirements_file):
        print("❌ requirements.txt not found")
        return False
    
    try:
        result = subprocess.run(
            ["pip", "install", "-r", "requirements.txt"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✅ Python dependencies installed successfully")
        else:
            print(f"❌ Dependency installation failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Dependency installation timed out")
        return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    
    # Step 2: Setup environment variables
    print("\n" + "-"*60)
    print("Step 2: Setting up environment variables...")
    print("-"*60)
    
    flaskenv_file = os.path.join(project_dir, '.flaskenv')
    flaskenv_example = os.path.join(project_dir, '.flaskenv.example')
    
    if os.path.exists(flaskenv_file):
        print("✓ .flaskenv already exists")
        update_flaskenv(flaskenv_file, db_type, db_url if db_type != "sqlite" else None, 
                       db_user if db_type != "sqlite" else None,
                       db_password if db_type != "sqlite" else None,
                       db_database if db_type != "sqlite" else None,
                       enable_encryption)
    elif os.path.exists(flaskenv_example):
        try:
            shutil.copy2(flaskenv_example, flaskenv_file)
            print("✅ .flaskenv created from .flaskenv.example")
            update_flaskenv(flaskenv_file, db_type, db_url if db_type != "sqlite" else None,
                           db_user if db_type != "sqlite" else None,
                           db_password if db_type != "sqlite" else None,
                           db_database if db_type != "sqlite" else None,
                           enable_encryption)
        except Exception as e:
            print(f"❌ Error copying .flaskenv: {e}")
            return False
    else:
        print("⚠️  .flaskenv.example not found, skipping environment setup")
    
    # Step 3: Create instance directory (for SQLite)
    if db_type == "sqlite":
        print("\n" + "-"*60)
        print("Step 3: Creating instance directory...")
        print("-"*60)
        
        instance_dir = os.path.join(project_dir, 'instance')
        if not os.path.exists(instance_dir):
            try:
                os.makedirs(instance_dir, exist_ok=True)
                print("✅ Instance directory created")
            except Exception as e:
                print(f"❌ Error creating instance directory: {e}")
                return False
        else:
            print("✓ Instance directory exists")
    
    # Step 4: Run database migrations
    print("\n" + "-"*60)
    print("Step 4: Running database migrations...")
    print("-"*60)
    
    env = os.environ.copy()
    env['DATABASE_DEFAULT'] = db_type
    if db_type != "sqlite":
        env['DB_URL'] = db_url
        env['DB_USER'] = db_user
        env['DB_PW'] = db_password
        env['DB_NAME'] = db_database
    
    try:
        result = subprocess.run(
            ["python", "-m", "flask", "db", "upgrade"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=60,
            env=env
        )
        
        if result.returncode == 0:
            print(f"✅ Database migrations completed successfully ({db_name})")
            
            if db_type == "sqlite":
                db_file = os.path.join(project_dir, 'instance', 'todobox.db')
                if os.path.exists(db_file):
                    size_kb = os.path.getsize(db_file) / 1024
                    print(f"✅ Database file created: {db_file} ({size_kb:.1f} KB)")
            
            print("\n" + "="*60)
            print("Installation Summary".center(60))
            print("="*60)
            print(f"""
✅ TodoBox manual installation completed successfully!

Database: {db_name}
""")
            if db_type != "sqlite":
                print(f"Host: {db_url}")
                print(f"User: {db_user}")
                print(f"Database: {db_database}")
            
            print("""
Next steps:

1. CREATE FIRST ADMIN USER
   Select option 1 from main menu and create your first admin user
   
2. RUN THE APPLICATION
   Select option 6 (Run) from main menu
   or
   python todobox.py
   or
   flask run
   
3. ACCESS THE APPLICATION
   Open your browser: http://localhost:9191
   
4. LOGIN
   Use the admin credentials you just created

Configuration:
   - Edit .flaskenv for custom settings
""")
            if db_type != "sqlite":
                print("   - Database credentials saved in .flaskenv")
            
            print("""
For more information:
   - docs/USER_CREATION.md    (user creation guide)
   - docs/OAUTH_SETUP.md      (Google OAuth configuration)
   - docs/DEPLOYMENT.md       (deployment options)
   - README.md                (quick reference)
""")
            print("="*60)
            
            # Automatically generate SECRET_KEY and SALT after installation
            print("\n🔐 Generating secure SECRET_KEY and SALT...")
            generate_secrets()
            
            return True
        else:
            print(f"❌ Migration failed:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ Migration process timed out")
        return False
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False

def install_docker():
    """Docker installation - create docker-compose setup"""
    import os
    
    print("\n\n" + "="*60)
    print("  TodoBox Docker Installation".center(60))
    print("="*60)
    
    print("\nSelect database type:")
    print("  1) SQLite (default - no container needed)")
    print("  2) MariaDB (with Docker container)")
    print("  3) PostgreSQL (with Docker container)")
    
    db_choice = input("\nSelect database (1-3) [1]: ").strip() or "1"
    
    db_config = {
        "1": ("sqlite", "SQLite"),
        "2": ("mysql", "MariaDB"),
        "3": ("postgres", "PostgreSQL")
    }
    
    if db_choice not in db_config:
        print("\n❌ Invalid selection. Please select 1-3.")
        return False
    
    db_type, db_name = db_config[db_choice]
    
    print(f"\n✓ Selected: {db_name}")
    
    # Encryption configuration
    print("\n" + "-"*60)
    print("Todo Encryption Configuration")
    print("-"*60)
    print("\nTodo encryption protects your todo data (names and details) from")
    print("being readable by database administrators. When enabled, only you")
    print("can read your todo content.")
    print("\n⚠️  Note: Once enabled, encryption cannot be easily disabled.")
    print("   Make sure you remember your SECRET_KEY and SALT values.")
    
    encryption_choice = input("\nEnable todo encryption? [y/N]: ").strip().lower()
    enable_encryption = encryption_choice in ['y', 'yes']
    
    if enable_encryption:
        print("✓ Todo encryption will be enabled")
    else:
        print("✓ Todo encryption will remain disabled (default)")
    
    project_dir = os.path.dirname(__file__)
    
    if db_type == "sqlite":
        return setup_sqlite_docker(project_dir, enable_encryption)
    elif db_type == "mysql":
        return setup_mariadb_docker(project_dir, enable_encryption)
    elif db_type == "postgres":
        return setup_postgres_docker(project_dir, enable_encryption)
    
    return False

def setup_sqlite_docker(project_dir, enable_encryption=False):
    """Setup SQLite with Docker"""
    import subprocess
    import os
    
    print("\n" + "-"*60)
    print("SQLite Docker Setup")
    print("-"*60)
    
    # Create .flaskenv
    flaskenv_file = os.path.join(project_dir, '.flaskenv')
    flaskenv_example = os.path.join(project_dir, '.flaskenv.example')
    
    if not os.path.exists(flaskenv_file) and os.path.exists(flaskenv_example):
        import shutil
        try:
            shutil.copy2(flaskenv_example, flaskenv_file)
            print("✅ .flaskenv created from .flaskenv.example")
            update_flaskenv(flaskenv_file, "sqlite", enable_encryption=enable_encryption)
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    # Create instance directory
    instance_dir = os.path.join(project_dir, 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    
    # Run migrations
    print("\nRunning database migrations...")
    try:
        result = subprocess.run(
            ["python", "-m", "flask", "db", "upgrade"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=60,
            env={**os.environ, 'DATABASE_DEFAULT': 'sqlite'}
        )
        
        if result.returncode == 0:
            print("✅ SQLite database initialized")
            return show_docker_summary("SQLite")
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def setup_mariadb_docker(project_dir, enable_encryption=False):
    """Setup MariaDB with Docker"""
    import subprocess
    import os
    
    print("\n" + "-"*60)
    print("MariaDB Docker Configuration")
    print("-"*60)
    
    # Get configuration
    db_user = input("\nDatabase User [todobox]: ").strip() or "todobox"
    db_password = getpass.getpass("Database Password [todobox123]: ") or "todobox123"
    db_name = input("Database Name [todobox]: ").strip() or "todobox"
    container_name = input("Container Name [todobox-mariadb]: ").strip() or "todobox-mariadb"
    port = input("Port [3306]: ").strip() or "3306"
    
    # Create docker-compose.yml
    docker_compose = f"""version: '3.8'

services:
  mariadb:
    image: mariadb:latest
    container_name: {container_name}
    environment:
      MYSQL_ROOT_PASSWORD: {db_password}
      MYSQL_USER: {db_user}
      MYSQL_PASSWORD: {db_password}
      MYSQL_DATABASE: {db_name}
    ports:
      - "{port}:3306"
    volumes:
      - mariadb_data:/var/lib/mysql
    restart: unless-stopped

volumes:
  mariadb_data:
"""
    
    docker_compose_file = os.path.join(project_dir, 'docker-compose.yml')
    try:
        with open(docker_compose_file, 'w') as f:
            f.write(docker_compose)
        print(f"✅ docker-compose.yml created")
    except Exception as e:
        print(f"❌ Error creating docker-compose.yml: {e}")
        return False
    
    # Create .flaskenv
    flaskenv_file = os.path.join(project_dir, '.flaskenv')
    flaskenv_example = os.path.join(project_dir, '.flaskenv.example')
    
    if not os.path.exists(flaskenv_file) and os.path.exists(flaskenv_example):
        import shutil
        try:
            shutil.copy2(flaskenv_example, flaskenv_file)
            print("✅ .flaskenv created from .flaskenv.example")
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    # Update .flaskenv
    db_url = f"127.0.0.1:{port}" if port != "3306" else "127.0.0.1"
    update_flaskenv(flaskenv_file, "mysql", db_url, db_user, db_password, db_name, enable_encryption)
    
    # Start Docker container
    print("\n" + "-"*60)
    print("Starting MariaDB container...")
    print("-"*60)
    
    try:
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ MariaDB container started")
            
            # Wait for database to be ready
            if not wait_for_database('mysql', '127.0.0.1', int(port), db_user, db_password, db_name):
                print("❌ Database failed to start properly")
                return False
            
            # Run migrations
            print("Running database migrations...")
            env = os.environ.copy()
            env['DATABASE_DEFAULT'] = 'mysql'
            env['DB_URL'] = f'127.0.0.1:{port}' if port != '3306' else '127.0.0.1'
            env['DB_USER'] = db_user
            env['DB_PW'] = db_password
            env['DB_NAME'] = db_name
            
            result = subprocess.run(
                ["python", "-m", "flask", "db", "upgrade"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=60,
                env=env
            )
            
            if result.returncode == 0:
                print("✅ Database migrations completed")
                return show_docker_summary("MariaDB", container_name, db_user, db_password, db_name)
            else:
                print(f"❌ Migration failed: {result.stderr}")
                return False
        else:
            print(f"❌ Failed to start container: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def setup_postgres_docker(project_dir, enable_encryption=False):
    """Setup PostgreSQL with Docker"""
    import subprocess
    import os
    
    print("\n" + "-"*60)
    print("PostgreSQL Docker Configuration")
    print("-"*60)
    
    # Get configuration
    db_user = input("\nDatabase User [todobox]: ").strip() or "todobox"
    db_password = getpass.getpass("Database Password [todobox123]: ") or "todobox123"
    db_name = input("Database Name [todobox]: ").strip() or "todobox"
    container_name = input("Container Name [todobox-postgres]: ").strip() or "todobox-postgres"
    port = input("Port [5432]: ").strip() or "5432"
    
    # Create docker-compose.yml
    docker_compose = f"""version: '3.8'

services:
  postgres:
    image: postgres:latest
    container_name: {container_name}
    environment:
      POSTGRES_USER: {db_user}
      POSTGRES_PASSWORD: {db_password}
      POSTGRES_DB: {db_name}
    ports:
      - "{port}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql
    restart: unless-stopped

volumes:
  postgres_data:
"""
    
    docker_compose_file = os.path.join(project_dir, 'docker-compose.yml')
    try:
        with open(docker_compose_file, 'w') as f:
            f.write(docker_compose)
        print(f"✅ docker-compose.yml created")
    except Exception as e:
        print(f"❌ Error creating docker-compose.yml: {e}")
        return False
    
    # Create .flaskenv
    flaskenv_file = os.path.join(project_dir, '.flaskenv')
    flaskenv_example = os.path.join(project_dir, '.flaskenv.example')
    
    if not os.path.exists(flaskenv_file) and os.path.exists(flaskenv_example):
        import shutil
        try:
            shutil.copy2(flaskenv_example, flaskenv_file)
            print("✅ .flaskenv created from .flaskenv.example")
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    # Update .flaskenv
    db_url = f"localhost:{port}" if port != "5432" else "localhost"
    update_flaskenv(flaskenv_file, "postgres", db_url, db_user, db_password, db_name, enable_encryption)
    
    # Install psycopg2 if needed
    print("\nEnsuring psycopg2 is installed...")
    subprocess.run(["pip", "install", "-q", "psycopg2-binary"], timeout=60)
    
    # Start Docker container
    print("\n" + "-"*60)
    print("Starting PostgreSQL container...")
    print("-"*60)
    
    try:
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ PostgreSQL container started")
            
            # Wait for database to be ready
            if not wait_for_database('postgres', 'localhost', int(port), db_user, db_password, db_name):
                print("❌ Database failed to start properly")
                return False
            
            # Run migrations
            print("Running database migrations...")
            env = os.environ.copy()
            env['DATABASE_DEFAULT'] = 'postgres'
            env['DB_URL'] = 'localhost'
            env['DB_USER'] = db_user
            env['DB_PW'] = db_password
            env['DB_NAME'] = db_name
            
            result = subprocess.run(
                ["python", "-m", "flask", "db", "upgrade"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=60,
                env=env
            )
            
            if result.returncode == 0:
                print("✅ Database migrations completed")
                return show_docker_summary("PostgreSQL", container_name, db_user, db_password, db_name)
            else:
                print(f"❌ Migration failed: {result.stderr}")
                return False
        else:
            print(f"❌ Failed to start container: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_docker_summary(db_name, container_name=None, db_user=None, db_password=None, db_database=None):
    """Show Docker installation summary"""
    print("\n" + "="*60)
    print("Installation Summary".center(60))
    print("="*60)
    
    print(f"""
✅ TodoBox Docker installation completed successfully!

Database: {db_name}
""")
    if container_name:
        print(f"Container: {container_name}")
        print(f"User: {db_user}")
        print(f"Database: {db_database}")
        print("\nUseful Docker commands:")
        print(f"  docker-compose up -d      # Start services")
        print(f"  docker-compose down       # Stop services")
        print(f"  docker-compose logs       # View logs")
        print(f"  docker exec {container_name} bash  # Enter container")
    
    print("""
Next steps:

1. CREATE FIRST ADMIN USER
   Select option 1 from main menu and create your first admin user
   
2. RUN THE APPLICATION
   Select option 6 (Run) from main menu
   
3. ACCESS THE APPLICATION
   Open your browser: http://localhost:9191
   
4. LOGIN
   Use the admin credentials you just created

For more information:
   - docs/USER_CREATION.md    (user creation guide)
   - docs/OAUTH_SETUP.md      (Google OAuth configuration)
   - docs/DEPLOYMENT.md       (deployment options)
   - README.md                (quick reference)
""")
    print("="*60)
    
    # Automatically generate SECRET_KEY and SALT after installation
    print("\n🔐 Generating secure SECRET_KEY and SALT...")
    generate_secrets()
    
    return True

def update_flaskenv(flaskenv_file, db_type, db_url=None, db_user=None, db_password=None, db_name=None, enable_encryption=False):
    """Update .flaskenv with database configuration and encryption settings"""
    try:
        with open(flaskenv_file, 'r') as f:
            content = f.read()
        
        # Update DATABASE_DEFAULT
        import re
        content = re.sub(r'DATABASE_DEFAULT=.*', f'DATABASE_DEFAULT={db_type}', content)
        
        # Update DATABASE_NAME for non-SQLite databases
        if db_type != "sqlite" and db_name:
            content = re.sub(r'DATABASE_NAME=.*', f'DATABASE_NAME={db_name}', content)
        
        if db_type != "sqlite":
            # For non-SQLite databases, add or update connection parameters
            if not re.search(r'^DB_URL=', content, re.MULTILINE):
                content += f'\nDB_URL={db_url}'
            else:
                content = re.sub(r'^DB_URL=.*', f'DB_URL={db_url}', content, flags=re.MULTILINE)
            
            if not re.search(r'^DB_USER=', content, re.MULTILINE):
                content += f'\nDB_USER={db_user}'
            else:
                content = re.sub(r'^DB_USER=.*', f'DB_USER={db_user}', content, flags=re.MULTILINE)
            
            if not re.search(r'^DB_PW=', content, re.MULTILINE):
                content += f'\nDB_PW={db_password}'
            else:
                content = re.sub(r'^DB_PW=.*', f'DB_PW={db_password}', content, flags=re.MULTILINE)
            
            if not re.search(r'^DB_NAME=', content, re.MULTILINE):
                content += f'\nDB_NAME={db_name}'
            else:
                content = re.sub(r'^DB_NAME=.*', f'DB_NAME={db_name}', content, flags=re.MULTILINE)
        
        # Update TODO_ENCRYPTION_ENABLED
        encryption_value = 'true' if enable_encryption else 'false'
        if not re.search(r'^TODO_ENCRYPTION_ENABLED=', content, re.MULTILINE):
            content += f'\nTODO_ENCRYPTION_ENABLED={encryption_value}'
        else:
            content = re.sub(r'^TODO_ENCRYPTION_ENABLED=.*', f'TODO_ENCRYPTION_ENABLED={encryption_value}', content, flags=re.MULTILINE)
        
        with open(flaskenv_file, 'w') as f:
            f.write(content)
        
        print(f"✅ .flaskenv updated with {db_type} configuration")
        if enable_encryption:
            print("✅ Todo encryption enabled")
        else:
            print("✅ Todo encryption disabled (default)")
    except Exception as e:
        print(f"⚠️  Could not update .flaskenv: {e}")

def create_user():
    """Create a new user with optional admin privileges"""
    from app import app, db
    from app.models import User
    
    with app.app_context():
        print("\n\n" + "-"*60)
        print("  Create New User")
        print("-"*60)
        
        email = get_valid_email()
        password = get_valid_password()
        fullname = input("\nFull name (optional) []: ").strip()
        
        # Ask about admin privileges
        make_admin = input("\nAssign admin privileges? [y/N]: ").strip().lower()
        is_admin = make_admin == 'y'
        
        # Confirm
        print("\n" + "-" * 60)
        print("Confirm user details:")
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
            user = User(email=email)
            if fullname:
                user.fullname = fullname
            user.is_admin = is_admin
            user.set_password(password)
            db.session.add(user)  # type: ignore[union-attr]
            db.session.commit()  # type: ignore[union-attr]
            
            admin_status = " (admin)" if is_admin else ""
            print(f"\n✅ User '{email}'{admin_status} created successfully!")
            return True
        except Exception as e:
            print(f"\n❌ Error creating user: {e}")
            db.session.rollback()  # type: ignore[union-attr]
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
        print(f"{'ID':<5} {'Email':<30} {'Full Name':<20} {'Admin':<6} {'Blocked':<8}")
        print("-"*80)
        
        for user in users:
            fullname = user.fullname or '(not set)'
            email = user.email or '(no email)'
            is_admin = 'Yes' if user.is_system_admin() else 'No'
            is_blocked = 'Yes' if user.is_blocked else 'No'
            print(f"{user.id:<5} {email:<30} {fullname:<20} {is_admin:<6} {is_blocked:<8}")
        
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
        
        # Get email
        email = input("\nEnter user email: ").strip()
        
        if not email:
            print("\n❌ Email cannot be empty.")
            return False
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"\n❌ User with email '{email}' not found.")
            return False
        
        # Show current status
        current_admin = user.is_system_admin()
        print(f"\nUser: {user.email}")
        print(f"Full Name: {user.fullname or '(not set)'}")
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
        if not input(f"\nConfirm {action_desc} user '{email}'? [Y/n]: ").strip().lower() == 'n':
            # Update user
            try:
                user.is_admin = new_admin
                db.session.commit()  # type: ignore[union-attr]
                
                status = "assigned" if new_admin else "removed"
                print(f"\n✅ Admin privileges {status} for user '{email}'!")
                return True
            except Exception as e:
                print(f"\n❌ Error updating user: {e}")
                db.session.rollback()  # type: ignore[union-attr]
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
        
        # Get email
        email = input("\nEnter user email to delete: ").strip()
        
        if not email:
            print("\n❌ Email cannot be empty.")
            return False
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"\n❌ User with email '{email}' not found.")
            return False
        
        # Show user details
        print(f"\nUser details:")
        print(f"  ID: {user.id}")
        print(f"  Email: {user.email or '(no email)'}")
        print(f"  Full Name: {user.fullname or '(not set)'}")
        print(f"  Admin: {'Yes' if user.is_system_admin() else 'No'}")
        
        # Confirm deletion
        print("\n⚠️  WARNING: This action cannot be undone!")
        confirm = input(f"\nAre you sure you want to delete user '{email}'? [y/N]: ").strip().lower()
        
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
            db.session.delete(user)  # type: ignore[union-attr]
            db.session.commit()  # type: ignore[union-attr]
            print(f"\n✅ User '{email}' deleted successfully!")
            return True
        except Exception as e:
            print(f"\n❌ Error deleting user: {e}")
            db.session.rollback()  # type: ignore[union-attr]
            return False

def generate_secrets():
    """Generate cryptographically secure SECRET_KEY and SALT"""
    
    print("\n\n" + "-"*60)
    print("  Generate SECRET_KEY and SALT")
    print("-"*60)
    
    # Generate secure random values
    secret_key = secrets.token_hex(32)  # 64 character hex string (256 bits)
    salt = secrets.token_hex(16)  # 32 character hex string (128 bits)
    
    # Define paths
    project_root = Path(__file__).parent
    flaskenv_path = project_root / '.flaskenv'
    flaskenv_example_path = project_root / '.flaskenv.example'
    
    # Placeholder values to detect (regex patterns for exact line matching)
    placeholder_secret_pattern = r'^SECRET_KEY=change-me-to-a-secure-random-key\s*$'
    placeholder_salt_pattern = r'^SALT=change-me-to-a-secure-salt\s*$'
    
    # Check if .flaskenv exists and has placeholder values
    updated = False
    if flaskenv_path.exists():
        content = flaskenv_path.read_text(encoding='utf-8')
        
        # Check for placeholder values using regex (multiline mode)
        has_placeholder_secret = re.search(placeholder_secret_pattern, content, re.MULTILINE) is not None
        has_placeholder_salt = re.search(placeholder_salt_pattern, content, re.MULTILINE) is not None
        
        if has_placeholder_secret or has_placeholder_salt:
            print("\n🔍 Detected placeholder values in .flaskenv")
            
            # Replace placeholder values using regex
            if has_placeholder_secret:
                content = re.sub(
                    placeholder_secret_pattern,
                    f'SECRET_KEY={secret_key}',
                    content,
                    flags=re.MULTILINE
                )
                print("   ✓ Updated SECRET_KEY")
            
            if has_placeholder_salt:
                content = re.sub(
                    placeholder_salt_pattern,
                    f'SALT={salt}',
                    content,
                    flags=re.MULTILINE
                )
                print("   ✓ Updated SALT")
            
            # Write updated content back
            flaskenv_path.write_text(content, encoding='utf-8')
            updated = True
            print("\n✅ .flaskenv has been updated with secure values!")
        else:
            print("\n⚠️  .flaskenv exists but does not contain placeholder values.")
            print("   SECRET_KEY and SALT were not updated.")
    else:
        # .flaskenv doesn't exist - check if we can create from example
        if flaskenv_example_path.exists():
            print("\n⚠️  .flaskenv does not exist.")
            create_env = input("   Create .flaskenv from .flaskenv.example? [Y/n]: ").strip().lower()
            
            if create_env != 'n':
                content = flaskenv_example_path.read_text(encoding='utf-8')
                
                # Replace placeholder values in the example content using regex
                content = re.sub(
                    placeholder_secret_pattern,
                    f'SECRET_KEY={secret_key}',
                    content,
                    flags=re.MULTILINE
                )
                content = re.sub(
                    placeholder_salt_pattern,
                    f'SALT={salt}',
                    content,
                    flags=re.MULTILINE
                )
                
                flaskenv_path.write_text(content, encoding='utf-8')
                updated = True
                print("\n✅ .flaskenv created with secure SECRET_KEY and SALT!")
            else:
                print("\n⚠️  .flaskenv was not created.")
        else:
            print("\n⚠️  Neither .flaskenv nor .flaskenv.example exist.")
    
    # Always display the generated values
    print("\n" + "-" * 60)
    print("Generated values:\n")
    print(f"SECRET_KEY={secret_key}")
    print(f"SALT={salt}")
    print("-" * 60)
    
    if not updated:
        print("\n⚠️  IMPORTANT: Store these values securely!")
        print("   These values should be set in your .flaskenv file.")
        print("   Never commit these values to version control.\n")
        
        # Ask if user wants to see the instructions
        show_help = input("\nShow instructions for updating .flaskenv? [y/N]: ").strip().lower()
        
        if show_help == 'y':
            print("\n" + "="*60)
            print("  Instructions")
            print("="*60)
            print("""
1. Open or create your .flaskenv file in the project root

2. Copy and paste the SECRET_KEY and SALT values shown above

3. Make sure .flaskenv is in your .gitignore file

4. For production, use environment variables instead of .flaskenv

Example .flaskenv structure:
   FLASK_APP=todobox.py
   SECRET_KEY=your_generated_secret_key_here
   SALT=your_generated_salt_here
   DATABASE_DEFAULT=sqlite
   DATABASE_NAME=todobox.db
""")
    
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
