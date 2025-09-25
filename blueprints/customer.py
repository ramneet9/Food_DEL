"""Customer-facing routes blueprint."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Tuple, Dict

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    session,
)
from flask_login import login_required, current_user

from models import db, User, Restaurant, MenuItem, Order, OrderItem, Cart, UserPreference, Review

logger = logging.getLogger(__name__)

customer_bp = Blueprint('customer', __name__)


@customer_bp.route('/dashboard')
@login_required
def dashboard():
    """Customer dashboard."""
    if not current_user.is_customer():
        flash('Access denied. Customer access required.', 'error')
        return redirect(url_for('main.index'))
    try:
        recent_orders = (
            Order.query.filter_by(customer_id=current_user.id)
            .order_by(Order.created_at.desc())
            .limit(5)
            .all()
        )
        cart_count = Cart.query.filter_by(customer_id=current_user.id).count()
        recommendations = get_customer_recommendations(current_user.id)
        return render_template(
            'customer/dashboard.html',
            recent_orders=recent_orders,
            cart_count=cart_count,
            recommendations=recommendations,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Error in customer dashboard: %s", exc)
        flash('An error occurred while loading the dashboard.', 'error')
        return render_template('customer/dashboard.html')


@customer_bp.route('/restaurants')
@login_required
def restaurants():
    """Browse restaurants."""
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
        restaurants_paged = query.paginate(page=page, per_page=12, error_out=False)
        cuisine_types = [c[0] for c in db.session.query(Restaurant.cuisine_type).distinct().all()]
        return render_template(
            'customer/restaurants.html',
            restaurants=restaurants_paged,
            cuisine_types=cuisine_types,
            search=search,
            cuisine_filter=cuisine_filter,
            location_filter=location_filter,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Error in restaurants view: %s", exc)
        flash('An error occurred while loading restaurants.', 'error')
        return render_template('customer/restaurants.html')


@customer_bp.route('/restaurant/<int:restaurant_id>')
@login_required
def restaurant_detail(restaurant_id: int):
    """Restaurant detail page with menu."""
    if not current_user.is_customer():
        flash('Access denied. Customer access required.', 'error')
        return redirect(url_for('main.index'))
    try:
        restaurant = Restaurant.query.get_or_404(restaurant_id)
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
                query = query.filter(MenuItem.price < 500)
            elif price_filter == 'medium':
                query = query.filter(MenuItem.price >= 500, MenuItem.price <= 1000)
            elif price_filter == 'high':
                query = query.filter(MenuItem.price > 1000)
        if dietary_filter:
            if dietary_filter == 'vegetarian':
                query = query.filter(MenuItem.is_vegetarian.is_(True))
            elif dietary_filter == 'vegan':
                query = query.filter(MenuItem.is_vegan.is_(True))
            elif dietary_filter == 'gluten_free':
                query = query.filter(MenuItem.is_gluten_free.is_(True))
        menu_items = query.order_by(
            MenuItem.is_deal_of_day.desc(),
            MenuItem.is_special.desc(),
            MenuItem.order_count.desc(),
            MenuItem.name.asc(),
        ).all()
        categories = [c[0] for c in db.session.query(MenuItem.category).filter_by(restaurant_id=restaurant_id).distinct().all()]
        cuisine_types = [c[0] for c in db.session.query(MenuItem.cuisine_type).filter_by(restaurant_id=restaurant_id).distinct().all()]
        reviews = (
            Review.query.filter_by(restaurant_id=restaurant_id)
            .order_by(Review.created_at.desc())
            .limit(5)
            .all()
        )
        can_review = False
        if current_user.is_authenticated and current_user.is_customer():
            has_order = Order.query.filter_by(
                customer_id=current_user.id, restaurant_id=restaurant_id, status='delivered'
            ).first()
            can_review = has_order is not None
        return render_template(
            'customer/restaurant_detail.html',
            restaurant=restaurant,
            menu_items=menu_items,
            categories=categories,
            cuisine_types=cuisine_types,
            reviews=reviews,
            can_review=can_review,
            category_filter=category_filter,
            cuisine_filter=cuisine_filter,
            price_filter=price_filter,
            dietary_filter=dietary_filter,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Error in restaurant detail: %s", exc)
        flash('An error occurred while loading restaurant details.', 'error')
        return redirect(url_for('customer.restaurants'))


@customer_bp.route('/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    """Add item to cart."""
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
        existing_cart_item = Cart.query.filter_by(
            customer_id=current_user.id, menu_item_id=menu_item_id
        ).first()
        if existing_cart_item:
            existing_cart_item.quantity += quantity
        else:
            db.session.add(
                Cart(customer_id=current_user.id, menu_item_id=menu_item_id, quantity=quantity)
            )
        db.session.commit()
        cart_count = (
            db.session.query(db.func.coalesce(db.func.sum(Cart.quantity), 0))
            .filter(Cart.customer_id == current_user.id)
            .scalar()
            or 0
        )
        return jsonify({'success': True, 'message': 'Item added to cart successfully', 'cart_count': int(cart_count)})
    except Exception as exc:  # noqa: BLE001
        logger.error("Error adding to cart: %s", exc)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'})


# ---- Discount / Coupon helpers ----

def _get_active_coupon() -> str:
    return (session.get('coupon_code') or '').upper().strip()


_COUPON_MAP: Dict[str, Tuple[float, Tuple[str, ...]]] = {
    'PIZZA50': (0.50, ('pizza',)),
    'BIRYANI30': (0.30, ('biryani',)),
    'HEALTHY40': (0.40, ('bowl', 'healthy')),
    'SUSHI25': (0.25, ('sushi',)),
}


def _is_item_eligible_for_coupon(menu_item: MenuItem, coupon: str) -> bool:
    if not coupon or coupon not in _COUPON_MAP:
        return False
    _, keywords = _COUPON_MAP[coupon]
    text = f"{menu_item.category} {menu_item.name}".lower()
    return any(k in text for k in keywords)


def _discounted_unit_price(menu_item: MenuItem, coupon: str) -> float:
    if coupon in _COUPON_MAP and _is_item_eligible_for_coupon(menu_item, coupon):
        pct, _ = _COUPON_MAP[coupon]
        return round(menu_item.price * (1 - pct), 2)
    return menu_item.price


@customer_bp.route('/apply-coupon', methods=['POST'])
@login_required
def apply_coupon():
    """Apply a coupon code for the current session (customers only)."""
    if not current_user.is_customer():
        return jsonify({'success': False, 'message': 'Access denied'})
    try:
        code = (request.json.get('code') or '').upper().strip()
        if code and code not in _COUPON_MAP:
            return jsonify({'success': False, 'message': 'Invalid coupon code'})
        session['coupon_code'] = code
        cart_items = Cart.query.filter_by(customer_id=current_user.id).all()
        subtotal = sum(item.quantity * item.menu_item.price for item in cart_items)
        coupon = _get_active_coupon()
        discounted_total = sum(item.quantity * _discounted_unit_price(item.menu_item, coupon) for item in cart_items)
        total_discount = round(subtotal - discounted_total, 2)
        return jsonify({'success': True, 'message': 'Coupon applied' if code else 'Coupon cleared', 'subtotal': subtotal, 'discount': total_discount, 'total': discounted_total})
    except Exception as exc:  # noqa: BLE001
        logger.error("Error applying coupon: %s", exc)
        return jsonify({'success': False, 'message': 'An error occurred'})


@customer_bp.route('/cart')
@login_required
def cart():
    """Shopping cart page."""
    if not current_user.is_customer():
        flash('Access denied. Customer access required.', 'error')
        return redirect(url_for('main.index'))
    try:
        cart_items = Cart.query.filter_by(customer_id=current_user.id).all()
        coupon = _get_active_coupon()
        subtotal = sum(item.quantity * item.menu_item.price for item in cart_items)
        discounted_total = sum(item.quantity * _discounted_unit_price(item.menu_item, coupon) for item in cart_items)
        total_amount = discounted_total
        return render_template('customer/cart.html', cart_items=cart_items, subtotal_amount=subtotal, total_discount=round(subtotal - discounted_total, 2), applied_coupon=coupon, total_amount=total_amount)
    except Exception as exc:  # noqa: BLE001
        logger.error("Error in cart view: %s", exc)
        flash('An error occurred while loading cart.', 'error')
        return render_template('customer/cart.html')


@customer_bp.route('/remove-from-cart', methods=['POST'])
@login_required
def remove_from_cart():
    """Remove item from cart."""
    if not current_user.is_customer():
        return jsonify({'success': False, 'message': 'Access denied'})
    try:
        cart_item_id = request.json.get('cart_item_id')
        if not cart_item_id:
            return jsonify({'success': False, 'message': 'Invalid cart item'})
        cart_item = Cart.query.filter_by(id=cart_item_id, customer_id=current_user.id).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
            cart_count = (
                db.session.query(db.func.coalesce(db.func.sum(Cart.quantity), 0))
                .filter(Cart.customer_id == current_user.id)
                .scalar()
                or 0
            )
            cart_items = Cart.query.filter_by(customer_id=current_user.id).all()
            coupon = _get_active_coupon()
            subtotal = sum(item.quantity * item.menu_item.price for item in cart_items)
            discounted_total = sum(item.quantity * _discounted_unit_price(item.menu_item, coupon) for item in cart_items)
            return jsonify({'success': True, 'message': 'Item removed from cart', 'cart_count': cart_count, 'subtotal_amount': subtotal, 'total_amount': discounted_total, 'discount_amount': round(subtotal - discounted_total, 2)})
        return jsonify({'success': False, 'message': 'Item not found in cart'})
    except Exception as exc:  # noqa: BLE001
        logger.error("Error removing from cart: %s", exc)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'})


@customer_bp.route('/update-cart-quantity', methods=['POST'])
@login_required
def update_cart_quantity():
    """Update quantity for a cart item and return updated totals."""
    if not current_user.is_customer():
        return jsonify({'success': False, 'message': 'Access denied'})
    try:
        cart_item_id = request.json.get('cart_item_id')
        quantity = request.json.get('quantity')
        if not cart_item_id or not quantity or int(quantity) < 1:
            return jsonify({'success': False, 'message': 'Invalid data'})
        cart_item = Cart.query.filter_by(id=cart_item_id, customer_id=current_user.id).first()
        if not cart_item:
            return jsonify({'success': False, 'message': 'Cart item not found'})
        cart_item.quantity = int(quantity)
        db.session.commit()
        cart_count = (
            db.session.query(db.func.coalesce(db.func.sum(Cart.quantity), 0))
            .filter(Cart.customer_id == current_user.id)
            .scalar()
            or 0
        )
        cart_items = Cart.query.filter_by(customer_id=current_user.id).all()
        coupon = _get_active_coupon()
        subtotal = sum(item.quantity * item.menu_item.price for item in cart_items)
        discounted_total = sum(item.quantity * _discounted_unit_price(item.menu_item, coupon) for item in cart_items)
        unit_price = _discounted_unit_price(cart_item.menu_item, coupon)
        line_total = cart_item.quantity * unit_price
        return jsonify({'success': True, 'message': 'Cart updated', 'cart_count': int(cart_count), 'subtotal_amount': subtotal, 'total_amount': discounted_total, 'discount_amount': round(subtotal - discounted_total, 2), 'line_total': line_total, 'line_unit_price': unit_price})
    except Exception as exc:  # noqa: BLE001
        logger.error("Error updating cart quantity: %s", exc)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'})


@customer_bp.route('/place-order', methods=['POST'])
@login_required
def place_order():
    """Place order."""
    if not current_user.is_customer():
        return jsonify({'success': False, 'message': 'Access denied'})
    try:
        cart_items = Cart.query.filter_by(customer_id=current_user.id).all()
        if not cart_items:
            return jsonify({'success': False, 'message': 'Cart is empty'})
        coupon = _get_active_coupon()
        restaurant_items: Dict[int, list[Cart]] = {}
        for item in cart_items:
            restaurant_id = item.menu_item.restaurant_id
            restaurant_items.setdefault(restaurant_id, []).append(item)
        orders = []
        for restaurant_id, items in restaurant_items.items():
            order_number = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{current_user.id}{restaurant_id}"
            total_amount = 0.0
            for item in items:
                unit = _discounted_unit_price(item.menu_item, coupon)
                total_amount += item.quantity * unit
            order = Order(order_number=order_number, total_amount=round(total_amount, 2), customer_id=current_user.id, restaurant_id=restaurant_id)
            db.session.add(order)
            db.session.flush()
            for item in items:
                unit = _discounted_unit_price(item.menu_item, coupon)
                db.session.add(OrderItem(order_id=order.id, menu_item_id=item.menu_item_id, quantity=item.quantity, price=unit))
                item.menu_item.order_count += item.quantity
            orders.append(order)
        Cart.query.filter_by(customer_id=current_user.id).delete()
        session['coupon_code'] = ''
        db.session.commit()
        return jsonify({'success': True, 'message': f'Order placed successfully! Order number: {orders[0].order_number}', 'order_number': orders[0].order_number})
    except Exception as exc:  # noqa: BLE001
        logger.error("Error placing order: %s", exc)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred while placing order'})


@customer_bp.route('/orders')
@login_required
def orders():
    """Order history."""
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
        orders_paged = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
        return render_template('customer/orders.html', orders=orders_paged, search=search, status_filter=status_filter)
    except Exception as exc:  # noqa: BLE001
        logger.error("Error in orders view: %s", exc)
        flash('An error occurred while loading orders.', 'error')
        return render_template('customer/orders.html')


@customer_bp.route('/profile')
@login_required
def profile():
    """Customer profile."""
    if not current_user.is_customer():
        flash('Access denied. Customer access required.', 'error')
        return redirect(url_for('main.index'))
    try:
        preferences = UserPreference.query.filter_by(user_id=current_user.id).all()
        cuisine_types = [c[0] for c in db.session.query(MenuItem.cuisine_type).distinct().all()]
        restaurant_options = [
            (r.id, r.name) for r in Restaurant.query.filter_by(is_active=True).order_by(Restaurant.name.asc()).all()
        ]
        dietary_options = ['vegetarian', 'vegan', 'gluten_free', 'no_spicy']
        return render_template('customer/profile.html', preferences=preferences, cuisine_types=cuisine_types, restaurant_options=restaurant_options, dietary_options=dietary_options)
    except Exception as exc:  # noqa: BLE001
        logger.error("Error in profile view: %s", exc)
        flash('An error occurred while loading profile.', 'error')
        return render_template('customer/profile.html')


@customer_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Update customer profile."""
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
    except Exception as exc:  # noqa: BLE001
        logger.error("Error updating profile: %s", exc)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'})


