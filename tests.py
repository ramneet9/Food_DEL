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

# Note: The app already initializes the SQLAlchemy instance.

class TestCase(unittest.TestCase):
    """Base test case with setup and teardown"""
    
    def setUp(self):
        """Set up test database and client"""
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_EXPIRE_ON_COMMIT'] = False
        
        self.app = app.test_client()
        # Keep an application context active for the duration of each test
        self.ctx = app.app_context()
        self.ctx.push()

        with app.app_context():
            db.create_all()
            self.create_test_data()
    
    def tearDown(self):
        """Clean up after tests"""
        os.close(self.db_fd)
        db.session.remove()
        db.drop_all()
        # Pop the application context
        self.ctx.pop()
    
    def create_test_data(self):
        """Create test data for all tests"""
        # Create test users
        customer = User(
            username='test_customer',
            email='customer@test.com',
            role='customer',
            first_name='Test',
            last_name='Customer'
        )
        customer.set_password('password123')
        
        restaurant_owner = User(
            username='test_owner',
            email='owner@test.com',
            role='restaurant_owner',
            first_name='Test',
            last_name='Owner'
        )
        restaurant_owner.set_password('password123')
        
        db.session.add(customer)
        db.session.add(restaurant_owner)
        db.session.commit()
        self.customer_id = customer.id
        self.restaurant_owner_id = restaurant_owner.id
        
        # Create test restaurant
        restaurant = Restaurant(
            name='Test Restaurant',
            description='A test restaurant',
            cuisine_type='Italian',
            location='Test City',
            phone='1234567890',
            owner_id=self.restaurant_owner_id
        )
        db.session.add(restaurant)
        db.session.commit()
        self.restaurant_id = restaurant.id
        
        # Create test menu item
        menu_item = MenuItem(
            name='Test Pizza',
            description='A test pizza',
            price=15.99,
            category='Pizza',
            cuisine_type='Italian',
            restaurant_id=self.restaurant_id
        )
        db.session.add(menu_item)
        db.session.commit()
        self.menu_item_id = menu_item.id

    # Helpers to fetch fresh instances bound to the current session
    def get_customer(self):
        return db.session.get(User, self.customer_id)

    def get_owner(self):
        return db.session.get(User, self.restaurant_owner_id)

    def get_restaurant(self):
        return db.session.get(Restaurant, self.restaurant_id)

    def get_menu_item(self):
        return db.session.get(MenuItem, self.menu_item_id)

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
        owner = self.get_owner()
        self.assertTrue(owner.is_restaurant_owner())
        self.assertFalse(owner.is_customer())

class TestRestaurantModel(TestCase):
    """Test Restaurant model functionality"""
    
    def test_restaurant_creation(self):
        """Test restaurant creation"""
        restaurant = Restaurant(
            name='New Restaurant',
            description='A new restaurant',
            cuisine_type='Chinese',
            location='New City',
            owner_id=self.restaurant_owner_id
        )
        db.session.add(restaurant)
        db.session.commit()
        
        self.assertEqual(restaurant.name, 'New Restaurant')
        self.assertEqual(restaurant.owner_id, self.restaurant_owner_id)

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
            restaurant_id=self.restaurant_id
        )
        db.session.add(menu_item)
        db.session.commit()
        
        self.assertEqual(menu_item.name, 'Test Burger')
        self.assertEqual(menu_item.price, 12.99)
        self.assertEqual(menu_item.restaurant_id, self.restaurant_id)
    
    def test_mostly_ordered_functionality(self):
        """Test mostly ordered item detection"""
        # Initially should not be mostly ordered
        self.assertFalse(self.get_menu_item().is_mostly_ordered())
        
        # Add some order items to make it mostly ordered
        order = Order(
            order_number='TEST001',
            total_amount=15.99,
            customer_id=self.customer_id,
            restaurant_id=self.restaurant_id
        )
        db.session.add(order)
        db.session.flush()
        
        # Add >10 order items for this menu item (quantity 1 each)
        for i in range(11):
            db.session.add(OrderItem(
                order_id=order.id,
                menu_item_id=self.menu_item_id,
                quantity=1,
                price=15.99
            ))
        db.session.commit()
        
        # Now it should be mostly ordered
        self.assertTrue(self.get_menu_item().is_mostly_ordered())

