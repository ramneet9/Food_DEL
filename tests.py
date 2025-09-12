"""
Unit tests for the Food Ordering Application
"""

import unittest
import os
import tempfile
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Import the application components
from app import app, db
from models import User, Restaurant, MenuItem, Order, OrderItem, Cart, UserPreference, Review

# Initialize db with app context
with app.app_context():
    db.init_app(app)

class TestCase(unittest.TestCase):
    """Base test case with setup and teardown"""
    
    def setUp(self):
        """Set up test database and client"""
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
            self.create_test_data()
    
    def tearDown(self):
        """Clean up after tests"""
        os.close(self.db_fd)
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def create_test_data(self):
        """Create test data for all tests"""
        # Create test users
        self.customer = User(
            username='test_customer',
            email='customer@test.com',
            role='customer',
            first_name='Test',
            last_name='Customer'
        )
        self.customer.set_password('password123')
        
        self.restaurant_owner = User(
            username='test_owner',
            email='owner@test.com',
            role='restaurant_owner',
            first_name='Test',
            last_name='Owner'
        )
        self.restaurant_owner.set_password('password123')
        
        db.session.add(self.customer)
        db.session.add(self.restaurant_owner)
        db.session.commit()
        
        # Create test restaurant
        self.restaurant = Restaurant(
            name='Test Restaurant',
            description='A test restaurant',
            cuisine_type='Italian',
            location='Test City',
            phone='1234567890',
            owner_id=self.restaurant_owner.id
        )
        db.session.add(self.restaurant)
        db.session.commit()
        
        # Create test menu item
        self.menu_item = MenuItem(
            name='Test Pizza',
            description='A test pizza',
            price=15.99,
            category='Pizza',
            cuisine_type='Italian',
            restaurant_id=self.restaurant.id
        )
        db.session.add(self.menu_item)
        db.session.commit()

class TestUserModel(TestCase):
    """Test User model functionality"""
    
    def test_user_creation(self):
        """Test user creation and password hashing"""
        user = User(
            username='new_user',
            email='new@test.com',
            role='customer',
            first_name='New',
            last_name='User'
        )
        user.set_password('testpassword')
        
        self.assertTrue(user.check_password('testpassword'))
        self.assertFalse(user.check_password('wrongpassword'))
        self.assertTrue(user.is_customer())
        self.assertFalse(user.is_restaurant_owner())
    
    def test_restaurant_owner_role(self):
        """Test restaurant owner role functionality"""
        self.assertTrue(self.restaurant_owner.is_restaurant_owner())
        self.assertFalse(self.restaurant_owner.is_customer())

class TestRestaurantModel(TestCase):
    """Test Restaurant model functionality"""
    
    def test_restaurant_creation(self):
        """Test restaurant creation"""
        restaurant = Restaurant(
            name='New Restaurant',
            description='A new restaurant',
            cuisine_type='Chinese',
            location='New City',
            owner_id=self.restaurant_owner.id
        )
        db.session.add(restaurant)
        db.session.commit()
        
        self.assertEqual(restaurant.name, 'New Restaurant')
        self.assertEqual(restaurant.owner_id, self.restaurant_owner.id)

class TestMenuItemModel(TestCase):
    """Test MenuItem model functionality"""
    
    def test_menu_item_creation(self):
        """Test menu item creation"""
        menu_item = MenuItem(
            name='Test Burger',
            description='A test burger',
            price=12.99,
            category='Burger',
            cuisine_type='American',
            restaurant_id=self.restaurant.id
        )
        db.session.add(menu_item)
        db.session.commit()
        
        self.assertEqual(menu_item.name, 'Test Burger')
        self.assertEqual(menu_item.price, 12.99)
        self.assertEqual(menu_item.restaurant_id, self.restaurant.id)
    
    def test_mostly_ordered_functionality(self):
        """Test mostly ordered item detection"""
        # Initially should not be mostly ordered
        self.assertFalse(self.menu_item.is_mostly_ordered())
        
        # Add some order items to make it mostly ordered
        order = Order(
            order_number='TEST001',
            total_amount=15.99,
            customer_id=self.customer.id,
            restaurant_id=self.restaurant.id
        )
        db.session.add(order)
        db.session.flush()
        
        # Add order item
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=self.menu_item.id,
            quantity=15,  # More than 10
            price=15.99
        )
        db.session.add(order_item)
        db.session.commit()
        
        # Now it should be mostly ordered
        self.assertTrue(self.menu_item.is_mostly_ordered())