@customer_bp.route('/add-preference', methods=['POST'])
@login_required
def add_preference():
    """Add a user preference."""
    if not current_user.is_customer():
        return jsonify({'success': False, 'message': 'Access denied'})
    try:
        data = request.get_json(silent=True) or {}
        pref_type = (data.get('preference_type') or '').strip()
        pref_value = (data.get('preference_value') or '').strip()
        allowed_types = {'favorite_cuisine', 'favorite_restaurant', 'dietary_restriction'}
        if pref_type not in allowed_types or not pref_value:
            return jsonify({'success': False, 'message': 'Invalid preference data'})
        existing = UserPreference.query.filter_by(user_id=current_user.id, preference_type=pref_type, preference_value=pref_value).first()
        if existing:
            return jsonify({'success': True, 'message': 'Preference already exists'})
        db.session.add(UserPreference(preference_type=pref_type, preference_value=pref_value, user_id=current_user.id))
        db.session.commit()
        return jsonify({'success': True, 'message': 'Preference added successfully'})
    except Exception as exc:  # noqa: BLE001
        logger.error("Error adding preference: %s", exc)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'})


@customer_bp.route('/remove-preference', methods=['POST'])
@login_required
def remove_preference():
    """Remove a user preference by id."""
    if not current_user.is_customer():
        return jsonify({'success': False, 'message': 'Access denied'})
    try:
        data = request.get_json(silent=True) or {}
        pref_id = data.get('preference_id')
        if not pref_id:
            return jsonify({'success': False, 'message': 'Invalid preference id'})
        pref = UserPreference.query.filter_by(id=pref_id, user_id=current_user.id).first()
        if not pref:
            return jsonify({'success': False, 'message': 'Preference not found'})
        db.session.delete(pref)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Preference removed successfully'})
    except Exception as exc:  # noqa: BLE001
        logger.error("Error removing preference: %s", exc)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'})