class TestOrderModel(TestCase):
    """Test Order model functionality"""
    
    def test_order_creation(self):
        """Test order creation"""
        order = Order(
            order_number='ORDER001',
            total_amount=25.99,
            customer_id=self.customer_id,
            restaurant_id=self.restaurant_id
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
            customer_id=self.customer_id,
            menu_item_id=self.menu_item_id,
            quantity=2
        )
        db.session.add(cart_item)
        db.session.commit()
        
        self.assertEqual(cart_item.customer_id, self.customer_id)
        self.assertEqual(cart_item.menu_item_id, self.menu_item_id)
        self.assertEqual(cart_item.quantity, 2)

class TestUserPreferenceModel(TestCase):
    """Test UserPreference model functionality"""
    
    def test_user_preference_creation(self):
        """Test user preference creation"""
        preference = UserPreference(
            user_id=self.customer_id,
            preference_type='favorite_cuisine',
            preference_value='Italian'
        )
        db.session.add(preference)
        db.session.commit()
        
        self.assertEqual(preference.user_id, self.customer_id)
        self.assertEqual(preference.preference_type, 'favorite_cuisine')
        self.assertEqual(preference.preference_value, 'Italian')

class TestReviewModel(TestCase):
    """Test Review model functionality"""
    
    def test_review_creation(self):
        """Test review creation"""
        review = Review(
            rating=5,
            comment='Great food!',
            user_id=self.customer_id,
            restaurant_id=self.restaurant_id
        )
        db.session.add(review)
        db.session.commit()
        
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Great food!')
        self.assertEqual(review.user_id, self.customer_id)
        self.assertEqual(review.restaurant_id, self.restaurant_id)

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

class TestCustomerFlows(TestCase):
    """End-to-end customer flows against JSON endpoints."""

    def login_as_customer(self):
        return self.app.post('/auth/login', data={
            'username': 'test_customer',
            'password': 'password123'
        }, follow_redirects=True)

    def test_add_to_cart_and_place_order(self):
        # Login as customer
        resp = self.login_as_customer()
        self.assertEqual(resp.status_code, 200)

        # Add to cart via API
        add_resp = self.app.post('/customer/add-to-cart', json={
            'menu_item_id': self.menu_item_id,
            'quantity': 2
        })
        self.assertEqual(add_resp.status_code, 200)
        self.assertTrue(add_resp.is_json)
        self.assertTrue(add_resp.get_json().get('success'))

        # Place order
        order_resp = self.app.post('/customer/place-order', json={})
        self.assertEqual(order_resp.status_code, 200)
        self.assertTrue(order_resp.is_json)
        self.assertTrue(order_resp.get_json().get('success'))

        # Verify order persisted for this customer
        orders = Order.query.filter_by(customer_id=self.customer_id).all()
        self.assertGreaterEqual(len(orders), 1)

