# Deployment & Maintenance Guide

## Pre-Deployment Checklist

### Security Review

- [ ] Change SECRET_KEY in config.py
- [ ] Change SALT value
- [ ] Remove debug mode (FLASK_DEBUG=0)
- [ ] Verify HTTPS/SSL configuration
- [ ] Update admin credentials
- [ ] Review database user permissions
- [ ] Enable CSRF protection verification
- [ ] Add HTML sanitization for Markdown
- [ ] Review active dependencies for CVEs

### Configuration Review

- [ ] Set DATABASE_DEFAULT to production database (MySQL/PostgreSQL)
- [ ] Configure database credentials via environment variables
- [ ] Set appropriate SECRET_KEY length
- [ ] Configure session timeout appropriately
- [ ] Review BIND_ADDRESS and PORT settings
- [ ] Verify logging configuration
- [ ] Test email configuration (if applicable)

### Database Review

- [ ] Run database migrations
- [ ] Verify database backups configured
- [ ] Test database recovery process
- [ ] Check database permissions
- [ ] Verify indexes created
- [ ] Monitor database size growth

### Testing

- [ ] Run unit tests (none currently)
- [ ] Perform manual integration testing
- [ ] Test authentication flows
- [ ] Test todo CRUD operations
- [ ] Test account management
- [ ] Verify password change functionality
- [ ] Test session timeout
- [ ] Verify CSRF protection

## Deployment Options

### Option 1: Traditional Server Deployment

#### Prerequisites

```bash
# Ubuntu/Debian
sudo apt-get install python3 python3-pip python3-venv mysql-server nginx
```

#### Deployment Steps

1. **Create Application User**

   ```bash
   sudo useradd -m -s /bin/bash todobox
   sudo -u todobox mkdir -p /var/www/todobox
```

2. **Clone Repository**

   ```bash
   cd /var/www/todobox
   git clone <repository-url> .
```

3. **Setup Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
```

4. **Configure Application**

   ```bash
   cp .flaskenv.example .flaskenv
   # Edit .flaskenv with production settings
   nano .flaskenv
```

5. **Create Systemd Service**

   ```bash
   sudo tee /etc/systemd/system/todobox.service > /dev/null << EOF
   [Unit]
   Description=TodoBox Flask Application
   After=network.target

   [Service]
   Type=notify
   User=todobox
   WorkingDirectory=/var/www/todobox
   Environment="PATH=/var/www/todobox/venv/bin"
   ExecStart=/var/www/todobox/venv/bin/gunicorn -w 4 -b 127.0.0.1:9191 todobox:app
   Restart=always
   RestartSec=5s

   [Install]
   WantedBy=multi-user.target
   EOF

   sudo systemctl daemon-reload
   sudo systemctl enable todobox
   sudo systemctl start todobox
```

6. **Configure Nginx**

   ```bash
   sudo tee /etc/nginx/sites-available/todobox > /dev/null << 'EOF'
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:9191;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location /static/ {
           alias /var/www/todobox/app/static/;
       }
   }
   EOF

   sudo ln -s /etc/nginx/sites-available/todobox /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
```

7. **Setup SSL with Let's Encrypt**

   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
```

8. **Initialize Database**

   ```bash
   cd /var/www/todobox
   source venv/bin/activate
   flask db upgrade
```

### Option 2: Docker Deployment

#### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create instance directory
RUN mkdir -p instance

# Expose port
EXPOSE 9191

# Set environment variables
ENV FLASK_APP=todobox.py
ENV FLASK_ENV=production

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:9191", "todobox:app"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: todobox
      MYSQL_USER: todobox
      MYSQL_PASSWORD: dbpassword
    volumes:
      - db_data:/var/lib/mysql
    ports:
      - "3306:3306"

  web:
    build: .
    environment:
      DATABASE_DEFAULT: mysql
      DB_URL: db
      DB_USER: todobox
      DB_PW: dbpassword
      DB_NAME: todobox
      SECRET_KEY: your-secret-key
    ports:
      - "9191:9191"
    depends_on:
      - db
    volumes:
      - ./instance:/app/instance
    command: >
      sh -c "flask db upgrade &&
             gunicorn -w 4 -b 0.0.0.0:9191 todobox:app"

volumes:
  db_data:
```

#### Deploy Docker

```bash
docker-compose build
docker-compose up -d
```

### Option 3: Cloud Deployment

#### AWS Deployment

1. Launch EC2 instance (Ubuntu 20.04)
2. Follow Traditional Server Deployment steps
3. Use RDS for MySQL database
4. Use Route53 for DNS
5. Use CloudFront for CDN
6. Use ACM for SSL certificates

#### Heroku Deployment

```bash
# Create Procfile
echo "web: gunicorn todobox:app" > Procfile

# Create runtime.txt
echo "python-3.9.10" > runtime.txt

# Deploy
git push heroku main
```

#### DigitalOcean Deployment

1. Create Droplet (Ubuntu 20.04)
2. Follow Traditional Server Deployment steps
3. Use DigitalOcean Managed Databases
4. Configure UFW firewall
5. Setup automated backups

## Maintenance Tasks

### Daily Tasks

- [ ] Monitor application logs
- [ ] Check disk space usage
- [ ] Verify application is responding
- [ ] Check error rates

### Weekly Tasks

- [ ] Review application performance metrics
- [ ] Check database performance
- [ ] Verify backup completion
- [ ] Review failed login attempts
- [ ] Update SSL certificate status

### Monthly Tasks

- [ ] Review user activity
- [ ] Analyze performance trends
- [ ] Update dependencies for security patches
- [ ] Review and optimize slow queries
- [ ] Backup and archive logs

### Quarterly Tasks

- [ ] Security audit
- [ ] Capacity planning
- [ ] Review and update documentation
- [ ] Plan feature releases
- [ ] Database optimization

### Annual Tasks

- [ ] Full security review
- [ ] Disaster recovery testing
- [ ] Architecture review
- [ ] Scalability assessment
- [ ] Compliance audit

## Monitoring & Logging

### Application Logging

Configure in `app/__init__.py`:

```python
import logging
from logging.handlers import RotatingFileHandler
import os

