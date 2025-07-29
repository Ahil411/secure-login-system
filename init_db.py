#!/usr/bin/env python3
"""
Database Initialization Script for Secure Login System

This script creates the MySQL database and tables required for the application.
Run this script before starting the application for the first time.
"""

import mysql.connector
import sys
import os

def create_database():
    """Create the MySQL database if it doesn't exist"""
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''  # Default XAMPP password is empty
        )

        cursor = connection.cursor()

        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS secure_login_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✅ Database 'secure_login_db' created successfully!")

        # Create a user for the application (optional, for better security)
        try:
            cursor.execute("CREATE USER IF NOT EXISTS 'flask_user'@'localhost' IDENTIFIED BY 'flask_password'")
            cursor.execute("GRANT ALL PRIVILEGES ON secure_login_db.* TO 'flask_user'@'localhost'")
            cursor.execute("FLUSH PRIVILEGES")
            print("✅ Database user 'flask_user' created with appropriate privileges!")
        except mysql.connector.Error as user_error:
            print(f"⚠️  Warning: Could not create database user: {user_error}")
            print("   Using root user is acceptable for development.")

        cursor.close()
        connection.close()

        return True

    except mysql.connector.Error as error:
        print(f"❌ Error creating database: {error}")
        print("\n📋 Troubleshooting:")
        print("   1. Make sure XAMPP is running")
        print("   2. Make sure MySQL service is started in XAMPP")
        print("   3. Check MySQL credentials in config.py")
        return False

def test_connection():
    """Test the database connection"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='secure_login_db'
        )

        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if result:
            print("✅ Database connection test successful!")
            return True
        else:
            print("❌ Database connection test failed!")
            return False

    except mysql.connector.Error as error:
        print(f"❌ Database connection test failed: {error}")
        return False

def main():
    print("🗄️  Initializing MySQL Database for Secure Login System...")
    print("=" * 60)

    # Check if MySQL is available
    try:
        import mysql.connector
    except ImportError:
        print("❌ mysql-connector-python is not installed!")
        print("   Install it with: pip install mysql-connector-python")
        sys.exit(1)

    # Create database
    if create_database():
        print("\n🔍 Testing database connection...")
        if test_connection():
            print("\n✅ Database initialization completed successfully!")
            print("\n📝 Next steps:")
            print("   1. Run: python run.py")
            print("   2. Visit: http://localhost:5000")
            print("   3. Login with admin/Admin@123456")
        else:
            print("\n❌ Database connection test failed!")
            sys.exit(1)
    else:
        print("\n❌ Database initialization failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
