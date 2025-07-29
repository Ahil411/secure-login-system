# Secure Login System - Installation Instructions

## Prerequisites

### 1. Install Python (3.8 or higher)
- Download from https://python.org
- Make sure to add Python to your PATH

### 2. Install XAMPP
- Download from https://www.apachefriends.org/
- Install and start Apache and MySQL services

### 3. Verify XAMPP MySQL
- Open http://localhost/phpmyadmin
- You should see the phpMyAdmin interface

## Installation Steps

### Step 1: Extract and Navigate
```bash
# Extract the zip file to your desired location
# Navigate to the project directory
cd secure_login_system
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Copy the environment template
cp .env.example .env

# Edit .env file with your settings (optional for development)
# The default settings work with XAMPP out of the box
```

### Step 5: Initialize Database
```bash
# Initialize the MySQL database
python init_db.py

# Or manually initialize using Flask CLI
python run.py init-db
```

### Step 6: Run the Application
```bash
# Start the development server
python run.py
```

### Step 7: Access the Application
- Open your browser and go to: http://localhost:5000
- Default admin login: admin / Admin@123456
- Default user login: testuser / Test@123456
- **IMPORTANT: Change default passwords immediately!**

## Quick Start Commands

```bash
# Complete setup in one go:
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python init_db.py
python run.py
```

## Troubleshooting

### MySQL Connection Issues
1. Ensure XAMPP is running
2. Start MySQL service in XAMPP Control Panel
3. Check if port 3306 is available
4. Verify phpMyAdmin works at http://localhost/phpmyadmin

### Port 5000 Already in Use
```bash
# Run on different port
python -c "from run import app; app.run(port=5001)"
```

### Package Installation Issues
```bash
# Upgrade pip first
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Database Initialization Fails
1. Check XAMPP MySQL is running
2. Try running: `python run.py reset-db`
3. Then: `python run.py init-db`

## Features Overview

### Security Features
- ✅ bcrypt password hashing
- ✅ JWT token authentication
- ✅ Role-based access control (Admin/User)
- ✅ Account lockout after failed attempts
- ✅ reCAPTCHA integration
- ✅ SQL injection prevention
- ✅ CSRF protection
- ✅ Security event logging

### User Management
- ✅ User registration and login
- ✅ Password strength requirements
- ✅ User profile management
- ✅ Admin user management panel

### Admin Features
- ✅ Admin dashboard with metrics
- ✅ User management (view, edit, lock, unlock, delete)
- ✅ Security logs and login attempt monitoring
- ✅ System statistics and reporting

## Default Accounts

| Username | Password | Role |
|----------|----------|------|
| admin    | Admin@123456 | Administrator |
| testuser | Test@123456  | Regular User |

**🔐 SECURITY WARNING: Change these default passwords immediately after first login!**

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the application logs
3. Ensure all prerequisites are properly installed
4. Verify XAMPP MySQL is running and accessible

## Project Structure

```
secure_login_system/
├── app/                    # Application package
│   ├── auth/              # Authentication blueprint
│   ├── main/              # Main application blueprint  
│   ├── admin/             # Admin panel blueprint
│   ├── static/            # CSS, JS, images
│   ├── templates/         # HTML templates
│   ├── models.py          # Database models
│   └── forms.py           # WTForms forms
├── config.py              # Configuration settings
├── run.py                 # Application entry point
├── requirements.txt       # Python dependencies
└── README.md             # This file
```
