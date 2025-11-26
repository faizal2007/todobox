#!/bin/bash
# Quick Migration Fix Script for Production
# Usage: bash fix_production_migration.sh

set -e

echo "🔧 TodoBox Production Migration Fix Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get database credentials
if [ -f .flaskenv ]; then
    export $(cat .flaskenv | xargs)
fi

echo -e "${YELLOW}Step 1: Backup Database${NC}"
if command -v mysqldump &> /dev/null; then
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    echo "Creating backup: $BACKUP_FILE"
    
    # Extract DB credentials from DATABASE_URL
    # Expected format: mysql://user:password@host/dbname
    if [ -n "$DATABASE_URL" ]; then
        # Parse connection string (basic parsing)
        MYSQL_USER=$(echo $DATABASE_URL | sed 's/.*:\/\/\([^:]*\):.*/\1/')
        MYSQL_PASS=$(echo $DATABASE_URL | sed 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/')
        MYSQL_HOST=$(echo $DATABASE_URL | sed 's/.*@\([^:\/]*\).*/\1/')
        MYSQL_DB=$(echo $DATABASE_URL | sed 's/.*\/\([^?]*\).*/\1/')
        
        echo "Backing up database: $MYSQL_DB"
        mysqldump -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PASS $MYSQL_DB > $BACKUP_FILE
        echo -e "${GREEN}✅ Backup created: $BACKUP_FILE${NC}"
    fi
fi

echo -e "\n${YELLOW}Step 2: Check Current Schema${NC}"
python3 << 'PYEOF'
from app import app, db
from sqlalchemy import inspect

with app.app_context():
    try:
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('user')]
        
        if 'api_token' in columns:
            print("✅ Column 'api_token' exists")
        else:
            print("❌ Column 'api_token' is MISSING - will be fixed by migration")
        
        print(f"\nUser table columns: {', '.join(columns)}")
    except Exception as e:
        print(f"Error checking schema: {e}")
PYEOF

echo -e "\n${YELLOW}Step 3: Run Flask Migrations${NC}"
echo "Running: flask db upgrade"
flask db upgrade

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migrations completed successfully${NC}"
else
    echo -e "${RED}❌ Migrations failed${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Step 4: Verify Schema${NC}"
python3 << 'PYEOF'
from app import app, db
from sqlalchemy import inspect

with app.app_context():
    try:
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('user')]
        
        if 'api_token' in columns:
            print("✅ Column 'api_token' now exists")
        else:
            print("❌ Column 'api_token' still missing")
            exit(1)
        
        indexes = {idx['name']: idx for idx in inspector.get_indexes('user')}
        if 'ix_user_api_token' in indexes:
            print("✅ Index 'ix_user_api_token' exists")
        else:
            print("⚠️  Index 'ix_user_api_token' missing (may be created separately)")
        
        print(f"\n✅ User table has {len(columns)} columns:")
        for col in columns:
            print(f"   - {col}")
    except Exception as e:
        print(f"Error verifying schema: {e}")
        exit(1)
PYEOF

echo -e "\n${GREEN}=========================================="
echo "✅ Migration fix completed successfully!"
echo "=========================================${NC}"
echo ""
echo "Your application can now run without the 'Unknown column' error."
echo ""
echo "Next steps:"
echo "  1. Test the application: flask run"
echo "  2. Monitor logs for any issues"
echo "  3. If issues occur, restore from backup:"
echo "     mysql -u user -p database < $BACKUP_FILE"
