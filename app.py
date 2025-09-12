"""
JustEat Technology - Food Ordering Web Application
Main Flask application entry point
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import re
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import NotFound
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///food_ordering.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
from models import db
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import models and routes
from models import User, Restaurant, MenuItem, Order, OrderItem, Cart, UserPreference, Review
from routes import auth_bp, customer_bp, restaurant_bp, main_bp

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(customer_bp, url_prefix='/customer')
app.register_blueprint(restaurant_bp, url_prefix='/restaurant')

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    logger.warning(f"404 error: {request.url}")
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    logger.error(f"500 error: {error}")
    return render_template('errors/500.html'), 500

@app.context_processor
def inject_user():
    """Inject current user into template context"""
    return dict(current_user=current_user)

@app.context_processor
def inject_image_paths():
    """Expose centralized image paths and helpers to all templates."""
    # Optional explicit overrides for restaurant images (name -> static path)
    # Add entries here if a restaurant image file doesn't match the slug logic or extension
    RESTAURANT_IMAGES = {
        # Map lowercase restaurant names to specific image files
        "mario's italian bistro": url_for('static', filename='images/restaurants/marrio.jpg'),
        "spice palace": url_for('static', filename='images/restaurants/spice.jpg'),
        "dragon wok": url_for('static', filename='images/restaurants/dragon.jpeg'),
        "green leaf cafe": url_for('static', filename='images/restaurants/green.jpg'),
        "burger junction": url_for('static', filename='images/restaurants/burger.jpg'),
        "sushi zen": url_for('static', filename='images/restaurants/sushi.jpeg'),
        "taco fiesta": url_for('static', filename='images/restaurants/taco.jpg'),
        "bakery corner": url_for('static', filename='images/restaurants/bakery.jpg'),
    }

    def restaurant_image(restaurant_name: str) -> str:
        if not restaurant_name:
            return url_for('static', filename='images/restaurants/default.jpg')
        normalized = restaurant_name.strip().lower()
        if normalized in RESTAURANT_IMAGES:
            return RESTAURANT_IMAGES[normalized]
        slug = re.sub(r"[^a-z0-9_\-]", "", normalized.replace(" ", "_"))

        # Try multiple extensions automatically
        possible_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        for ext in possible_extensions:
            rel_path = f'images/restaurants/{slug}{ext}'
            abs_path = os.path.join(app.static_folder, 'images', 'restaurants', f'{slug}{ext}')
            if os.path.exists(abs_path):
                return url_for('static', filename=rel_path)

        # Fallback default
        return url_for('static', filename='images/restaurants/default.jpg')

    IMAGE_PATHS = {
        # Backdrops used across pages/sections
        # All background images are organized in a single dictionary
        'backgrounds': {
            'hero': url_for('static', filename='images/header-bg.jpg'),
            'featured': url_for('static', filename='images/header-bg.jpg'),
            'login': url_for('static', filename='images/header-bg.jpg'),
        },
        # The duplicate top-level keys 'hero' and 'featured_bg' exist for backwards compatibility
        # with older templates that haven't been updated to use the new nested structure.
        # TODO: Update all templates to use IMAGE_PATHS.backgrounds.* and remove these legacy keys
        'hero': url_for('static', filename='images/header-bg.jpg'),  # Legacy key
        'featured_bg': url_for('static', filename='images/header-bg.jpg'),  # Legacy key
        # Food category chip images
        'foods': {
            'pizza': url_for('static', filename='images/food-categories/pizza.jpg'),
            'biryani': url_for('static', filename='images/food-categories/biryani.jpg'),
            'daily_meal': url_for('static', filename='images/food-categories/Daily-Meal.png'),
            'bowl': url_for('static', filename='images/food-categories/bowl.jpeg'),
            'thali': url_for('static', filename='images/food-categories/thali.jpg'),
            'thin_crust': url_for('static', filename='images/food-categories/thin.jpeg'),
            'rolls': url_for('static', filename='images/food-categories/rolls.jpeg'),
            'light_meal': url_for('static', filename='images/food-categories/light.jpg'),
            'high_protein': url_for('static', filename='images/food-categories/high.jpg'),
            'sandwich': url_for('static', filename='images/food-categories/sandwich.jpeg'),
        },
        # Optional explicit map for restaurant images (if you prefer not to rely on slugging)
        # Keys must be lowercase restaurant names; values are url_for paths
        'restaurants': RESTAURANT_IMAGES,
    }

    return dict(IMAGE_PATHS=IMAGE_PATHS, restaurant_image=restaurant_image)

def create_tables():
    """Create database tables"""
    with app.app_context():
        db.create_all()
        logger.info("Database tables created successfully")

def seed_database():
    """Seed database with initial data"""
    from seed_data import seed_all_data
    with app.app_context():
        seed_all_data()
        logger.info("Database seeded successfully")

if __name__ == '__main__':
    # Create tables and seed data
    create_tables()
    seed_database()
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
