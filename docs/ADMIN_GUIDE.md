# College Data Management System - Administrator Guide

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Initial Setup](#initial-setup)
4. [User Management](#user-management)
5. [System Settings](#system-settings)
6. [Backup & Restore](#backup--restore)
7. [Monitoring & Logs](#monitoring--logs)
8. [Troubleshooting](#troubleshooting)
9. [Production Deployment](#production-deployment)
10. [Maintenance Tasks](#maintenance-tasks)

---

## Installation

### Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend build)
- pip (Python package manager)
- npm (Node package manager)

### Development Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd college_data_cli

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Node dependencies
npm install

# 5. Build frontend assets
npm run build

# 6. Run database migrations
python manage.py migrate

# 7. Create superuser
python manage.py createsuperuser

# 8. Setup default roles
python manage.py setup_roles

# 9. Seed initial data (optional)
python manage.py seed_data
python manage.py seed_grading_settings

# 10. Run development server
python manage.py runserver
```

### Quick Start Script

```bash
#!/bin/bash
# save as setup.sh

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
npm install
npm run build
python manage.py migrate
python manage.py setup_roles
python manage.py seed_grading_settings
echo "Setup complete! Run: python manage.py runserver"
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database (for PostgreSQL)
DATABASE_URL=postgres://user:password@localhost:5432/college_db

# Session Settings
SESSION_TIMEOUT_MINUTES=60
MAX_CONCURRENT_SESSIONS=3
TRACK_USER_SESSIONS=True

# Email (for notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Django Settings (`college_data_cli/settings.py`)

Key settings to configure:

```python
# Security
DEBUG = False  # Always False in production
SECRET_KEY = os.environ.get('SECRET_KEY')
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'college_db',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Session security
SESSION_TIMEOUT_MINUTES = 60
MAX_CONCURRENT_SESSIONS = 3
SESSION_COOKIE_SECURE = True  # HTTPS only
CSRF_COOKIE_SECURE = True

# Session engine (use database for production)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
```

---

## Initial Setup

### 1. Create Administrator Account

```bash
python manage.py createsuperuser
# Follow prompts for username, email, password
```

### 2. Setup Roles

```bash
python manage.py setup_roles
# Creates: Admin, DataEntry, Teacher roles
```

### 3. Configure Grading Scale

```bash
# Option A: Use default grading settings
python manage.py seed_grading_settings

# Option B: Custom via CLI
python manage.py add_grading_setting --min 70 --max 100 --grade A --point 4.0
python manage.py add_grading_setting --min 60 --max 69 --grade B --point 3.0
python manage.py add_grading_setting --min 50 --max 59 --grade C --point 2.0
python manage.py add_grading_setting --min 45 --max 49 --grade D --point 1.0
python manage.py add_grading_setting --min 0 --max 44 --grade F --point 0.0

# Option C: Via web interface
# Navigate to Settings → Grading Scale
```

### 4. Configure College Information

Via Web Interface:
1. Login as Admin
2. Go to Settings → College Info
3. Enter:
   - College Name
   - Address
   - Phone, Email, Website
   - Registrar Name and Title
   - Upload Logo and Signature

Via CLI:
```bash
python manage.py update_college_settings \
    --name "University of Technology" \
    --address "123 Main Street, City" \
    --phone "+1234567890" \
    --email "info@university.edu"
```

### 5. Create Academic Sessions

```bash
# Via CLI
python manage.py shell
>>> from students.models import Session
>>> Session.objects.create(name="2024/2025", is_active=True)

# Or via web interface: Settings → Sessions
```

### 6. Create Levels

```bash
python manage.py shell
>>> from students.models import Level
>>> Level.objects.create(name="100", order=1)
>>> Level.objects.create(name="200", order=2)
>>> Level.objects.create(name="300", order=3)
>>> Level.objects.create(name="400", order=4)

# Or via web interface: Settings → Levels
```

### 7. Create Departments

Via web interface: Settings → Departments

### 8. Import Initial Data

```bash
# Import students
python manage.py import_students_csv students.csv
python manage.py import_students_excel students.xlsx
python manage.py import_students_json students.json

# Import courses
python manage.py add_course --code CS101 --title "Intro to CS" --units 3

# Or use web interface bulk import features
```

---

## User Management

### Creating Users

#### Via Django Admin
1. Go to `/admin/`
2. Click "Users" → "Add User"
3. Set username and password
4. Save and continue editing
5. Set first name, last name, email
6. Check "Staff status" for admin access

#### Via CLI
```bash
python manage.py create_user --username john --email john@example.com --role Teacher
```

### Assigning Roles

#### Via Web Interface
1. Go to Settings → User Management
2. Click Edit on a user
3. Check desired roles
4. Save

#### Via CLI
```bash
python manage.py assign_role --user john --role Teacher
```

### Linking Teachers to Users

For teacher login with their own grade access:

```bash
python manage.py link_teacher_user --user john --teacher-id T001
```

Or via Django Admin:
1. Go to Users → UserProfile
2. Create profile linking User to Teacher

### Deactivating Users

1. Settings → User Management
2. Edit user
3. Uncheck "Active User"
4. Save

Inactive users cannot log in.

---

## System Settings

### Academic Policy

Location: Settings → Academic Policy

| Setting | Description | Default |
|---------|-------------|---------|
| Max Course Repeats | How many times student can repeat a course | 3 |
| GPA Calculation | How repeats affect GPA (Last/Best/Average) | Last |
| Probation GPA | GPA threshold for academic probation | 2.0 |
| Dismissal GPA | GPA threshold for dismissal | 1.0 |
| Require Grade Approval | Enable grade approval workflow | Yes |
| Require Transcript Approval | Enable transcript approval | No |

### Session Management

Settings → Sessions
- Create new academic sessions
- Set active session (only one can be active)
- Edit/delete sessions

### Levels

Settings → Levels
- Create academic levels (100, 200, 300, 400)
- Set display order
- Edit/delete levels

### Departments

Settings → Departments
- Create academic departments
- Assign department heads
- Set department codes
- Deactivate departments

### Grading Scale

Settings → Grading Scale
- Define grade boundaries (A: 70-100, B: 60-69, etc.)
- Set grade points for GPA calculation
- Add/edit/delete grade levels

---

## Backup & Restore

### Database Backup

#### SQLite
```bash
# Simple file copy
cp db.sqlite3 backups/db_$(date +%Y%m%d).sqlite3

# Using Django dumpdata
python manage.py dumpdata > backups/backup_$(date +%Y%m%d).json
```

#### PostgreSQL
```bash
# Full backup
pg_dump -U postgres college_db > backups/backup_$(date +%Y%m%d).sql

# Compressed backup
pg_dump -U postgres college_db | gzip > backups/backup_$(date +%Y%m%d).sql.gz
```

### Media Files Backup

```bash
# Backup uploaded files
tar -czvf backups/media_$(date +%Y%m%d).tar.gz media/
```

### Restore Database

#### SQLite
```bash
# From file copy
cp backups/db_20240115.sqlite3 db.sqlite3

# From JSON dump
python manage.py loaddata backups/backup_20240115.json
```

#### PostgreSQL
```bash
# Drop and recreate database
dropdb college_db
createdb college_db
psql college_db < backups/backup_20240115.sql
```

### Automated Backup Script

```bash
#!/bin/bash
# save as backup.sh

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
python manage.py dumpdata --indent 2 > "$BACKUP_DIR/db_$DATE.json"

# Media backup
tar -czvf "$BACKUP_DIR/media_$DATE.tar.gz" media/

# Keep only last 30 days
find "$BACKUP_DIR" -name "*.json" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

Add to cron for daily backups:
```bash
0 2 * * * /path/to/backup.sh >> /var/log/backup.log 2>&1
```

---

## Monitoring & Logs

### Audit Log

The system automatically logs important actions:
- User logins/logouts
- Data creation/modification/deletion
- Grade submissions and approvals
- Transcript generation

View via: Settings → Audit Log

Filter by:
- Action type
- User
- Date range
- Search in details

### Django Logs

Configure logging in `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/var/log/college_app/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
}
```

### Session Tracking

When `TRACK_USER_SESSIONS = True`:
- Active sessions are tracked in database
- View via Django Admin → User Sessions
- Shows IP address, user agent, last activity

---

## Troubleshooting

### Common Issues

#### "Migration errors"
```bash
# Reset migrations (development only!)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
```

#### "Static files not loading"
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check STATIC_ROOT in settings
# Ensure web server serves /static/
```

#### "Permission denied errors"
```bash
# Check file permissions
chmod -R 755 media/
chmod -R 755 staticfiles/

# Check directory ownership
chown -R www-data:www-data /path/to/app/
```

#### "Session expired too quickly"
```python
# Increase timeout in settings.py
SESSION_TIMEOUT_MINUTES = 120  # 2 hours
```

#### "Database locked (SQLite)"
```bash
# Stop all processes accessing the database
# Check for zombie processes
ps aux | grep python

# Consider switching to PostgreSQL for production
```

#### "Grades not auto-calculating"
- Check GradingSettings table has entries
- Verify score ranges don't have gaps
- Check Grade.save() method is being called

### Debug Mode

For detailed error information (development only):

```python
# settings.py
DEBUG = True
```

**Never enable DEBUG in production!**

### Getting Help

1. Check this documentation
2. Review error messages in logs
3. Check Django admin for data issues
4. Contact system developer

---

## Production Deployment

### Using Gunicorn + Nginx

#### 1. Install Gunicorn
```bash
pip install gunicorn
```

#### 2. Create Gunicorn service
```ini
# /etc/systemd/system/college_app.service
[Unit]
Description=College App Gunicorn Daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/college_data_cli
ExecStart=/path/to/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/run/college_app.sock \
    college_data_cli.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### 3. Nginx Configuration
```nginx
# /etc/nginx/sites-available/college_app
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/college_data_cli/staticfiles/;
    }

    location /media/ {
        alias /path/to/college_data_cli/media/;
    }

    location / {
        proxy_pass http://unix:/run/college_app.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

#### 4. Enable and Start Services
```bash
sudo systemctl enable college_app
sudo systemctl start college_app
sudo systemctl enable nginx
sudo systemctl restart nginx
```

### SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### Production Checklist

- [ ] `DEBUG = False`
- [ ] Unique `SECRET_KEY` set via environment variable
- [ ] `ALLOWED_HOSTS` configured
- [ ] PostgreSQL (not SQLite) for database
- [ ] Static files collected (`collectstatic`)
- [ ] SSL certificate installed
- [ ] Backup schedule configured
- [ ] Logging configured
- [ ] Firewall rules set
- [ ] Regular security updates scheduled

---

## Maintenance Tasks

### Regular Tasks

#### Daily
- Review audit log for anomalies
- Check backup completion

#### Weekly
- Review pending grade approvals
- Check disk space usage
- Review error logs

#### Monthly
- Database optimization
- Update dependencies (security patches)
- Review user accounts (deactivate unused)

#### Semester End
- Archive old session data
- Generate completion reports
- Backup before major changes

### Database Maintenance

```bash
# PostgreSQL vacuum
psql -U postgres -d college_db -c "VACUUM ANALYZE;"

# SQLite optimization
sqlite3 db.sqlite3 "VACUUM;"
```

### Clearing Old Sessions

```bash
python manage.py clearsessions
```

### Updating Dependencies

```bash
# Check for updates
pip list --outdated

# Update specific package
pip install --upgrade django

# Update all (careful!)
pip install --upgrade -r requirements.txt
```

### Log Rotation

```bash
# /etc/logrotate.d/college_app
/var/log/college_app/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
}
```

---

## Quick Reference

### CLI Commands

```bash
# User management
python manage.py createsuperuser
python manage.py create_user --username X --role Y
python manage.py assign_role --user X --role Y
python manage.py setup_roles

# Data management
python manage.py add_student --id X --first-name Y --last-name Z
python manage.py add_course --code X --title Y --units Z
python manage.py add_program --code X --name Y

# Import/Export
python manage.py import_students_csv file.csv
python manage.py export_grades_csv --session "2024/2025"

# Maintenance
python manage.py clearsessions
python manage.py collectstatic
python manage.py check --deploy
```

### Important URLs

| URL | Purpose |
|-----|---------|
| `/` | Dashboard |
| `/admin/` | Django Admin |
| `/login/` | User login |
| `/settings/` | System settings |
| `/settings/audit-log/` | Activity log |

### Default Ports

| Service | Port |
|---------|------|
| Django Dev Server | 8000 |
| PostgreSQL | 5432 |
| Nginx | 80/443 |

---

*Last Updated: January 2026*
