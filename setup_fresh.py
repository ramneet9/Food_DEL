#!/usr/bin/env python3
"""
Fresh setup script for the Food Ordering Application
Use this for a completely fresh installation on a new device
"""

import os
import sys

def setup_fresh_database():
    """Initialize and setup a fresh database"""
    print("🚀 Setting up Food Ordering Application (Fresh Install)...")
    
    # Import app and db
    from app import app, db
    from models import User, Restaurant, MenuItem, Order, OrderItem, Cart, UserPreference, Review
    
    with app.app_context():
        print("🗑️  Dropping existing tables...")
        db.drop_all()
        
        print("📁 Creating fresh database tables...")
        db.create_all()
        print("✅ Database tables created successfully!")
        
        print("🌱 Seeding database with initial data...")
        
        # Import and run consolidated seed
        from seed_data import seed_all_data
        
        try:
            seed_all_data()
            
            print("✅ Fresh database setup completed successfully!")
            print("🎉 You can now run: python app.py")
            print("\n📋 Demo Accounts:")
            print("   Customer: john_doe / password123")
            print("   Restaurant Owner: chef_mario / password123")
            
        except Exception as e:
            print(f"❌ Error during setup: {e}")
            sys.exit(1)

if __name__ == "__main__":
    setup_fresh_database()
