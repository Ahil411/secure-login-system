#!/usr/bin/env python3
"""
Secure Login System - Main Application Entry Point

This is the main entry point for the Secure Login System Flask application.
It initializes the Flask app, creates the database tables, and starts the server.

Features:
- Secure authentication with bcrypt password hashing
- JWT token-based authentication
- Role-based access control (RBAC)
- Account lockout protection
- CAPTCHA integration
- SQL injection prevention
- CSRF protection
- Comprehensive security logging

Author: Cybersecurity Intern
Date: July 2025
"""

import os
import sys
from flask.cli import FlaskGroup
from app import create_app, db
from app.models import User, Role

# Create Flask application
app = create_app(os.getenv('FLASK_CONFIG') or 'development')

# Create CLI group
cli = FlaskGroup(app)

@app.shell_context_processor
def make_shell_context():
    """Make database models available in flask shell"""
    return {
        'db': db,
        'User': User,
        'Role': Role
    }

@app.cli.command()
def init_db():
    """Initialize the database with tables and default data"""
    print("Creating database tables...")
    db.create_all()

    # Create default roles
    admin_role = Role.query.filter_by(name='Admin').first()
    if not admin_role:
        admin_role = Role(name='Admin', description='Administrator with full access')
        db.session.add(admin_role)

    user_role = Role.query.filter_by(name='User').first()
    if not user_role:
        user_role = Role(name='User', description='Regular user with limited access')
        db.session.add(user_role)

    # Create default admin user
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@securelogin.com',
            password='Admin@123456',  # Change this in production!
            role=admin_role
        )
        db.session.add(admin_user)
        print("Created default admin user:")
        print("  Username: admin")
        print("  Password: Admin@123456")
        print("  ⚠  IMPORTANT: Change the default password immediately!")

    # Create default regular user
    test_user = User.query.filter_by(username='testuser').first()
    if not test_user:
        test_user = User(
            username='testuser',
            email='test@securelogin.com',
            password='Test@123456',
            role=user_role
        )
        db.session.add(test_user)
        print("Created test user:")
        print("  Username: testuser")
        print("  Password: Test@123456")

    db.session.commit()
    print("✅ Database initialized successfully!")

@app.cli.command()
def reset_db():
    """Reset the database (drop all tables and recreate)"""
    print("⚠  Resetting database - all data will be lost!")
    response = input("Are you sure? (y/N): ")
    if response.lower() == 'y':
        db.drop_all()
        db.create_all()
        print("✅ Database reset complete!")
    else:
        print("Database reset cancelled.")

@app.cli.command()
def create_admin():
    """Create a new admin user"""
    username = input("Admin username: ")
    email = input("Admin email: ")
    password = input("Admin password: ")

    # Check if user already exists
    if User.query.filter_by(username=username).first():
        print("❌ Username already exists!")
        return

    if User.query.filter_by(email=email).first():
        print("❌ Email already exists!")
        return

    # Get or create admin role
    admin_role = Role.query.filter_by(name='Admin').first()
    if not admin_role:
        admin_role = Role(name='Admin', description='Administrator with full access')
        db.session.add(admin_role)
        db.session.flush()

    # Create admin user
    admin_user = User(
        username=username,
        email=email,
        password=password,
        role=admin_role
    )

    db.session.add(admin_user)
    db.session.commit()

    print(f"✅ Admin user '{username}' created successfully!")

def run_development_server():
    """Run the development server with debug mode"""
    print("🚀 Starting Secure Login System...")
    print("📋 Application Features:")
    print("   • Secure password hashing with bcrypt")
    print("   • JWT token authentication")
    print("   • Role-based access control")
    print("   • Account lockout protection")
    print("   • CAPTCHA integration")
    print("   • SQL injection prevention")
    print("   • CSRF protection")
    print("   • Security event logging")
    print()
    print("🔐 Default Accounts:")
    print("   Admin: admin / Admin@123456")
    print("   User:  testuser / Test@123456")
    print("   ⚠  Change default passwords immediately!")
    print()
    print("🌐 Access the application at: http://localhost:5000")
    print("📊 Admin panel at: http://localhost:5000/admin/dashboard")
    print()

    # Run the Flask development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )

if __name__ == '_main_':
    # Check for CLI commands
    if len(sys.argv) > 1 and sys.argv[1] == 'init-db':
        with app.app_context():
            init_db()
    elif len(sys.argv) > 1 and sys.argv[1] == 'reset-db':
        with app.app_context():
            reset_db()
    elif len(sys.argv) > 1 and sys.argv[1] == 'create-admin':
        with app.app_context():
            create_admin()
    else:
        # Initialize database if it doesn't exist
        with app.app_context():
            if not os.path.exists('instance/secure_login_db'):
                print("🔧 Initializing database...")
                init_db()

        # Run the development server
        run_development_server()