if not app.debug and not app.testing:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler(
        'logs/todobox.log', maxBytes=10240000, backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('TodoBox startup')
```

### Key Metrics to Monitor

- Application response time (< 200ms target)
- Error rate (< 0.1% target)
- Active users
- Database query time
- Memory usage
- CPU usage
- Disk space usage

### Monitoring Tools

- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **ELK Stack**: Logging and analysis
- **New Relic**: APM
- **DataDog**: Monitoring and alerting

### Alerting

Setup alerts for:

- High error rates (> 1%)
- Slow response times (> 500ms)
- High memory usage (> 80%)
- Disk space low (< 10%)
- Database connection errors
- Unauthorized access attempts

## Backup & Recovery

### Database Backup Strategy

**MySQL Backup:**

```bash
# Full backup
mysqldump -u todobox -p todobox > backup_$(date +%Y%m%d).sql

# Compressed backup
mysqldump -u todobox -p todobox | gzip > backup_$(date +%Y%m%d).sql.gz

# Automated daily backup
0 2 * * * mysqldump -u todobox -p'password' todobox | \
    gzip > /backups/todobox_$(date +\%Y\%m\%d).sql.gz
```

**Database Restore:**

```bash
mysql -u todobox -p todobox < backup_20240115.sql
```

### Application Backup

```bash
# Backup application code
tar -czf app_backup_$(date +%Y%m%d).tar.gz /var/www/todobox

# Backup instance data
tar -czf instance_backup_$(date +%Y%m%d).tar.gz /var/www/todobox/instance
```

### Backup Schedule

- **Hourly**: Database incremental
- **Daily**: Full database + application
- **Weekly**: Full backup to offsite storage
- **Monthly**: Archive backup for compliance

### Recovery Procedure

```bash
# 1. Restore database
mysql -u todobox -p todobox < backup_20240115.sql.gz

# 2. Restore application
tar -xzf app_backup_20240115.tar.gz -C /var/www/todobox

# 3. Verify application
systemctl restart todobox

# 4. Check logs
tail -f /var/log/syslog | grep todobox
```

## Performance Optimization

### Database Optimization

```sql
-- Check query performance
EXPLAIN SELECT * FROM todo
WHERE user_id = 1 AND modified > DATE_SUB(NOW(), INTERVAL 7 DAY);

-- Add indexes if needed
CREATE INDEX idx_user_modified ON todo(user_id, modified);
```

### Application Optimization

1. Enable gzip compression in Nginx
2. Cache static files (CSS, JS, images)
3. Use connection pooling
4. Implement query result caching
5. Optimize markdown rendering
6. Add pagination to todo lists

### Nginx Compression Config

```nginx
gzip on;
gzip_types text/plain text/css text/javascript application/json;
gzip_min_length 1000;
```

## Scaling Strategies

### Horizontal Scaling

```text
Load Balancer
├─ App Server 1
├─ App Server 2
└─ App Server 3
       ↓
  MySQL Cluster (with replication)
```

### Vertical Scaling

- Increase server RAM
- Upgrade CPU
- Faster storage (SSD)
- Database optimization

### Caching Layer

```text
App Server
    ↓
Redis Cache (sessions, queries)
    ↓
Database
```

## Troubleshooting

### Application Won't Start

```bash
# Check systemd status
sudo systemctl status todobox

# View logs
sudo journalctl -u todobox -n 50

# Manual start for errors
cd /var/www/todobox
source venv/bin/activate
python todobox.py
```

### Database Connection Error

```bash
# Test connection
mysql -u todobox -p -h localhost todobox

# Check environment variables
grep DATABASE .flaskenv

# Verify database user permissions
SHOW GRANTS FOR 'todobox'@'localhost';
```

### High Memory Usage

```bash
# Check Gunicorn workers
ps aux | grep gunicorn

# Reduce workers or memory limit
# Edit systemd service or docker config
```

### Slow Queries

```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;

-- Analyze slow queries
SELECT * FROM mysql.slow_log;
```

## Security Maintenance

### Regular Security Tasks

- [ ] Update dependencies monthly
- [ ] Review access logs for suspicious activity
- [ ] Check for failed login attempts
- [ ] Rotate credentials periodically
- [ ] Review user accounts (remove inactive)
- [ ] Verify firewall rules
- [ ] Check SSL certificate expiration

### Dependency Updates

```bash
pip list --outdated
pip install --upgrade package-name
```

### Log Monitoring for Security

```bash
# Check for failed logins
grep "Invalid username" /var/log/todobox.log

# Check for brute force attempts
grep "login" /var/log/todobox.log | grep -c failed
```

## Upgrade Procedure

### Before Upgrade

1. Backup database and files
2. Notify users of maintenance window
3. Document current version
4. Test upgrade on staging environment

### Upgrade Steps

```bash
# 1. Stop application
sudo systemctl stop todobox

# 2. Backup
tar -czf backup_$(date +%Y%m%d).tar.gz /var/www/todobox

# 3. Pull latest code
cd /var/www/todobox
git pull origin main

# 4. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 5. Run migrations
flask db upgrade

# 6. Restart application
sudo systemctl start todobox

# 7. Verify
curl http://127.0.0.1:9191
```

### After Upgrade

1. Test all functionality
2. Monitor error logs
3. Verify performance
4. Inform users
5. Document changes
