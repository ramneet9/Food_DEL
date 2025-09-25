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


def sync_all_data():
    """Idempotently sync seed data into the current database (upsert)."""
    try:
        upsert_users()
        upsert_restaurants()
        upsert_menu_items()
        upsert_user_preferences()
        upsert_reviews()

        # Recompute restaurant ratings and total reviews
        restaurants = Restaurant.query.all()
        for restaurant in restaurants:
            reviews = Review.query.filter_by(restaurant_id=restaurant.id).all()
            if reviews:
                restaurant.total_reviews = len(reviews)
                restaurant.rating = sum(r.rating for r in reviews) / len(reviews)
            else:
                restaurant.total_reviews = 0
                restaurant.rating = 0.0
        db.session.commit()
        print("Database synced successfully!")
    except Exception as e:
        print(f"Error syncing database: {e}")
        db.session.rollback()

def seed_users():
    """Seed users data"""
    users_data = [
        # Customers
        {
            'username': 'ramneet',
            'email': 'ram@example.com',
            'password': 'ramneet',
            'role': 'customer',
            'first_name': 'Ramneet',
            'last_name': 'Singh',
            'phone': '+1234567890',
            'address': '123 Apt, West Delhi'
        },
        {
            'username': 'batman',
            'email': 'batman@example.com',
            'password': 'batman',
            'role': 'customer',
            'first_name': 'BAT',
            'last_name': 'MAN',
            'phone': '+1234567891',
            'address': '456, South Delhi'
        },
        
        # Restaurant Owners
        {
            'username': 'chef_mario',
            'email': 'mario@italianbistro.com',
            'password': 'mario',
            'role': 'restaurant_owner',
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'phone': '+1234567893',
            'address': '321 Restaurant Row, City, State'
        },
        {
            'username': 'chef_raj',
            'email': 'raj@spicepalace.com',
            'password': 'raj',
            'role': 'restaurant_owner',
            'first_name': 'Raj',
            'last_name': 'Patel',
            'phone': '+1234567894',
            'address': '654 Curry Lane, City, State'
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


def upsert_users():
    """Upsert users based on username as natural key."""
    users_data = [
        {
            'username': 'ramneet', 'email': 'ram@example.com', 'password': 'ramneet',
            'role': 'customer', 'first_name': 'Ramneet', 'last_name': 'Singh',
            'phone': '+1234567890', 'address': '123 Apt, West Delhi'
        },
        {
            'username': 'batman', 'email': 'batman@example.com', 'password': 'batman',
            'role': 'customer', 'first_name': 'BAT', 'last_name': 'MAN',
            'phone': '+1234567891', 'address': '456, South Delhi'
        },
        {
            'username': 'chef_mario', 'email': 'mario@italianbistro.com', 'password': 'mario',
            'role': 'restaurant_owner', 'first_name': 'Mario', 'last_name': 'Rossi',
            'phone': '+1234567893', 'address': '321 Restaurant Row, City, State'
        },
        {
            'username': 'chef_raj', 'email': 'raj@spicepalace.com', 'password': 'raj',
            'role': 'restaurant_owner', 'first_name': 'Raj', 'last_name': 'Patel',
            'phone': '+1234567894', 'address': '654 Curry Lane, City, State'
        }
    ]
    for data in users_data:
        user = User.query.filter_by(username=data['username']).first()
        if not user:
            user = User(username=data['username'])
            db.session.add(user)
        # Update fields
        user.email = data['email']
        user.role = data['role']
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.phone = data['phone']
        user.address = data['address']
        # Always ensure password matches the seed value
        user.set_password(data['password'])
    db.session.commit()

def seed_restaurants():
    """Seed restaurants data"""
    # Get restaurant owners
    mario = User.query.filter_by(username='chef_mario').first()
    raj = User.query.filter_by(username='chef_raj').first()
    # li = User.query.filter_by(username='chef_li').first()
    # sarah = User.query.filter_by(username='chef_sarah').first()
    # antonio = User.query.filter_by(username='chef_antonio').first()
    # emily = User.query.filter_by(username='chef_emily').first()
    
    restaurants_data = [
        {
            'name': 'Mario\'s Italian Bistro',
            'description': 'Authentic Italian cuisine with fresh ingredients and traditional recipes passed down through generations.',
            'cuisine_type': 'Italian',
            'location': 'South Delhi',
            'phone': '+1234567001',
            'email': 'info@italianbistro.com',
            'owner_id': mario.id
        },
        {
            'name': 'Spice Palace',
            'description': 'Exotic Indian flavors with aromatic spices and traditional cooking methods.',
            'cuisine_type': 'Indian',
            'location': 'West Delhi',
            'phone': '+1234567002',
            'email': 'info@spicepalace.com',
            'owner_id': raj.id
        },
        {
            'name': 'Dragon Wok',
            'description': 'Modern Chinese cuisine with fresh ingredients and authentic flavors.',
            'cuisine_type': 'Chinese',
            'location': 'East Delhi',
            'phone': '+1234567003',
            'email': 'info@dragonwok.com',
            'owner_id': raj.id
        },
        {
            'name': 'Green Leaf Cafe',
            'description': 'Healthy vegetarian and vegan options with organic ingredients.',
            'cuisine_type': 'Vegetarian',
            'location': 'South Delhi',
            'phone': '+1234567004',
            'email': 'info@greenleaf.com',
            'owner_id': mario.id
        },
        {
            'name': 'Burger Junction',
            'description': 'Gourmet burgers with premium ingredients and creative combinations.',
            'cuisine_type': 'American',
            'location': 'North Delhi',
            'phone': '+1234567005',
            'email': 'info@burgerjunction.com',
            'owner_id': mario.id
        },
        {
            'name': 'Sushi Zen',
            'description': 'Fresh sushi and Japanese cuisine with traditional techniques.',
            'cuisine_type': 'Japanese',
            'location': 'Central Delhi',
            'phone': '+1234567006',
            'email': 'info@sushizen.com',
            'owner_id': raj.id
        },
        {
            'name': 'Taco Fiesta',
            'description': 'Authentic Mexican street food with fresh ingredients and bold flavors.',
            'cuisine_type': 'Mexican',
            'location': 'West Delhi',
            'phone': '+1234567007',
            'email': 'info@tacofiesta.com',
            'owner_id': mario.id
        },
        {
            'name': 'Bakery Corner',
            'description': 'Fresh baked goods, pastries, and artisanal breads made daily.',
            'cuisine_type': 'Bakery',
            'location': 'Central Delhi',
            'phone': '+1234567008',
            'email': 'info@bakerycorner.com',
            'owner_id': raj.id
        }
    ]
    
    for restaurant_data in restaurants_data:
        restaurant = Restaurant(**restaurant_data)
        db.session.add(restaurant)
    
    db.session.commit()
    print("Restaurants seeded successfully!")


def upsert_restaurants():
    """Upsert restaurants based on name as natural key."""
    mario = User.query.filter_by(username='chef_mario').first()
    raj = User.query.filter_by(username='chef_raj').first()
    restaurants_data = [
        {
            'name': "Mario's Italian Bistro",
            'description': 'Authentic Italian cuisine with fresh ingredients and traditional recipes passed down through generations.',
            'cuisine_type': 'Italian', 'location': 'South Delhi', 'phone': '+1234567001',
            'email': 'info@italianbistro.com', 'owner_id': mario.id if mario else None
        },
        {
            'name': 'Spice Palace',
            'description': 'Exotic Indian flavors with aromatic spices and traditional cooking methods.',
            'cuisine_type': 'Indian', 'location': 'West Delhi', 'phone': '+1234567002',
            'email': 'info@spicepalace.com', 'owner_id': raj.id if raj else None
        },
        {
            'name': 'Dragon Wok',
            'description': 'Modern Chinese cuisine with fresh ingredients and authentic flavors.',
            'cuisine_type': 'Chinese', 'location': 'East Delhi', 'phone': '+1234567003',
            'email': 'info@dragonwok.com', 'owner_id': raj.id if raj else None
        },
        {
            'name': 'Green Leaf Cafe',
            'description': 'Healthy vegetarian and vegan options with organic ingredients.',
            'cuisine_type': 'Vegetarian', 'location': 'South Delhi', 'phone': '+1234567004',
            'email': 'info@greenleaf.com', 'owner_id': mario.id if mario else None
        },
        {
            'name': 'Burger Junction',
            'description': 'Gourmet burgers with premium ingredients and creative combinations.',
            'cuisine_type': 'American', 'location': 'North Delhi', 'phone': '+1234567005',
            'email': 'info@burgerjunction.com', 'owner_id': mario.id if mario else None
        },
        {
            'name': 'Sushi Zen',
            'description': 'Fresh sushi and Japanese cuisine with traditional techniques.',
            'cuisine_type': 'Japanese', 'location': 'Central Delhi', 'phone': '+1234567006',
            'email': 'info@sushizen.com', 'owner_id': raj.id if raj else None
        },
        {
            'name': 'Taco Fiesta',
            'description': 'Authentic Mexican street food with fresh ingredients and bold flavors.',
            'cuisine_type': 'Mexican', 'location': 'West Delhi', 'phone': '+1234567007',
            'email': 'info@tacofiesta.com', 'owner_id': mario.id if mario else None
        },
        {
            'name': 'Bakery Corner',
            'description': 'Fresh baked goods, pastries, and artisanal breads made daily.',
            'cuisine_type': 'Bakery', 'location': 'Central Delhi', 'phone': '+1234567008',
            'email': 'info@bakerycorner.com', 'owner_id': raj.id if raj else None
        }
    ]
    for data in restaurants_data:
        if not data['owner_id']:
            continue
        restaurant = Restaurant.query.filter_by(name=data['name']).first()
        if not restaurant:
            restaurant = Restaurant(name=data['name'])
            db.session.add(restaurant)
        restaurant.description = data['description']
        restaurant.cuisine_type = data['cuisine_type']
        restaurant.location = data['location']
        restaurant.phone = data['phone']
        restaurant.email = data['email']
        restaurant.owner_id = data['owner_id']
    db.session.commit()

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
            'price': 169,
            'category': 'Pizza',
            'cuisine_type': 'Italian',
            'is_vegetarian': True,
            'restaurant_id': italian_bistro.id,
            'is_special': True
        },
        {
            'name': 'Spaghetti Carbonara',
            'description': 'Creamy pasta with eggs, cheese, and pancetta',
            'price': 189,
            'category': 'Pasta',
            'cuisine_type': 'Italian',
            'is_vegetarian': False,
            'restaurant_id': italian_bistro.id
        },
        {
            'name': 'Chicken Parmigiana',
            'description': 'Breaded chicken breast with marinara sauce and mozzarella',
            'price': 229,
            'category': 'Main Course',
            'cuisine_type': 'Italian',
            'is_vegetarian': False,
            'restaurant_id': italian_bistro.id
        },
        {
            'name': 'Tiramisu',
            'description': 'Classic Italian dessert with coffee and mascarpone',
            'price': 899,
            'category': 'Dessert',
            'cuisine_type': 'Italian',
            'is_vegetarian': True,
            'restaurant_id': italian_bistro.id
        },
        
        # Spice Palace
        {
            'name': 'Chicken Tikka Masala',
            'description': 'Tender chicken in creamy tomato sauce with aromatic spices',
            'price': 199,
            'category': 'Curry',
            'cuisine_type': 'Indian',
            'is_vegetarian': False,
            'restaurant_id': spice_palace.id,
            'is_deal_of_day': True
        },
        {
            'name': 'Vegetable Biryani',
            'description': 'Fragrant basmati rice with mixed vegetables and spices',
            'price': 199,
            'category': 'Rice',
            'cuisine_type': 'Indian',
            'is_vegetarian': True,
            'restaurant_id': spice_palace.id
        },
        {
            'name': 'Butter Chicken',
            'description': 'Creamy tomato-based curry with tender chicken pieces',
            'price': 299,
            'category': 'Curry',
            'cuisine_type': 'Indian',
            'is_vegetarian': False,
            'restaurant_id': spice_palace.id
        },
        {
            'name': 'Naan Bread',
            'description': 'Fresh baked flatbread',
            'price': 49,
            'category': 'Bread',
            'cuisine_type': 'Indian',
            'is_vegetarian': True,
            'restaurant_id': spice_palace.id
        },
        
        # Dragon Wok
        {
            'name': 'Kung Pao Chicken',
            'description': 'Spicy stir-fried chicken with peanuts and vegetables',
            'price': 179,
            'category': 'Stir Fry',
            'cuisine_type': 'Chinese',
            'is_vegetarian': False,
            'restaurant_id': dragon_wok.id
        },
        {
            'name': 'Sweet and Sour Pork',
            'description': 'Crispy pork with bell peppers in tangy sauce',
            'price': 199,
            'category': 'Main Course',
            'cuisine_type': 'Chinese',
            'is_vegetarian': False,
            'restaurant_id': dragon_wok.id
        },
        {
            'name': 'Vegetable Lo Mein',
            'description': 'Stir-fried noodles with mixed vegetables',
            'price': 199,
            'category': 'Noodles',
            'cuisine_type': 'Chinese',
            'is_vegetarian': True,
            'restaurant_id': dragon_wok.id
        },
        {
            'name': 'Spring Rolls',
            'description': 'Crispy vegetable spring rolls with sweet chili sauce',
            'price': 79,
            'category': 'Appetizer',
            'cuisine_type': 'Chinese',
            'is_vegetarian': True,
            'restaurant_id': dragon_wok.id
        },
        
        # Green Leaf Cafe
        {
            'name': 'Quinoa Buddha Bowl',
            'description': 'Nutritious bowl with quinoa, roasted vegetables, and tahini dressing',
            'price': 159,
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
            'price': 139,
            'category': 'Burger',
            'cuisine_type': 'Vegetarian',
            'is_vegetarian': True,
            'is_vegan': True,
            'restaurant_id': green_leaf.id
        },
        {
            'name': 'Green Smoothie',
            'description': 'Blend of spinach, banana, mango, and coconut water',
            'price': 89,
            'category': 'Beverage',
            'cuisine_type': 'Vegetarian',
            'is_vegetarian': True,
            'is_vegan': True,
            'restaurant_id': green_leaf.id
        },
        {
            'name': 'Avocado Toast',
            'description': 'Smashed avocado on sourdough with cherry tomatoes',
            'price': 119,
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
            'price': 149,
            'category': 'Burger',
            'cuisine_type': 'American',
            'is_vegetarian': False,
            'restaurant_id': burger_junction.id
        },
        {
            'name': 'BBQ Bacon Burger',
            'description': 'Beef patty with bacon, BBQ sauce, and onion rings',
            'price': 179,
            'category': 'Burger',
            'cuisine_type': 'American',
            'is_vegetarian': False,
            'restaurant_id': burger_junction.id
        },
        {
            'name': 'Chicken Wings',
            'description': 'Crispy wings with choice of buffalo, BBQ, or honey mustard',
            'price': 129,
            'category': 'Appetizer',
            'cuisine_type': 'American',
            'is_vegetarian': False,
            'restaurant_id': burger_junction.id
        },
        {
            'name': 'French Fries',
            'description': 'Golden crispy fries with sea salt',
            'price': 69,
            'category': 'Side',
            'cuisine_type': 'American',
            'is_vegetarian': True,
            'restaurant_id': burger_junction.id
        },
        
        # Sushi Zen
        {
            'name': 'California Roll',
            'description': 'Crab, avocado, and cucumber roll',
            'price': 129,
            'category': 'Sushi Roll',
            'cuisine_type': 'Japanese',
            'is_vegetarian': False,
            'restaurant_id': sushi_zen.id
        },
        {
            'name': 'Salmon Nigiri',
            'description': 'Fresh salmon over seasoned rice',
            'price': 159,
            'category': 'Nigiri',
            'cuisine_type': 'Japanese',
            'is_vegetarian': False,
            'restaurant_id': sushi_zen.id
        },
        {
            'name': 'Vegetable Tempura',
            'description': 'Lightly battered and fried seasonal vegetables',
            'price': 119,
            'category': 'Appetizer',
            'cuisine_type': 'Japanese',
            'is_vegetarian': True,
            'restaurant_id': sushi_zen.id
        },
        {
            'name': 'Miso Soup',
            'description': 'Traditional Japanese soup with tofu and seaweed',
            'price': 99,
            'category': 'Soup',
            'cuisine_type': 'Japanese',
            'is_vegetarian': True,
            'restaurant_id': sushi_zen.id
        },
        
        # Taco Fiesta
        {
            'name': 'Carnitas Tacos',
            'description': 'Slow-cooked pork with onions, cilantro, and lime',
            'price': 199,
            'category': 'Tacos',
            'cuisine_type': 'Mexican',
            'is_vegetarian': False,
            'restaurant_id': taco_fiesta.id
        },
        {
            'name': 'Veggie Quesadilla',
            'description': 'Grilled tortilla with cheese, peppers, and onions',
            'price': 109,
            'category': 'Quesadilla',
            'cuisine_type': 'Mexican',
            'is_vegetarian': True,
            'restaurant_id': taco_fiesta.id
        },
        {
            'name': 'Churros',
            'description': 'Crispy fried dough with cinnamon sugar',
            'price': 99,
            'category': 'Dessert',
            'cuisine_type': 'Mexican',
            'is_vegetarian': True,
            'restaurant_id': taco_fiesta.id
        },
        
        # Bakery Corner
        {
            'name': 'Croissant',
            'description': 'Buttery, flaky French pastry',
            'price': 39,
            'category': 'Pastry',
            'cuisine_type': 'Bakery',
            'is_vegetarian': True,
            'restaurant_id': bakery_corner.id
        },
        {
            'name': 'Chocolate Chip Cookies',
            'description': 'Fresh baked cookies with premium chocolate chips',
            'price': 29,
            'category': 'Cookies',
            'cuisine_type': 'Bakery',
            'is_vegetarian': True,
            'restaurant_id': bakery_corner.id
        },
        {
            'name': 'Artisan Bread',
            'description': 'Fresh baked sourdough bread',
            'price': 59,
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


def upsert_menu_items():
    """Upsert menu items based on (restaurant_id, name)."""
    italian_bistro = Restaurant.query.filter_by(name="Mario's Italian Bistro").first()
    spice_palace = Restaurant.query.filter_by(name='Spice Palace').first()
    dragon_wok = Restaurant.query.filter_by(name='Dragon Wok').first()
    green_leaf = Restaurant.query.filter_by(name='Green Leaf Cafe').first()
    burger_junction = Restaurant.query.filter_by(name='Burger Junction').first()
    sushi_zen = Restaurant.query.filter_by(name='Sushi Zen').first()
    taco_fiesta = Restaurant.query.filter_by(name='Taco Fiesta').first()
    bakery_corner = Restaurant.query.filter_by(name='Bakery Corner').first()

    menu_items_data = [
        {'name': 'Margherita Pizza', 'description': 'Classic pizza with tomato sauce, mozzarella, and fresh basil', 'price': 169, 'category': 'Pizza', 'cuisine_type': 'Italian', 'is_vegetarian': True, 'restaurant': italian_bistro, 'is_special': True},
        {'name': 'Spaghetti Carbonara', 'description': 'Creamy pasta with eggs, cheese, and pancetta', 'price': 189, 'category': 'Pasta', 'cuisine_type': 'Italian', 'is_vegetarian': False, 'restaurant': italian_bistro},
        {'name': 'Chicken Parmigiana', 'description': 'Breaded chicken breast with marinara sauce and mozzarella', 'price': 229, 'category': 'Main Course', 'cuisine_type': 'Italian', 'is_vegetarian': False, 'restaurant': italian_bistro},
        {'name': 'Tiramisu', 'description': 'Classic Italian dessert with coffee and mascarpone', 'price': 899, 'category': 'Dessert', 'cuisine_type': 'Italian', 'is_vegetarian': True, 'restaurant': italian_bistro},

        {'name': 'Chicken Tikka Masala', 'description': 'Tender chicken in creamy tomato sauce with aromatic spices', 'price': 199, 'category': 'Curry', 'cuisine_type': 'Indian', 'is_vegetarian': False, 'restaurant': spice_palace, 'is_deal_of_day': True},
        {'name': 'Vegetable Biryani', 'description': 'Fragrant basmati rice with mixed vegetables and spices', 'price': 199, 'category': 'Rice', 'cuisine_type': 'Indian', 'is_vegetarian': True, 'restaurant': spice_palace},
        {'name': 'Butter Chicken', 'description': 'Creamy tomato-based curry with tender chicken pieces', 'price': 299, 'category': 'Curry', 'cuisine_type': 'Indian', 'is_vegetarian': False, 'restaurant': spice_palace},
        {'name': 'Naan Bread', 'description': 'Fresh baked flatbread', 'price': 49, 'category': 'Bread', 'cuisine_type': 'Indian', 'is_vegetarian': True, 'restaurant': spice_palace},

        {'name': 'Kung Pao Chicken', 'description': 'Spicy stir-fried chicken with peanuts and vegetables', 'price': 179, 'category': 'Stir Fry', 'cuisine_type': 'Chinese', 'is_vegetarian': False, 'restaurant': dragon_wok},
        {'name': 'Sweet and Sour Pork', 'description': 'Crispy pork with bell peppers in tangy sauce', 'price': 199, 'category': 'Main Course', 'cuisine_type': 'Chinese', 'is_vegetarian': False, 'restaurant': dragon_wok},
        {'name': 'Vegetable Lo Mein', 'description': 'Stir-fried noodles with mixed vegetables', 'price': 199, 'category': 'Noodles', 'cuisine_type': 'Chinese', 'is_vegetarian': True, 'restaurant': dragon_wok},
        {'name': 'Spring Rolls', 'description': 'Crispy vegetable spring rolls with sweet chili sauce', 'price': 79, 'category': 'Appetizer', 'cuisine_type': 'Chinese', 'is_vegetarian': True, 'restaurant': dragon_wok},

        {'name': 'Quinoa Buddha Bowl', 'description': 'Nutritious bowl with quinoa, roasted vegetables, and tahini dressing', 'price': 159, 'category': 'Bowl', 'cuisine_type': 'Vegetarian', 'is_vegetarian': True, 'is_vegan': True, 'is_gluten_free': True, 'restaurant': green_leaf},
        {'name': 'Veggie Burger', 'description': 'Plant-based patty with lettuce, tomato, and vegan mayo', 'price': 139, 'category': 'Burger', 'cuisine_type': 'Vegetarian', 'is_vegetarian': True, 'is_vegan': True, 'restaurant': green_leaf},
        {'name': 'Green Smoothie', 'description': 'Blend of spinach, banana, mango, and coconut water', 'price': 89, 'category': 'Beverage', 'cuisine_type': 'Vegetarian', 'is_vegetarian': True, 'is_vegan': True, 'restaurant': green_leaf},
        {'name': 'Avocado Toast', 'description': 'Smashed avocado on sourdough with cherry tomatoes', 'price': 119, 'category': 'Breakfast', 'cuisine_type': 'Vegetarian', 'is_vegetarian': True, 'is_vegan': True, 'restaurant': green_leaf},

        {'name': 'Classic Cheeseburger', 'description': 'Beef patty with cheese, lettuce, tomato, and special sauce', 'price': 149, 'category': 'Burger', 'cuisine_type': 'American', 'is_vegetarian': False, 'restaurant': burger_junction},
        {'name': 'BBQ Bacon Burger', 'description': 'Beef patty with bacon, BBQ sauce, and onion rings', 'price': 179, 'category': 'Burger', 'cuisine_type': 'American', 'is_vegetarian': False, 'restaurant': burger_junction},
        {'name': 'Chicken Wings', 'description': 'Crispy wings with choice of buffalo, BBQ, or honey mustard', 'price': 129, 'category': 'Appetizer', 'cuisine_type': 'American', 'is_vegetarian': False, 'restaurant': burger_junction},
        {'name': 'French Fries', 'description': 'Golden crispy fries with sea salt', 'price': 69, 'category': 'Side', 'cuisine_type': 'American', 'is_vegetarian': True, 'restaurant': burger_junction},

        {'name': 'California Roll', 'description': 'Crab, avocado, and cucumber roll', 'price': 129, 'category': 'Sushi Roll', 'cuisine_type': 'Japanese', 'is_vegetarian': False, 'restaurant': sushi_zen},
        {'name': 'Salmon Nigiri', 'description': 'Fresh salmon over seasoned rice', 'price': 159, 'category': 'Nigiri', 'cuisine_type': 'Japanese', 'is_vegetarian': False, 'restaurant': sushi_zen},
        {'name': 'Vegetable Tempura', 'description': 'Lightly battered and fried seasonal vegetables', 'price': 119, 'category': 'Appetizer', 'cuisine_type': 'Japanese', 'is_vegetarian': True, 'restaurant': sushi_zen},
        {'name': 'Miso Soup', 'description': 'Traditional Japanese soup with tofu and seaweed', 'price': 99, 'category': 'Soup', 'cuisine_type': 'Japanese', 'is_vegetarian': True, 'restaurant': sushi_zen},

        {'name': 'Carnitas Tacos', 'description': 'Slow-cooked pork with onions, cilantro, and lime', 'price': 199, 'category': 'Tacos', 'cuisine_type': 'Mexican', 'is_vegetarian': False, 'restaurant': taco_fiesta},
        {'name': 'Veggie Quesadilla', 'description': 'Grilled tortilla with cheese, peppers, and onions', 'price': 109, 'category': 'Quesadilla', 'cuisine_type': 'Mexican', 'is_vegetarian': True, 'restaurant': taco_fiesta},
        {'name': 'Churros', 'description': 'Crispy fried dough with cinnamon sugar', 'price': 99, 'category': 'Dessert', 'cuisine_type': 'Mexican', 'is_vegetarian': True, 'restaurant': taco_fiesta},

        {'name': 'Croissant', 'description': 'Buttery, flaky French pastry', 'price': 39, 'category': 'Pastry', 'cuisine_type': 'Bakery', 'is_vegetarian': True, 'restaurant': bakery_corner},
        {'name': 'Chocolate Chip Cookies', 'description': 'Fresh baked cookies with premium chocolate chips', 'price': 29, 'category': 'Cookies', 'cuisine_type': 'Bakery', 'is_vegetarian': True, 'restaurant': bakery_corner},
        {'name': 'Artisan Bread', 'description': 'Fresh baked sourdough bread', 'price': 59, 'category': 'Bread', 'cuisine_type': 'Bakery', 'is_vegetarian': True, 'restaurant': bakery_corner},
    ]

    for data in menu_items_data:
        rest = data.pop('restaurant', None)
        if not rest:
            continue
        existing = MenuItem.query.filter_by(restaurant_id=rest.id, name=data['name']).first()
        if not existing:
            existing = MenuItem(restaurant_id=rest.id, name=data['name'])
            db.session.add(existing)
        # Update fields
        for key, value in data.items():
            setattr(existing, key, value)
        existing.restaurant_id = rest.id
    db.session.commit()

def seed_user_preferences():
    """Seed user preferences data"""
    # Get existing seeded customers
    ramneet = User.query.filter_by(username='ramneet').first()
    batman = User.query.filter_by(username='batman').first()
    
    preferences_data = [
        # Preferences for existing users
        {'user_id': ramneet.id, 'preference_type': 'favorite_cuisine', 'preference_value': 'Italian'},
        {'user_id': ramneet.id, 'preference_type': 'favorite_cuisine', 'preference_value': 'American'},
        {'user_id': ramneet.id, 'preference_type': 'dietary_restriction', 'preference_value': 'no_spicy'},
        {'user_id': batman.id, 'preference_type': 'favorite_cuisine', 'preference_value': 'Indian'},
        {'user_id': batman.id, 'preference_type': 'favorite_cuisine', 'preference_value': 'Vegetarian'},
        {'user_id': batman.id, 'preference_type': 'dietary_restriction', 'preference_value': 'vegetarian'}
    ]
    
    for pref_data in preferences_data:
        preference = UserPreference(**pref_data)
        db.session.add(preference)
    
    db.session.commit()
    print("User preferences seeded successfully!")


def upsert_user_preferences():
    """Ensure preferences exist; avoid duplicates."""
    ramneet = User.query.filter_by(username='ramneet').first()
    batman = User.query.filter_by(username='batman').first()
    preferences_data = []
    if ramneet:
        preferences_data += [
            {'user_id': ramneet.id, 'preference_type': 'favorite_cuisine', 'preference_value': 'Italian'},
            {'user_id': ramneet.id, 'preference_type': 'favorite_cuisine', 'preference_value': 'American'},
            {'user_id': ramneet.id, 'preference_type': 'dietary_restriction', 'preference_value': 'no_spicy'},
        ]
    if batman:
        preferences_data += [
            {'user_id': batman.id, 'preference_type': 'favorite_cuisine', 'preference_value': 'Indian'},
            {'user_id': batman.id, 'preference_type': 'favorite_cuisine', 'preference_value': 'Vegetarian'},
            {'user_id': batman.id, 'preference_type': 'dietary_restriction', 'preference_value': 'vegetarian'},
        ]
    for pref in preferences_data:
        exists = UserPreference.query.filter_by(
            user_id=pref['user_id'],
            preference_type=pref['preference_type'],
            preference_value=pref['preference_value']
        ).first()
        if not exists:
            db.session.add(UserPreference(**pref))
    db.session.commit()

def seed_reviews():
    """Seed reviews data"""
    # Get users and restaurants
    ramneet = User.query.filter_by(username='ramneet').first()
    batman = User.query.filter_by(username='batman').first()
    
    italian_bistro = Restaurant.query.filter_by(name='Mario\'s Italian Bistro').first()
    spice_palace = Restaurant.query.filter_by(name='Spice Palace').first()
    dragon_wok = Restaurant.query.filter_by(name='Dragon Wok').first()
    
    reviews_data = [
        {
            'rating': 5,
            'comment': 'Amazing pizza! The Margherita was perfect with fresh basil.',
            'user_id': ramneet.id,
            'restaurant_id': italian_bistro.id
        },
        {
            'rating': 4,
            'comment': 'Great Italian food, but a bit pricey.',
            'user_id': batman.id,
            'restaurant_id': italian_bistro.id
        },
        {
            'rating': 5,
            'comment': 'Best Indian food in town! The Chicken Tikka Masala was incredible.',
            'user_id': batman.id,
            'restaurant_id': spice_palace.id
        },
        {
            'rating': 4,
            'comment': 'Good Chinese food, quick service.',
            'user_id': batman.id,
            'restaurant_id': dragon_wok.id
        },
        {
            'rating': 3,
            'comment': 'Decent food but could be better.',
            'user_id': ramneet.id,
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


def upsert_reviews():
    """Insert reviews if not already present; then ratings are recalculated by sync."""
    ramneet = User.query.filter_by(username='ramneet').first()
    batman = User.query.filter_by(username='batman').first()
    italian_bistro = Restaurant.query.filter_by(name="Mario's Italian Bistro").first()
    spice_palace = Restaurant.query.filter_by(name='Spice Palace').first()
    dragon_wok = Restaurant.query.filter_by(name='Dragon Wok').first()
    reviews_data = []
    if ramneet and italian_bistro:
        reviews_data.append({'rating': 5, 'comment': 'Amazing pizza! The Margherita was perfect with fresh basil.', 'user_id': ramneet.id, 'restaurant_id': italian_bistro.id})
        reviews_data.append({'rating': 3, 'comment': 'Decent food but could be better.', 'user_id': ramneet.id, 'restaurant_id': dragon_wok.id if dragon_wok else None})
    if batman and italian_bistro:
        reviews_data.append({'rating': 4, 'comment': 'Great Italian food, but a bit pricey.', 'user_id': batman.id, 'restaurant_id': italian_bistro.id})
    if batman and spice_palace:
        reviews_data.append({'rating': 5, 'comment': 'Best Indian food in town! The Chicken Tikka Masala was incredible.', 'user_id': batman.id, 'restaurant_id': spice_palace.id})

    for rd in reviews_data:
        if not rd.get('restaurant_id'):
            continue
        exists = Review.query.filter_by(
            user_id=rd['user_id'], restaurant_id=rd['restaurant_id'], comment=rd['comment']
        ).first()
        if not exists:
            db.session.add(Review(**rd))
    db.session.commit()