class TestOwnerFlows(TestCase):
    """End-to-end owner flows to ensure CRUD APIs are stable."""

    def login_as_owner(self):
        return self.app.post('/auth/login', data={
            'username': 'test_owner',
            'password': 'password123'
        }, follow_redirects=True)

    def test_add_restaurant_form_and_menu_crud(self):
        # Login as owner
        resp = self.login_as_owner()
        self.assertEqual(resp.status_code, 200)

        # Add restaurant via form POST
        form_resp = self.app.post('/restaurant/add-restaurant', data={
            'name': 'Owner Test Resto',
            'description': 'Owned by test',
            'cuisine_type': 'Indian',
            'location': 'Delhi',
            'phone': '1111111111',
            'email': 'o@test.com'
        }, follow_redirects=True)
        self.assertEqual(form_resp.status_code, 200)

        # Fetch created restaurant id
        created = Restaurant.query.filter_by(name='Owner Test Resto').first()
        self.assertIsNotNone(created)

        # Add menu item via JSON
        add_item = self.app.post('/restaurant/add-menu-item', json={
            'restaurant_id': created.id,
            'name': 'Paneer Tikka',
            'description': 'Starter',
            'price': 199,
            'category': 'Appetizer',
            'cuisine_type': 'Indian',
            'is_vegetarian': True
        })
        self.assertEqual(add_item.status_code, 200)
        self.assertTrue(add_item.get_json().get('success'))

        item = MenuItem.query.filter_by(restaurant_id=created.id, name='Paneer Tikka').first()
        self.assertIsNotNone(item)

        # Update menu item
        upd_item = self.app.post('/restaurant/update-menu-item', json={
            'id': item.id,
            'price': 209,
            'name': 'Paneer Tikka (Updated)'
        })
        self.assertEqual(upd_item.status_code, 200)
        self.assertTrue(upd_item.get_json().get('success'))
        db.session.refresh(item)
        self.assertEqual(item.price, 209)
        self.assertIn('Updated', item.name)

        # Delete menu item
        del_item = self.app.post('/restaurant/delete-menu-item', json={'id': item.id})
        self.assertEqual(del_item.status_code, 200)
        self.assertTrue(del_item.get_json().get('success'))
        self.assertIsNone(db.session.get(MenuItem, item.id))

    def test_update_order_status(self):
        # Prepare: create customer order for owner's restaurant
        # Login as customer to place an order
        cust_resp = self.app.post('/auth/login', data={
            'username': 'test_customer',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(cust_resp.status_code, 200)

        # Add to cart and place order for existing restaurant/menu
        self.app.post('/customer/add-to-cart', json={'menu_item_id': self.menu_item_id, 'quantity': 1})
        place = self.app.post('/customer/place-order', json={})
        self.assertTrue(place.get_json().get('success'))

        # Find latest order for that restaurant
        order = (
            Order.query.filter_by(restaurant_id=self.restaurant_id)
            .order_by(Order.created_at.desc())
            .first()
        )
        self.assertIsNotNone(order)

        # Login as owner and update status
        self.app.get('/auth/logout')
        owner_login = self.login_as_owner()
        self.assertEqual(owner_login.status_code, 200)

        upd = self.app.post('/restaurant/update-order-status', json={
            'order_id': order.id,
            'status': 'confirmed'
        })
        self.assertEqual(upd.status_code, 200)
        self.assertTrue(upd.get_json().get('success'))
        db.session.refresh(order)
        self.assertEqual(order.status, 'confirmed')

class TestDatabaseRelationships(TestCase):
    """Test database relationships"""
    
    def test_user_restaurant_relationship(self):
        """Test user-restaurant relationship"""
        restaurant = self.get_restaurant()
        owner = self.get_owner()
        self.assertEqual(restaurant.owner.id, owner.id)
        self.assertTrue(any(r.id == restaurant.id for r in owner.restaurants))
    
    def test_restaurant_menu_items_relationship(self):
        """Test restaurant-menu items relationship"""
        menu_item = self.get_menu_item()
        restaurant = self.get_restaurant()
        self.assertEqual(menu_item.restaurant.id, restaurant.id)
        self.assertTrue(any(mi.id == menu_item.id for mi in restaurant.menu_items))
    
    def test_order_relationships(self):
        """Test order relationships"""
        order = Order(
            order_number='TEST001',
            total_amount=15.99,
            customer_id=self.customer_id,
            restaurant_id=self.restaurant_id
        )
        db.session.add(order)
        db.session.commit()
        
        self.assertEqual(order.customer.id, self.customer_id)
        self.assertEqual(order.restaurant.id, self.restaurant_id)

if __name__ == '__main__':
    unittest.main()
