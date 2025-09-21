#!/usr/bin/env python3
"""
Setup script for the Food Ordering Application
Run this script to initialize the database and seed data on a new device
"""

import os
import sys

def setup_database():
    """Initialize and setup the database"""
    print("🚀 Setting up Food Ordering Application...")
    
    # Import app and db
    from app import app, db
    from models import User, Restaurant, MenuItem, Order, OrderItem, Cart, UserPreference, Review
    
    with app.app_context():
        print("📁 Creating database tables...")
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Check if data already exists
        from models import Restaurant
        existing_restaurants = Restaurant.query.count()
        
        if existing_restaurants > 0:
            print(f"⚠️  Database already contains {existing_restaurants} restaurants.")
            response = input("Do you want to reset the database? (y/N): ").lower()
            if response == 'y':
                print("🗑️  Dropping all tables...")
                db.drop_all()
                db.create_all()
                print("✅ Database reset successfully!")
            else:
                print("ℹ️  Keeping existing data. Skipping seed data.")
                return
        
        print("🌱 Seeding database with initial data...")
        
        # Import and run consolidated seed
        from seed_data import seed_all_data
        
        try:
            seed_all_data()
            
            print("✅ Database setup completed successfully!")
            print("🎉 You can now run: python app.py")
            
        except Exception as e:
            print(f"❌ Error during setup: {e}")
            sys.exit(1)

if __name__ == "__main__":
    setup_database()