@customer_bp.route('/add-review', methods=['POST'])
@login_required
def add_review():
    """Add a review if user has a delivered order for the restaurant."""
    if not current_user.is_customer():
        return jsonify({'success': False, 'message': 'Access denied'})
    try:
        restaurant_id = request.json.get('restaurant_id')
        rating = int(request.json.get('rating', 0))
        comment = request.json.get('comment', '').strip()
        if not restaurant_id or rating < 1 or rating > 5 or not comment:
            return jsonify({'success': False, 'message': 'Invalid review data'})
        eligible = Order.query.filter_by(customer_id=current_user.id, restaurant_id=restaurant_id, status='delivered').first()
        if not eligible:
            return jsonify({'success': False, 'message': 'You can review only after a delivered order'})
        db.session.add(Review(rating=rating, comment=comment, user_id=current_user.id, restaurant_id=restaurant_id))
        db.session.commit()
        restaurant = Restaurant.query.get(restaurant_id)
        reviews = Review.query.filter_by(restaurant_id=restaurant_id).all()
        restaurant.total_reviews = len(reviews)
        restaurant.rating = sum(r.rating for r in reviews) / len(reviews)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Review added successfully'})
    except Exception as exc:  # noqa: BLE001
        logger.error("Error adding review: %s", exc)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'})


