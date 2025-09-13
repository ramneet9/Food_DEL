"""
Seed data for the Food Ordering Application
"""

from datetime import datetime
from models import db, User, Restaurant, MenuItem, UserPreference, Review

def seed_all_data():
    """Seed all initial data"""
    try:
        # Check if data already exists
        if User.query.first():
            print("Data already exists, skipping seed...")
            return
        
        # Create users
        seed_users()
        
        # Create restaurants
        seed_restaurants()
        
        # Create menu items
        seed_menu_items()
        
        # Create user preferences
        seed_user_preferences()
        
        # Create reviews
        seed_reviews()
        
        print("Database seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.session.rollback()

def seed_users():
    """Seed users data"""
    users_data = [
        # Customers
        {
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'password123',
            'role': 'customer',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+1234567890',
            'address': '123 Main St, City, State'
        },
        {
            'username': 'jane_smith',
            'email': 'jane@example.com',
            'password': 'password123',
            'role': 'customer',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'phone': '+1234567891',
            'address': '456 Oak Ave, City, State'
        },
        {
            'username': 'mike_wilson',
            'email': 'mike@example.com',
            'password': 'password123',
            'role': 'customer',
            'first_name': 'Mike',
            'last_name': 'Wilson',
            'phone': '+1234567892',
            'address': '789 Pine Rd, City, State'
        },
        
        # Restaurant Owners
        {
            'username': 'chef_mario',
            'email': 'mario@italianbistro.com',
            'password': 'password123',
            'role': 'restaurant_owner',
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'phone': '+1234567893',
            'address': '321 Restaurant Row, City, State'
        },
        {
            'username': 'chef_raj',
            'email': 'raj@spicepalace.com',
            'password': 'password123',
            'role': 'restaurant_owner',
            'first_name': 'Raj',
            'last_name': 'Patel',
            'phone': '+1234567894',
            'address': '654 Curry Lane, City, State'
        },
        {
            'username': 'chef_li',
            'email': 'li@dragonwok.com',
            'password': 'password123',
            'role': 'restaurant_owner',
            'first_name': 'Li',
            'last_name': 'Wang',
            'phone': '+1234567895',
            'address': '987 Bamboo St, City, State'
        },
        {
            'username': 'chef_sarah',
            'email': 'sarah@greenleaf.com',
            'password': 'password123',
            'role': 'restaurant_owner',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'phone': '+1234567896',
            'address': '147 Garden Way, City, State'
        },
        {
            'username': 'chef_antonio',
            'email': 'antonio@tacofiesta.com',
            'password': 'password123',
            'role': 'restaurant_owner',
            'first_name': 'Antonio',
            'last_name': 'Garcia',
            'phone': '+1234567897',
            'address': '258 Taco Street, City, State'
        },
        {
            'username': 'chef_emily',
            'email': 'emily@bakerycorner.com',
            'password': 'password123',
            'role': 'restaurant_owner',
            'first_name': 'Emily',
            'last_name': 'Davis',
            'phone': '+1234567898',
            'address': '369 Sweet Avenue, City, State'
        }
    ]
    
    for user_data in users_data:
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            role=user_data['role'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            phone=user_data['phone'],
            address=user_data['address']
        )
        user.set_password(user_data['password'])
        db.session.add(user)
    
    db.session.commit()
    print("Users seeded successfully!")

def seed_restaurants():
    """Seed restaurants data"""
    # Get restaurant owners
    mario = User.query.filter_by(username='chef_mario').first()
    raj = User.query.filter_by(username='chef_raj').first()
    li = User.query.filter_by(username='chef_li').first()
    sarah = User.query.filter_by(username='chef_sarah').first()
    antonio = User.query.filter_by(username='chef_antonio').first()
    emily = User.query.filter_by(username='chef_emily').first()
    
    restaurants_data = [
        {
            'name': 'Mario\'s Italian Bistro',
            'description': 'Authentic Italian cuisine with fresh ingredients and traditional recipes passed down through generations.',
            'cuisine_type': 'Italian',
            'location': 'Downtown',
            'phone': '+1234567001',
            'email': 'info@italianbistro.com',
            'owner_id': mario.id
        },
        {
            'name': 'Spice Palace',
            'description': 'Exotic Indian flavors with aromatic spices and traditional cooking methods.',
            'cuisine_type': 'Indian',
            'location': 'Midtown',
            'phone': '+1234567002',
            'email': 'info@spicepalace.com',
            'owner_id': raj.id
        },
        {
            'name': 'Dragon Wok',
            'description': 'Modern Chinese cuisine with fresh ingredients and authentic flavors.',
            'cuisine_type': 'Chinese',
            'location': 'Chinatown',
            'phone': '+1234567003',
            'email': 'info@dragonwok.com',
            'owner_id': li.id
        },
        {
            'name': 'Green Leaf Cafe',
            'description': 'Healthy vegetarian and vegan options with organic ingredients.',
            'cuisine_type': 'Vegetarian',
            'location': 'Uptown',
            'phone': '+1234567004',
            'email': 'info@greenleaf.com',
            'owner_id': sarah.id
        },
        {
            'name': 'Burger Junction',
            'description': 'Gourmet burgers with premium ingredients and creative combinations.',
            'cuisine_type': 'American',
            'location': 'Downtown',
            'phone': '+1234567005',
            'email': 'info@burgerjunction.com',
            'owner_id': mario.id
        },
        {
            'name': 'Sushi Zen',
            'description': 'Fresh sushi and Japanese cuisine with traditional techniques.',
            'cuisine_type': 'Japanese',
            'location': 'Midtown',
            'phone': '+1234567006',
            'email': 'info@sushizen.com',
            'owner_id': li.id
        },
        {
            'name': 'Taco Fiesta',
            'description': 'Authentic Mexican street food with fresh ingredients and bold flavors.',
            'cuisine_type': 'Mexican',
            'location': 'Downtown',
            'phone': '+1234567007',
            'email': 'info@tacofiesta.com',
            'owner_id': antonio.id
        },
        {
            'name': 'Bakery Corner',
            'description': 'Fresh baked goods, pastries, and artisanal breads made daily.',
            'cuisine_type': 'Bakery',
            'location': 'Uptown',
            'phone': '+1234567008',
            'email': 'info@bakerycorner.com',
            'owner_id': emily.id
        }
    ]
    
    for restaurant_data in restaurants_data:
        restaurant = Restaurant(**restaurant_data)
        db.session.add(restaurant)
    
    db.session.commit()
    print("Restaurants seeded successfully!")

def seed_menu_items():
    """Seed menu items data"""
    # Get restaurants
    italian_bistro = Restaurant.query.filter_by(name='Mario\'s Italian Bistro').first()
    spice_palace = Restaurant.query.filter_by(name='Spice Palace').first()
    dragon_wok = Restaurant.query.filter_by(name='Dragon Wok').first()
    green_leaf = Restaurant.query.filter_by(name='Green Leaf Cafe').first()
    burger_junction = Restaurant.query.filter_by(name='Burger Junction').first()
    sushi_zen = Restaurant.query.filter_by(name='Sushi Zen').first()
    taco_fiesta = Restaurant.query.filter_by(name='Taco Fiesta').first()
    bakery_corner = Restaurant.query.filter_by(name='Bakery Corner').first()
    
    menu_items_data = [
        # Italian Bistro
        {
            'name': 'Margherita Pizza',
            'description': 'Classic pizza with tomato sauce, mozzarella, and fresh basil',
            'price': 16.99,
            'category': 'Pizza',
            'cuisine_type': 'Italian',
            'is_vegetarian': True,
            'restaurant_id': italian_bistro.id,
            'is_special': True
        },
        {
            'name': 'Spaghetti Carbonara',
            'description': 'Creamy pasta with eggs, cheese, and pancetta',
            'price': 18.99,
            'category': 'Pasta',
            'cuisine_type': 'Italian',
            'is_vegetarian': False,
            'restaurant_id': italian_bistro.id
        },
        {
            'name': 'Chicken Parmigiana',
            'description': 'Breaded chicken breast with marinara sauce and mozzarella',
            'price': 22.99,
            'category': 'Main Course',
            'cuisine_type': 'Italian',
            'is_vegetarian': False,
            'restaurant_id': italian_bistro.id
        },
        {
            'name': 'Tiramisu',
            'description': 'Classic Italian dessert with coffee and mascarpone',
            'price': 8.99,
            'category': 'Dessert',
            'cuisine_type': 'Italian',
            'is_vegetarian': True,
            'restaurant_id': italian_bistro.id
        },
        
        # Spice Palace
        {
            'name': 'Chicken Tikka Masala',
            'description': 'Tender chicken in creamy tomato sauce with aromatic spices',
            'price': 19.99,
            'category': 'Curry',
            'cuisine_type': 'Indian',
            'is_vegetarian': False,
            'restaurant_id': spice_palace.id,
            'is_deal_of_day': True
        },
        {
            'name': 'Vegetable Biryani',
            'description': 'Fragrant basmati rice with mixed vegetables and spices',
            'price': 16.99,
            'category': 'Rice',
            'cuisine_type': 'Indian',
            'is_vegetarian': True,
            'restaurant_id': spice_palace.id
        },
        {
            'name': 'Butter Chicken',
            'description': 'Creamy tomato-based curry with tender chicken pieces',
            'price': 21.99,
            'category': 'Curry',
            'cuisine_type': 'Indian',
            'is_vegetarian': False,
            'restaurant_id': spice_palace.id
        },
        {
            'name': 'Naan Bread',
            'description': 'Fresh baked flatbread',
            'price': 4.99,
            'category': 'Bread',
            'cuisine_type': 'Indian',
            'is_vegetarian': True,
            'restaurant_id': spice_palace.id
        },
        
        # Dragon Wok
        {
            'name': 'Kung Pao Chicken',
            'description': 'Spicy stir-fried chicken with peanuts and vegetables',
            'price': 17.99,
            'category': 'Stir Fry',
            'cuisine_type': 'Chinese',
            'is_vegetarian': False,
            'restaurant_id': dragon_wok.id
        },
        {
            'name': 'Sweet and Sour Pork',
            'description': 'Crispy pork with bell peppers in tangy sauce',
            'price': 18.99,
            'category': 'Main Course',
            'cuisine_type': 'Chinese',
            'is_vegetarian': False,
            'restaurant_id': dragon_wok.id
        },
        {
            'name': 'Vegetable Lo Mein',
            'description': 'Stir-fried noodles with mixed vegetables',
            'price': 14.99,
            'category': 'Noodles',
            'cuisine_type': 'Chinese',
            'is_vegetarian': True,
            'restaurant_id': dragon_wok.id
        },
        {
            'name': 'Spring Rolls',
            'description': 'Crispy vegetable spring rolls with sweet chili sauce',
            'price': 7.99,
            'category': 'Appetizer',
            'cuisine_type': 'Chinese',
            'is_vegetarian': True,
            'restaurant_id': dragon_wok.id
        },
        
        # Green Leaf Cafe
        {
            'name': 'Quinoa Buddha Bowl',
            'description': 'Nutritious bowl with quinoa, roasted vegetables, and tahini dressing',
            'price': 15.99,
            'category': 'Bowl',
            'cuisine_type': 'Vegetarian',
            'is_vegetarian': True,
            'is_vegan': True,
            'is_gluten_free': True,
            'restaurant_id': green_leaf.id
        },
        {
            'name': 'Veggie Burger',
            'description': 'Plant-based patty with lettuce, tomato, and vegan mayo',
            'price': 13.99,
            'category': 'Burger',
            'cuisine_type': 'Vegetarian',
            'is_vegetarian': True,
            'is_vegan': True,
            'restaurant_id': green_leaf.id
        },
        {
            'name': 'Green Smoothie',
            'description': 'Blend of spinach, banana, mango, and coconut water',
            'price': 8.99,
            'category': 'Beverage',
            'cuisine_type': 'Vegetarian',
            'is_vegetarian': True,
            'is_vegan': True,
            'restaurant_id': green_leaf.id
        },
        {
            'name': 'Avocado Toast',
            'description': 'Smashed avocado on sourdough with cherry tomatoes',
            'price': 11.99,
            'category': 'Breakfast',
            'cuisine_type': 'Vegetarian',
            'is_vegetarian': True,
            'is_vegan': True,
            'restaurant_id': green_leaf.id
        },
        
        # Burger Junction
        {
            'name': 'Classic Cheeseburger',
            'description': 'Beef patty with cheese, lettuce, tomato, and special sauce',
            'price': 14.99,
            'category': 'Burger',
            'cuisine_type': 'American',
            'is_vegetarian': False,
            'restaurant_id': burger_junction.id
        },
        {
            'name': 'BBQ Bacon Burger',
            'description': 'Beef patty with bacon, BBQ sauce, and onion rings',
            'price': 17.99,
            'category': 'Burger',
            'cuisine_type': 'American',
            'is_vegetarian': False,
            'restaurant_id': burger_junction.id
        },
        {
            'name': 'Chicken Wings',
            'description': 'Crispy wings with choice of buffalo, BBQ, or honey mustard',
            'price': 12.99,
            'category': 'Appetizer',
            'cuisine_type': 'American',
            'is_vegetarian': False,
            'restaurant_id': burger_junction.id
        },
        {
            'name': 'French Fries',
            'description': 'Golden crispy fries with sea salt',
            'price': 6.99,
            'category': 'Side',
            'cuisine_type': 'American',
            'is_vegetarian': True,
            'restaurant_id': burger_junction.id
        },
        
        # Sushi Zen
        {
            'name': 'California Roll',
            'description': 'Crab, avocado, and cucumber roll',
            'price': 12.99,
            'category': 'Sushi Roll',
            'cuisine_type': 'Japanese',
            'is_vegetarian': False,
            'restaurant_id': sushi_zen.id
        },
        {
            'name': 'Salmon Nigiri',
            'description': 'Fresh salmon over seasoned rice',
            'price': 15.99,
            'category': 'Nigiri',
            'cuisine_type': 'Japanese',
            'is_vegetarian': False,
            'restaurant_id': sushi_zen.id
        },
        {
            'name': 'Vegetable Tempura',
            'description': 'Lightly battered and fried seasonal vegetables',
            'price': 11.99,
            'category': 'Appetizer',
            'cuisine_type': 'Japanese',
            'is_vegetarian': True,
            'restaurant_id': sushi_zen.id
        },
        {
            'name': 'Miso Soup',
            'description': 'Traditional Japanese soup with tofu and seaweed',
            'price': 4.99,
            'category': 'Soup',
            'cuisine_type': 'Japanese',
            'is_vegetarian': True,
            'restaurant_id': sushi_zen.id
        },
        
        # Taco Fiesta
        {
            'name': 'Carnitas Tacos',
            'description': 'Slow-cooked pork with onions, cilantro, and lime',
            'price': 12.99,
            'category': 'Tacos',
            'cuisine_type': 'Mexican',
            'is_vegetarian': False,
            'restaurant_id': taco_fiesta.id
        },
        {
            'name': 'Veggie Quesadilla',
            'description': 'Grilled tortilla with cheese, peppers, and onions',
            'price': 10.99,
            'category': 'Quesadilla',
            'cuisine_type': 'Mexican',
            'is_vegetarian': True,
            'restaurant_id': taco_fiesta.id
        },
        {
            'name': 'Churros',
            'description': 'Crispy fried dough with cinnamon sugar',
            'price': 6.99,
            'category': 'Dessert',
            'cuisine_type': 'Mexican',
            'is_vegetarian': True,
            'restaurant_id': taco_fiesta.id
        },
        
        # Bakery Corner
        {
            'name': 'Croissant',
            'description': 'Buttery, flaky French pastry',
            'price': 3.99,
            'category': 'Pastry',
            'cuisine_type': 'Bakery',
            'is_vegetarian': True,
            'restaurant_id': bakery_corner.id
        },
        {
            'name': 'Chocolate Chip Cookies',
            'description': 'Fresh baked cookies with premium chocolate chips',
            'price': 2.99,
            'category': 'Cookies',
            'cuisine_type': 'Bakery',
            'is_vegetarian': True,
            'restaurant_id': bakery_corner.id
        },
        {
            'name': 'Artisan Bread',
            'description': 'Fresh baked sourdough bread',
            'price': 5.99,
            'category': 'Bread',
            'cuisine_type': 'Bakery',
            'is_vegetarian': True,
            'restaurant_id': bakery_corner.id
        }
    ]
    
    for item_data in menu_items_data:
        menu_item = MenuItem(**item_data)
        db.session.add(menu_item)
    
    db.session.commit()
    print("Menu items seeded successfully!")

def seed_user_preferences():
    """Seed user preferences data"""
    # Get users
    john = User.query.filter_by(username='john_doe').first()
    jane = User.query.filter_by(username='jane_smith').first()
    mike = User.query.filter_by(username='mike_wilson').first()
    
    preferences_data = [
        # John's preferences
        {'user_id': john.id, 'preference_type': 'favorite_cuisine', 'preference_value': 'Italian'},
        {'user_id': john.id, 'preference_type': 'favorite_cuisine', 'preference_value': 'American'},
        {'user_id': john.id, 'preference_type': 'dietary_restriction', 'preference_value': 'no_spicy'},
        
        # Jane's preferences
        {'user_id': jane.id, 'preference_type': 'favorite_cuisine', 'preference_value': 'Indian'},
        {'user_id': jane.id, 'preference_type': 'favorite_cuisine', 'preference_value': 'Vegetarian'},
        {'user_id': jane.id, 'preference_type': 'dietary_restriction', 'preference_value': 'vegetarian'},
        
        # Mike's preferences
        {'user_id': mike.id, 'preference_type': 'favorite_cuisine', 'preference_value': 'Chinese'},
        {'user_id': mike.id, 'preference_type': 'favorite_cuisine', 'preference_value': 'Japanese'},
        {'user_id': mike.id, 'preference_type': 'dietary_restriction', 'preference_value': 'gluten_free'}
    ]
    
    for pref_data in preferences_data:
        preference = UserPreference(**pref_data)
        db.session.add(preference)
    
    db.session.commit()
    print("User preferences seeded successfully!")

def seed_reviews():
    """Seed reviews data"""
    # Get users and restaurants
    john = User.query.filter_by(username='john_doe').first()
    jane = User.query.filter_by(username='jane_smith').first()
    mike = User.query.filter_by(username='mike_wilson').first()
    
    italian_bistro = Restaurant.query.filter_by(name='Mario\'s Italian Bistro').first()
    spice_palace = Restaurant.query.filter_by(name='Spice Palace').first()
    dragon_wok = Restaurant.query.filter_by(name='Dragon Wok').first()
    
    reviews_data = [
        {
            'rating': 5,
            'comment': 'Amazing pizza! The Margherita was perfect with fresh basil.',
            'user_id': john.id,
            'restaurant_id': italian_bistro.id
        },
        {
            'rating': 4,
            'comment': 'Great Italian food, but a bit pricey.',
            'user_id': jane.id,
            'restaurant_id': italian_bistro.id
        },
        {
            'rating': 5,
            'comment': 'Best Indian food in town! The Chicken Tikka Masala was incredible.',
            'user_id': jane.id,
            'restaurant_id': spice_palace.id
        },
        {
            'rating': 4,
            'comment': 'Good Chinese food, quick service.',
            'user_id': mike.id,
            'restaurant_id': dragon_wok.id
        },
        {
            'rating': 3,
            'comment': 'Decent food but could be better.',
            'user_id': john.id,
            'restaurant_id': dragon_wok.id
        }
    ]
    
    for review_data in reviews_data:
        review = Review(**review_data)
        db.session.add(review)
    
    db.session.commit()
    
    # Update restaurant ratings and total_reviews
    restaurants = Restaurant.query.all()
    for restaurant in restaurants:
        reviews = Review.query.filter_by(restaurant_id=restaurant.id).all()
        if reviews:
            restaurant.total_reviews = len(reviews)
            restaurant.rating = sum(review.rating for review in reviews) / len(reviews)
        else:
            restaurant.total_reviews = 0
            restaurant.rating = 0.0
    
    db.session.commit()
    print("Reviews seeded successfully!")
