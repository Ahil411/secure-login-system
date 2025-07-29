# secure-login-system
🔐 Secure Login System A Flask-based web application implementing secure user authentication with MySQL database integration. Features user registration, login/logout, role-based access control, and comprehensive security measures including password hashing, account lockout, CSRF protection, and optional reCAPTCHA verification.

Prerequisites
Python 3.8 or higher

XAMPP (Apache + MySQL)
# 1 unpack & enter project
unzip secure_login_system.zip && cd secure_login_system

bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
Install dependencies

bash
pip install --upgrade pip
pip install -r requirements.txt
Start XAMPP services

Open XAMPP Control Panel

Start Apache and MySQL services

Initialize database

bash
python init_db.py
Run the application

bash
python run.py
Access the application

Open browser and go to: http://localhost:5000
If port 5000 is busy, try:
# Run on different port
python -c "from app import create_app; app = create_app(); app.run(port=5001, debug=True)"

Default admin account: admin / Admin@123456

🔧 Configuration
Environment Variables
Create a .env file in the root directory:

text
SECRET_KEY=your-secret-key-here
SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:@localhost/secure_login_db
RECAPTCHA_PUBLIC_KEY=your-recaptcha-public-key
RECAPTCHA_PRIVATE_KEY=your-recaptcha-private-key
Database Configuration
Update MySQL connection in config.py:

python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/database_name'
📱 Usage
User Registration
Navigate to /register

Fill in username, email, and password

Complete reCAPTCHA verification

Account created successfully

User Login
Navigate to /login

Enter credentials

Access dashboard upon successful authentication

Admin Features
User management dashboard at /admin

View security logs and login attempts

Manage user roles and permissions

🔒 Security Features Implementation
Password Security
bcrypt hashing with salt rounds

Minimum password requirements (8+ characters, special chars)

Password confirmation validation

Account Protection
Account lockout after 5 failed attempts

Lockout duration configurable (default: 30 minutes)

Security logging of all authentication events

Session Security
JWT tokens for stateless authentication

Secure session cookies with HttpOnly flag

CSRF tokens on all forms

🧪 Testing
Run the test suite:

bash
python -m pytest tests/
Test coverage includes:

User registration validation

Login/logout functionality

Security feature verification

Database operations

📊 Database Schema
Users Table
sql
CREATE TABLE user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    failed_attempts INT DEFAULT 0,
    locked_until DATETIME NULL
);
🚀 Deployment
Production Considerations
Use environment variables for sensitive configuration

Enable HTTPS/SSL certificates

Configure proper database user permissions

Set up monitoring and logging

Implement backup strategies

XAMPP to Production Migration
Export database using phpMyAdmin

Update connection strings for production database

Configure web server (Apache/Nginx)

🤝 Contributing
Fork the repository

Create a feature branch (git checkout -b feature/amazing-feature)