def get_customer_recommendations(customer_id: int):
    """Get personalized recommendations for customer."""
    try:
        preferences = UserPreference.query.filter_by(user_id=customer_id).all()
        dietary_values = {p.preference_value for p in preferences if p.preference_type == 'dietary_restriction'}
        require_veg = 'vegetarian' in dietary_values
        require_vegan = 'vegan' in dietary_values
        require_gluten_free = 'gluten_free' in dietary_values
        favorite_cuisines = [p.preference_value for p in preferences if p.preference_type == 'favorite_cuisine']
        base_query = MenuItem.query.filter(MenuItem.is_available.is_(True))
        if favorite_cuisines:
            base_query = base_query.filter(MenuItem.cuisine_type.in_(favorite_cuisines))
        if require_vegan:
            base_query = base_query.filter(MenuItem.is_vegan.is_(True))
        if require_veg:
            base_query = base_query.filter(MenuItem.is_vegetarian.is_(True))
        if require_gluten_free:
            base_query = base_query.filter(MenuItem.is_gluten_free.is_(True))
        filtered_popular = base_query.order_by(MenuItem.order_count.desc()).limit(8).all()
        if len(filtered_popular) < 8:
            backfill_query = MenuItem.query.filter(MenuItem.is_available.is_(True))
            if require_vegan:
                backfill_query = backfill_query.filter(MenuItem.is_vegan.is_(True))
            if require_veg:
                backfill_query = backfill_query.filter(MenuItem.is_vegetarian.is_(True))
            if require_gluten_free:
                backfill_query = backfill_query.filter(MenuItem.is_gluten_free.is_(True))
            backfill = backfill_query.order_by(MenuItem.order_count.desc()).limit(8 - len(filtered_popular)).all()
        else:
            backfill = []
        seen: set[int] = set()
        combined = []
        for item in filtered_popular + backfill:
            if item.id not in seen:
                seen.add(item.id)
                combined.append(item)
        return combined[:8]
    except Exception as exc:  # noqa: BLE001
        logger.error("Error getting recommendations: %s", exc)
        return []