class TestOrderModel(TestCase):
    """Test Order model functionality"""
    
    def test_order_creation(self):
        """Test order creation"""
        order = Order(
            order_number='ORDER001',
            total_amount=25.99,
            customer_id=self.customer.id,
            restaurant_id=self.restaurant.id
        )
        db.session.add(order)
        db.session.commit()
        
        self.assertEqual(order.order_number, 'ORDER001')
        self.assertEqual(order.total_amount, 25.99)
        self.assertEqual(order.status, 'pending')  # Default status

class TestCartModel(TestCase):
    """Test Cart model functionality"""
    
    def test_cart_item_creation(self):
        """Test cart item creation"""
        cart_item = Cart(
            customer_id=self.customer.id,
            menu_item_id=self.menu_item.id,
            quantity=2
        )
        db.session.add(cart_item)
        db.session.commit()
        
        self.assertEqual(cart_item.customer_id, self.customer.id)
        self.assertEqual(cart_item.menu_item_id, self.menu_item.id)
        self.assertEqual(cart_item.quantity, 2)

class TestUserPreferenceModel(TestCase):
    """Test UserPreference model functionality"""
    
    def test_user_preference_creation(self):
        """Test user preference creation"""
        preference = UserPreference(
            user_id=self.customer.id,
            preference_type='favorite_cuisine',
            preference_value='Italian'
        )
        db.session.add(preference)
        db.session.commit()
        
        self.assertEqual(preference.user_id, self.customer.id)
        self.assertEqual(preference.preference_type, 'favorite_cuisine')
        self.assertEqual(preference.preference_value, 'Italian')

class TestReviewModel(TestCase):
    """Test Review model functionality"""
    
    def test_review_creation(self):
        """Test review creation"""
        review = Review(
            rating=5,
            comment='Great food!',
            user_id=self.customer.id,
            restaurant_id=self.restaurant.id
        )
        db.session.add(review)
        db.session.commit()
        
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Great food!')
        self.assertEqual(review.user_id, self.customer.id)
        self.assertEqual(review.restaurant_id, self.restaurant.id)

class TestAuthenticationRoutes(TestCase):
    """Test authentication routes"""
    
    def test_login_page_loads(self):
        """Test that login page loads correctly"""
        response = self.app.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome Back', response.data)
    
    def test_login_with_valid_credentials(self):
        """Test login with valid credentials"""
        response = self.app.post('/auth/login', data={
            'username': 'test_customer',
            'password': 'password123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.app.post('/auth/login', data={
            'username': 'test_customer',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid username or password', response.data)

class TestCustomerRoutes(TestCase):
    """Test customer-specific routes"""
    
    def test_customer_dashboard_requires_login(self):
        """Test that customer dashboard requires login"""
        response = self.app.get('/customer/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_restaurants_page_loads(self):
        """Test that restaurants page loads"""
        response = self.app.get('/customer/restaurants')
        self.assertEqual(response.status_code, 302)  # Redirect to login

class TestRestaurantRoutes(TestCase):
    """Test restaurant owner routes"""
    
    def test_restaurant_dashboard_requires_login(self):
        """Test that restaurant dashboard requires login"""
        response = self.app.get('/restaurant/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_add_restaurant_page_loads(self):
        """Test that add restaurant page loads"""
        response = self.app.get('/restaurant/add-restaurant')
        self.assertEqual(response.status_code, 302)  # Redirect to login

class TestMainRoutes(TestCase):
    """Test main application routes"""
    
    def test_home_page_loads(self):
        """Test that home page loads correctly"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'JustEat Technology', response.data)
    
    def test_logout_redirects(self):
        """Test that logout redirects to home"""
        response = self.app.get('/auth/logout')
        self.assertEqual(response.status_code, 302)  # Redirect

class TestDatabaseRelationships(TestCase):
    """Test database relationships"""
    
    def test_user_restaurant_relationship(self):
        """Test user-restaurant relationship"""
        self.assertEqual(self.restaurant.owner, self.restaurant_owner)
        self.assertIn(self.restaurant, self.restaurant_owner.restaurants)
    
    def test_restaurant_menu_items_relationship(self):
        """Test restaurant-menu items relationship"""
        self.assertEqual(self.menu_item.restaurant, self.restaurant)
        self.assertIn(self.menu_item, self.restaurant.menu_items)
    
    def test_order_relationships(self):
        """Test order relationships"""
        order = Order(
            order_number='TEST001',
            total_amount=15.99,
            customer_id=self.customer.id,
            restaurant_id=self.restaurant.id
        )
        db.session.add(order)
        db.session.commit()
        
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.restaurant, self.restaurant)

if __name__ == '__main__':
    unittest.main()
