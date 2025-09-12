"""
Route blueprints for the Food Ordering Application
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import check_password_hash
from datetime import datetime, date
import logging
from models import db, User, Restaurant, MenuItem, Order, OrderItem, Cart, UserPreference, Review

logger = logging.getLogger(__name__)

# Main blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page"""
    try:
        # Get featured restaurants
        featured_restaurants = Restaurant.query.filter_by(is_active=True).limit(6).all()
        
        # Get today's special items
        special_items = MenuItem.query.filter_by(is_special=True, is_available=True).limit(4).all()
        
        # Get deal of the day items
        deal_items = MenuItem.query.filter_by(is_deal_of_day=True, is_available=True).limit(4).all()
        
        return render_template('index.html', 
                             featured_restaurants=featured_restaurants,
                             special_items=special_items,
                             deal_items=deal_items)
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        flash('An error occurred while loading the home page.', 'error')
        return render_template('index.html')

# Authentication blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for both customers and restaurant owners"""
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                flash('Please fill in all fields.', 'error')
                return render_template('auth/login.html')
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password) and user.is_active:
                login_user(user)
                flash(f'Welcome back, {user.first_name}!', 'success')
                
                # Redirect based on user role
                if user.is_customer():
                    return redirect(url_for('customer.dashboard'))
                elif user.is_restaurant_owner():
                    return redirect(url_for('restaurant.dashboard'))
            else:
                flash('Invalid username or password.', 'error')
                
        except Exception as e:
            logger.error(f"Error in login: {e}")
            flash('An error occurred during login.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    try:
        logout_user()
    except Exception as e:
        logger.error(f"Error in logout: {e}")
        flash('An error occurred during logout.', 'error')
    
    return redirect(url_for('main.index'))

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Password reset functionality"""
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            
            if not username or not email:
                flash('Please fill in all fields.', 'error')
                return render_template('auth/reset_password.html')
            
            user = User.query.filter_by(username=username, email=email).first()
            
            if user:
                # In a real application, you would send an email with reset link
                flash('Password reset instructions have been sent to your email.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('No user found with the provided credentials.', 'error')
                
        except Exception as e:
            logger.error(f"Error in reset password: {e}")
            flash('An error occurred during password reset.', 'error')
    
    return render_template('auth/reset_password.html')

# Customer blueprint
customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/dashboard')
@login_required
def dashboard():
    """Customer dashboard"""
    if not current_user.is_customer():
        flash('Access denied. Customer access required.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Get recent orders
        recent_orders = Order.query.filter_by(customer_id=current_user.id)\
                                 .order_by(Order.created_at.desc()).limit(5).all()
        
        # Get cart items count
        cart_count = Cart.query.filter_by(customer_id=current_user.id).count()
        
        # Get recommendations
        recommendations = get_customer_recommendations(current_user.id)
        
        return render_template('customer/dashboard.html',
                             recent_orders=recent_orders,
                             cart_count=cart_count,
                             recommendations=recommendations)
    except Exception as e:
        logger.error(f"Error in customer dashboard: {e}")
        flash('An error occurred while loading the dashboard.', 'error')
        return render_template('customer/dashboard.html')

@customer_bp.route('/restaurants')
@login_required
def restaurants():
    """Browse restaurants"""
    if not current_user.is_customer():
        flash('Access denied. Customer access required.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        cuisine_filter = request.args.get('cuisine', '')
        location_filter = request.args.get('location', '')
        
        query = Restaurant.query.filter_by(is_active=True)
        
        if search:
            query = query.filter(Restaurant.name.contains(search))
        
        if cuisine_filter:
            query = query.filter(Restaurant.cuisine_type == cuisine_filter)
        
        if location_filter:
            query = query.filter(Restaurant.location.contains(location_filter))
        
        restaurants = query.paginate(page=page, per_page=12, error_out=False)
        
        # Get unique cuisine types for filter
        cuisine_types = db.session.query(Restaurant.cuisine_type).distinct().all()
        cuisine_types = [c[0] for c in cuisine_types]
        
        return render_template('customer/restaurants.html',
                             restaurants=restaurants,
                             cuisine_types=cuisine_types,
                             search=search,
                             cuisine_filter=cuisine_filter,
                             location_filter=location_filter)
    except Exception as e:
        logger.error(f"Error in restaurants view: {e}")
        flash('An error occurred while loading restaurants.', 'error')
        return render_template('customer/restaurants.html')

@customer_bp.route('/restaurant/<int:restaurant_id>')
@login_required
def restaurant_detail(restaurant_id):
    """Restaurant detail page with menu"""
    if not current_user.is_customer():
        flash('Access denied. Customer access required.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        
        # Get menu items
        category_filter = request.args.get('category', '')
        cuisine_filter = request.args.get('cuisine', '')
        price_filter = request.args.get('price', '')
        dietary_filter = request.args.get('dietary', '')
        
        query = MenuItem.query.filter_by(restaurant_id=restaurant_id, is_available=True)
        
        if category_filter:
            query = query.filter(MenuItem.category == category_filter)
        
        if cuisine_filter:
            query = query.filter(MenuItem.cuisine_type == cuisine_filter)
        
        if price_filter:
            if price_filter == 'low':
                query = query.filter(MenuItem.price <= 10)
            elif price_filter == 'medium':
                query = query.filter(MenuItem.price > 10, MenuItem.price <= 25)
            elif price_filter == 'high':
                query = query.filter(MenuItem.price > 25)
        
        if dietary_filter:
            if dietary_filter == 'vegetarian':
                query = query.filter(MenuItem.is_vegetarian == True)
            elif dietary_filter == 'vegan':
                query = query.filter(MenuItem.is_vegan == True)
            elif dietary_filter == 'gluten_free':
                query = query.filter(MenuItem.is_gluten_free == True)
        
        menu_items = query.all()
        
        # Get unique categories and cuisine types for filters
        categories = db.session.query(MenuItem.category).filter_by(restaurant_id=restaurant_id).distinct().all()
        categories = [c[0] for c in categories]
        
        cuisine_types = db.session.query(MenuItem.cuisine_type).filter_by(restaurant_id=restaurant_id).distinct().all()
        cuisine_types = [c[0] for c in cuisine_types]
        
        # Get reviews
        reviews = Review.query.filter_by(restaurant_id=restaurant_id).order_by(Review.created_at.desc()).limit(5).all()
        
        return render_template('customer/restaurant_detail.html',
                             restaurant=restaurant,
                             menu_items=menu_items,
                             categories=categories,
                             cuisine_types=cuisine_types,
                             reviews=reviews,
                             category_filter=category_filter,
                             cuisine_filter=cuisine_filter,
                             price_filter=price_filter,
                             dietary_filter=dietary_filter)
    except Exception as e:
        logger.error(f"Error in restaurant detail: {e}")
        flash('An error occurred while loading restaurant details.', 'error')
        return redirect(url_for('customer.restaurants'))

@customer_bp.route('/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    """Add item to cart"""
    if not current_user.is_customer():
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        menu_item_id = request.json.get('menu_item_id')
        quantity = request.json.get('quantity', 1)
        
        if not menu_item_id:
            return jsonify({'success': False, 'message': 'Invalid menu item'})
        
        menu_item = MenuItem.query.get_or_404(menu_item_id)
        
        if not menu_item.is_available:
            return jsonify({'success': False, 'message': 'Item is not available'})
        
        # Check if item already in cart
        existing_cart_item = Cart.query.filter_by(
            customer_id=current_user.id,
            menu_item_id=menu_item_id
        ).first()
        
        if existing_cart_item:
            existing_cart_item.quantity += quantity
        else:
            cart_item = Cart(
                customer_id=current_user.id,
                menu_item_id=menu_item_id,
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        
        # Get updated cart count
        cart_count = Cart.query.filter_by(customer_id=current_user.id).count()
        
        return jsonify({
            'success': True,
            'message': 'Item added to cart successfully',
            'cart_count': cart_count
        })
        
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'})

@customer_bp.route('/cart')
@login_required
def cart():
    """Shopping cart page"""
    if not current_user.is_customer():
        flash('Access denied. Customer access required.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        cart_items = Cart.query.filter_by(customer_id=current_user.id).all()
        total_amount = sum(item.quantity * item.menu_item.price for item in cart_items)
        
        return render_template('customer/cart.html',
                             cart_items=cart_items,
                             total_amount=total_amount)
    except Exception as e:
        logger.error(f"Error in cart view: {e}")
        flash('An error occurred while loading cart.', 'error')
        return render_template('customer/cart.html')

@customer_bp.route('/remove-from-cart', methods=['POST'])
@login_required
def remove_from_cart():
    """Remove item from cart"""
    if not current_user.is_customer():
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        cart_item_id = request.json.get('cart_item_id')
        
        if not cart_item_id:
            return jsonify({'success': False, 'message': 'Invalid cart item'})
        
        cart_item = Cart.query.filter_by(
            id=cart_item_id,
            customer_id=current_user.id
        ).first()
        
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
            
            # Get updated cart count and total
            cart_count = Cart.query.filter_by(customer_id=current_user.id).count()
            cart_items = Cart.query.filter_by(customer_id=current_user.id).all()
            total_amount = sum(item.quantity * item.menu_item.price for item in cart_items)
            
            return jsonify({
                'success': True,
                'message': 'Item removed from cart',
                'cart_count': cart_count,
                'total_amount': total_amount
            })
        else:
            return jsonify({'success': False, 'message': 'Item not found in cart'})
            
    except Exception as e:
        logger.error(f"Error removing from cart: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'})

@customer_bp.route('/place-order', methods=['POST'])
@login_required
def place_order():
    """Place order"""
    if not current_user.is_customer():
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        cart_items = Cart.query.filter_by(customer_id=current_user.id).all()
        
        if not cart_items:
            return jsonify({'success': False, 'message': 'Cart is empty'})
        
        # Group items by restaurant
        restaurant_items = {}
        for item in cart_items:
            restaurant_id = item.menu_item.restaurant_id
            if restaurant_id not in restaurant_items:
                restaurant_items[restaurant_id] = []
            restaurant_items[restaurant_id].append(item)
        
        # Create orders for each restaurant
        orders = []
        for restaurant_id, items in restaurant_items.items():
            # Generate order number
            order_number = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{current_user.id}{restaurant_id}"
            
            # Calculate total
            total_amount = sum(item.quantity * item.menu_item.price for item in items)
            
            # Create order
            order = Order(
                order_number=order_number,
                total_amount=total_amount,
                customer_id=current_user.id,
                restaurant_id=restaurant_id
            )
            db.session.add(order)
            db.session.flush()  # Get order ID
            
            # Create order items
            for item in items:
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=item.menu_item_id,
                    quantity=item.quantity,
                    price=item.menu_item.price
                )
                db.session.add(order_item)
                
                # Update menu item order count
                item.menu_item.order_count += item.quantity
            
            orders.append(order)
        
        # Clear cart
        Cart.query.filter_by(customer_id=current_user.id).delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Order placed successfully! Order number: {orders[0].order_number}',
            'order_number': orders[0].order_number
        })
        
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred while placing order'})

@customer_bp.route('/orders')
@login_required
def orders():
    """Order history"""
    if not current_user.is_customer():
        flash('Access denied. Customer access required.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        status_filter = request.args.get('status', '')
        
        query = Order.query.filter_by(customer_id=current_user.id)
        
        if search:
            query = query.filter(Order.order_number.contains(search))
        
        if status_filter:
            query = query.filter(Order.status == status_filter)
        
        orders = query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=10, error_out=False
        )
        
        return render_template('customer/orders.html',
                             orders=orders,
                             search=search,
                             status_filter=status_filter)
    except Exception as e:
        logger.error(f"Error in orders view: {e}")
        flash('An error occurred while loading orders.', 'error')
        return render_template('customer/orders.html')

@customer_bp.route('/profile')
@login_required
def profile():
    """Customer profile"""
    if not current_user.is_customer():
        flash('Access denied. Customer access required.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        preferences = UserPreference.query.filter_by(user_id=current_user.id).all()
        return render_template('customer/profile.html', preferences=preferences)
    except Exception as e:
        logger.error(f"Error in profile view: {e}")
        flash('An error occurred while loading profile.', 'error')
        return render_template('customer/profile.html')

@customer_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Update customer profile"""
    if not current_user.is_customer():
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        first_name = request.json.get('first_name')
        last_name = request.json.get('last_name')
        email = request.json.get('email')
        phone = request.json.get('phone')
        address = request.json.get('address')
        
        if not first_name or not last_name or not email:
            return jsonify({'success': False, 'message': 'Required fields missing'})
        
        # Check if email is already taken by another user
        existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing_user:
            return jsonify({'success': False, 'message': 'Email already taken'})
        
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.email = email
        current_user.phone = phone
        current_user.address = address
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
        
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'})

# Restaurant owner blueprint
restaurant_bp = Blueprint('restaurant', __name__)

@restaurant_bp.route('/dashboard')
@login_required
def dashboard():
    """Restaurant owner dashboard"""
    if not current_user.is_restaurant_owner():
        flash('Access denied. Restaurant owner access required.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Get user's restaurants
        restaurants = Restaurant.query.filter_by(owner_id=current_user.id).all()
        
        # Get recent orders across all restaurants
        restaurant_ids = [r.id for r in restaurants]
        recent_orders = Order.query.filter(Order.restaurant_id.in_(restaurant_ids))\
                                 .order_by(Order.created_at.desc()).limit(10).all()
        
        # Get order statistics
        total_orders = Order.query.filter(Order.restaurant_id.in_(restaurant_ids)).count()
        pending_orders = Order.query.filter(Order.restaurant_id.in_(restaurant_ids),
                                          Order.status == 'pending').count()
        
        return render_template('restaurant/dashboard.html',
                             restaurants=restaurants,
                             recent_orders=recent_orders,
                             total_orders=total_orders,
                             pending_orders=pending_orders)
    except Exception as e:
        logger.error(f"Error in restaurant dashboard: {e}")
        flash('An error occurred while loading the dashboard.', 'error')
        return render_template('restaurant/dashboard.html')

@restaurant_bp.route('/restaurants')
@login_required
def restaurants():
    """Manage restaurants"""
    if not current_user.is_restaurant_owner():
        flash('Access denied. Restaurant owner access required.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        restaurants = Restaurant.query.filter_by(owner_id=current_user.id).all()
        return render_template('restaurant/restaurants.html', restaurants=restaurants)
    except Exception as e:
        logger.error(f"Error in restaurant management: {e}")
        flash('An error occurred while loading restaurants.', 'error')
        return render_template('restaurant/restaurants.html')

@restaurant_bp.route('/add-restaurant', methods=['GET', 'POST'])
@login_required
def add_restaurant():
    """Add new restaurant"""
    if not current_user.is_restaurant_owner():
        flash('Access denied. Restaurant owner access required.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            cuisine_type = request.form.get('cuisine_type')
            location = request.form.get('location')
            phone = request.form.get('phone')
            email = request.form.get('email')
            
            if not all([name, cuisine_type, location]):
                flash('Please fill in all required fields.', 'error')
                return render_template('restaurant/add_restaurant.html')
            
            restaurant = Restaurant(
                name=name,
                description=description,
                cuisine_type=cuisine_type,
                location=location,
                phone=phone,
                email=email,
                owner_id=current_user.id
            )
            
            db.session.add(restaurant)
            db.session.commit()
            
            flash('Restaurant added successfully!', 'success')
            return redirect(url_for('restaurant.restaurants'))
            
        except Exception as e:
            logger.error(f"Error adding restaurant: {e}")
            db.session.rollback()
            flash('An error occurred while adding restaurant.', 'error')
    
    return render_template('restaurant/add_restaurant.html')

@restaurant_bp.route('/restaurant/<int:restaurant_id>/menu')
@login_required
def menu_management(restaurant_id):
    """Manage restaurant menu"""
    if not current_user.is_restaurant_owner():
        flash('Access denied. Restaurant owner access required.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        restaurant = Restaurant.query.filter_by(id=restaurant_id, owner_id=current_user.id).first_or_404()
        menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
        
        return render_template('restaurant/menu_management.html',
                             restaurant=restaurant,
                             menu_items=menu_items)
    except Exception as e:
        logger.error(f"Error in menu management: {e}")
        flash('An error occurred while loading menu.', 'error')
        return redirect(url_for('restaurant.restaurants'))

@restaurant_bp.route('/add-menu-item', methods=['POST'])
@login_required
def add_menu_item():
    """Add menu item"""
    if not current_user.is_restaurant_owner():
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        restaurant_id = request.json.get('restaurant_id')
        name = request.json.get('name')
        description = request.json.get('description')
        price = request.json.get('price')
        category = request.json.get('category')
        cuisine_type = request.json.get('cuisine_type')
        is_vegetarian = request.json.get('is_vegetarian', False)
        is_vegan = request.json.get('is_vegan', False)
        is_gluten_free = request.json.get('is_gluten_free', False)
        is_special = request.json.get('is_special', False)
        is_deal_of_day = request.json.get('is_deal_of_day', False)
        
        if not all([restaurant_id, name, price, category, cuisine_type]):
            return jsonify({'success': False, 'message': 'Required fields missing'})
        
        # Verify restaurant ownership
        restaurant = Restaurant.query.filter_by(id=restaurant_id, owner_id=current_user.id).first()
        if not restaurant:
            return jsonify({'success': False, 'message': 'Restaurant not found'})
        
        menu_item = MenuItem(
            name=name,
            description=description,
            price=float(price),
            category=category,
            cuisine_type=cuisine_type,
            is_vegetarian=is_vegetarian,
            is_vegan=is_vegan,
            is_gluten_free=is_gluten_free,
            is_special=is_special,
            is_deal_of_day=is_deal_of_day,
            restaurant_id=restaurant_id
        )
        
        db.session.add(menu_item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Menu item added successfully'})
        
    except Exception as e:
        logger.error(f"Error adding menu item: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'})

@restaurant_bp.route('/orders')
@login_required
def orders():
    """Manage orders"""
    if not current_user.is_restaurant_owner():
        flash('Access denied. Restaurant owner access required.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Get user's restaurants
        restaurants = Restaurant.query.filter_by(owner_id=current_user.id).all()
        restaurant_ids = [r.id for r in restaurants]
        
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', '')
        
        query = Order.query.filter(Order.restaurant_id.in_(restaurant_ids))
        
        if status_filter:
            query = query.filter(Order.status == status_filter)
        
        orders = query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=10, error_out=False
        )
        
        return render_template('restaurant/orders.html',
                             orders=orders,
                             restaurants=restaurants,
                             status_filter=status_filter)
    except Exception as e:
        logger.error(f"Error in orders management: {e}")
        flash('An error occurred while loading orders.', 'error')
        return render_template('restaurant/orders.html')

@restaurant_bp.route('/update-order-status', methods=['POST'])
@login_required
def update_order_status():
    """Update order status"""
    if not current_user.is_restaurant_owner():
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        order_id = request.json.get('order_id')
        status = request.json.get('status')
        
        if not order_id or not status:
            return jsonify({'success': False, 'message': 'Invalid data'})
        
        # Verify order ownership
        order = Order.query.join(Restaurant).filter(
            Order.id == order_id,
            Restaurant.owner_id == current_user.id
        ).first()
        
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'})
        
        order.status = status
        order.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Order status updated successfully'})
        
    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'})

def get_customer_recommendations(customer_id):
    """Get personalized recommendations for customer"""
    try:
        # Get user preferences
        preferences = UserPreference.query.filter_by(user_id=customer_id).all()
        
        # Get user's order history
        user_orders = Order.query.filter_by(customer_id=customer_id).all()
        
        # Simple recommendation logic based on preferences and order history
        recommendations = []
        
        # Get favorite cuisines
        favorite_cuisines = [p.preference_value for p in preferences 
                           if p.preference_type == 'favorite_cuisine']
        
        if favorite_cuisines:
            # Recommend items from favorite cuisines
            recommended_items = MenuItem.query.filter(
                MenuItem.cuisine_type.in_(favorite_cuisines),
                MenuItem.is_available == True
            ).limit(5).all()
            recommendations.extend(recommended_items)
        
        # Get mostly ordered items
        mostly_ordered = MenuItem.query.filter(
            MenuItem.order_count > 10,
            MenuItem.is_available == True
        ).limit(3).all()
        recommendations.extend(mostly_ordered)
        
        # Remove duplicates
        seen = set()
        unique_recommendations = []
        for item in recommendations:
            if item.id not in seen:
                seen.add(item.id)
                unique_recommendations.append(item)
        
        return unique_recommendations[:8]  # Return top 8 recommendations
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return []
