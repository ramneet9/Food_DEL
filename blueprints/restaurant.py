"""Restaurant owner routes blueprint."""

from __future__ import annotations

import logging
from datetime import datetime
import os

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    current_app,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from models import db, Restaurant, MenuItem, Order, OrderItem, Cart, Review

logger = logging.getLogger(__name__)

restaurant_bp = Blueprint('restaurant', __name__)


@restaurant_bp.route('/dashboard')
@login_required
def dashboard():
    """Restaurant owner dashboard."""
    if not current_user.is_restaurant_owner():
        flash('Access denied. Restaurant owner access required.', 'error')
        return redirect(url_for('main.index'))
    try:
        restaurants = Restaurant.query.filter_by(owner_id=current_user.id).all()
        restaurant_ids = [r.id for r in restaurants]
        recent_orders = (
            Order.query.filter(Order.restaurant_id.in_(restaurant_ids))
            .order_by(Order.created_at.desc())
            .limit(10)
            .all()
        )
        total_orders = Order.query.filter(Order.restaurant_id.in_(restaurant_ids)).count()
        pending_orders = Order.query.filter(
            Order.restaurant_id.in_(restaurant_ids), Order.status == 'pending'
        ).count()
        recent_reviews = (
            Review.query.filter(Review.restaurant_id.in_(restaurant_ids))
            .order_by(Review.created_at.desc())
            .limit(5)
            .all()
        )
        return render_template(
            'restaurant/dashboard.html',
            restaurants=restaurants,
            recent_orders=recent_orders,
            total_orders=total_orders,
            pending_orders=pending_orders,
            recent_reviews=recent_reviews,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Error in restaurant dashboard: %s", exc)
        flash('An error occurred while loading the dashboard.', 'error')
        return render_template('restaurant/dashboard.html')


@restaurant_bp.route('/restaurants')
@login_required
def restaurants():
    """Manage restaurants."""
    if not current_user.is_restaurant_owner():
        flash('Access denied. Restaurant owner access required.', 'error')
        return redirect(url_for('main.index'))
    try:
        restaurants_list = Restaurant.query.filter_by(owner_id=current_user.id).all()
        return render_template('restaurant/restaurants.html', restaurants=restaurants_list)
    except Exception as exc:  # noqa: BLE001
        logger.error("Error in restaurant management: %s", exc)
        flash('An error occurred while loading restaurants.', 'error')
        return render_template('restaurant/restaurants.html')


@restaurant_bp.route('/add-restaurant', methods=['GET', 'POST'])
@login_required
def add_restaurant():
    """Add new restaurant."""
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
            image_file = request.files.get('background_image')
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
                owner_id=current_user.id,
            )
            db.session.add(restaurant)
            db.session.commit()
            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                _, ext = os.path.splitext(filename)
                allowed_ext = {'.jpg', '.jpeg', '.png', '.webp'}
                if ext.lower() in allowed_ext:
                    import re
                    slug = re.sub(r"[^a-z0-9_\-]", "", name.strip().lower().replace(" ", "_"))
                    target_dir = os.path.join(current_app.static_folder, 'images', 'restaurants')
                    os.makedirs(target_dir, exist_ok=True)
                    save_path = os.path.join(target_dir, f"{slug}{ext.lower()}")
                    image_file.save(save_path)
            flash('Restaurant added successfully!', 'success')
            return redirect(url_for('restaurant.restaurants'))
        except Exception as exc:  # noqa: BLE001
            logger.error("Error adding restaurant: %s", exc)
            db.session.rollback()
            flash('An error occurred while adding restaurant.', 'error')
    return render_template('restaurant/add_restaurant.html')


@restaurant_bp.route('/delete-restaurant', methods=['POST'])
@login_required
def delete_restaurant():
    """Delete a restaurant (and its menu items)."""
    if not current_user.is_restaurant_owner():
        return jsonify({'success': False, 'message': 'Access denied'})
    try:
        restaurant_id = request.json.get('restaurant_id')
        restaurant = Restaurant.query.filter_by(id=restaurant_id, owner_id=current_user.id).first()
        if not restaurant:
            return jsonify({'success': False, 'message': 'Restaurant not found'})
        try:
            Review.query.filter_by(restaurant_id=restaurant.id).delete(synchronize_session=False)
            menu_item_ids = [m.id for m in MenuItem.query.filter_by(restaurant_id=restaurant.id).all()]
            if menu_item_ids:
                Cart.query.filter(Cart.menu_item_id.in_(menu_item_ids)).delete(synchronize_session=False)
                OrderItem.query.filter(OrderItem.menu_item_id.in_(menu_item_ids)).delete(synchronize_session=False)
            Order.query.filter_by(restaurant_id=restaurant.id).delete(synchronize_session=False)
            MenuItem.query.filter_by(restaurant_id=restaurant.id).delete(synchronize_session=False)
            db.session.delete(restaurant)
            db.session.commit()
        except Exception as exc:  # noqa: BLE001
            logger.error("Error during cascading delete for restaurant %s: %s", restaurant_id, exc)
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Failed to delete due to related data'})
        return jsonify({'success': True, 'message': 'Restaurant deleted'})
    except Exception as exc:  # noqa: BLE001
        logger.error("Error deleting restaurant: %s", exc)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'})


@restaurant_bp.route('/restaurant/<int:restaurant_id>/menu')
@login_required
def menu_management(restaurant_id: int):
    """Manage restaurant menu."""
    if not current_user.is_restaurant_owner():
        flash('Access denied. Restaurant owner access required.', 'error')
        return redirect(url_for('main.index'))
    try:
        restaurant = Restaurant.query.filter_by(id=restaurant_id, owner_id=current_user.id).first_or_404()
        menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
        return render_template('restaurant/menu_management.html', restaurant=restaurant, menu_items=menu_items)
    except Exception as exc:  # noqa: BLE001
        logger.error("Error in menu management: %s", exc)
        flash('An error occurred while loading menu.', 'error')
        return redirect(url_for('restaurant.restaurants'))


@restaurant_bp.route('/add-menu-item', methods=['POST'])
@login_required
def add_menu_item():
    """Add menu item."""
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
        restaurant = Restaurant.query.filter_by(id=restaurant_id, owner_id=current_user.id).first()
        if not restaurant:
            return jsonify({'success': False, 'message': 'Restaurant not found'})
        db.session.add(MenuItem(name=name, description=description, price=float(price), category=category, cuisine_type=cuisine_type, is_vegetarian=is_vegetarian, is_vegan=is_vegan, is_gluten_free=is_gluten_free, is_special=is_special, is_deal_of_day=is_deal_of_day, restaurant_id=restaurant_id))
        db.session.commit()
        return jsonify({'success': True, 'message': 'Menu item added successfully'})
    except Exception as exc:  # noqa: BLE001
        logger.error("Error adding menu item: %s", exc)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'})


@restaurant_bp.route('/update-menu-item', methods=['POST'])
@login_required
def update_menu_item():
    """Edit an existing menu item (owner only)."""
    if not current_user.is_restaurant_owner():
        return jsonify({'success': False, 'message': 'Access denied'})
    try:
        data = request.get_json(silent=True) or {}
        item_id = data.get('id')
        if not item_id:
            return jsonify({'success': False, 'message': 'Invalid menu item'})
        item = MenuItem.query.join(Restaurant).filter(
            MenuItem.id == item_id, Restaurant.owner_id == current_user.id
        ).first()
        if not item:
            return jsonify({'success': False, 'message': 'Menu item not found'})
        updatable_fields = ['name', 'description', 'price', 'category', 'cuisine_type', 'is_vegetarian', 'is_vegan', 'is_gluten_free', 'is_special', 'is_deal_of_day', 'is_available']
        for field in updatable_fields:
            if field in data:
                setattr(item, field, data[field])
        db.session.commit()
        return jsonify({'success': True, 'message': 'Menu item updated'})
    except Exception as exc:  # noqa: BLE001
        logger.error("Error updating menu item: %s", exc)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'})


@restaurant_bp.route('/delete-menu-item', methods=['POST'])
@login_required
def delete_menu_item():
    """Delete a menu item (owner only)."""
    if not current_user.is_restaurant_owner():
        return jsonify({'success': False, 'message': 'Access denied'})
    try:
        item_id = request.json.get('id')
        item = MenuItem.query.join(Restaurant).filter(
            MenuItem.id == item_id, Restaurant.owner_id == current_user.id
        ).first()
        if not item:
            return jsonify({'success': False, 'message': 'Menu item not found'})
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Menu item deleted'})
    except Exception as exc:  # noqa: BLE001
        logger.error("Error deleting menu item: %s", exc)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'})


@restaurant_bp.route('/orders')
@login_required
def orders():
    """Manage orders."""
    if not current_user.is_restaurant_owner():
        flash('Access denied. Restaurant owner access required.', 'error')
        return redirect(url_for('main.index'))
    try:
        restaurants = Restaurant.query.filter_by(owner_id=current_user.id).all()
        restaurant_ids = [r.id for r in restaurants]
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', '')
        query = Order.query.filter(Order.restaurant_id.in_(restaurant_ids))
        if status_filter:
            query = query.filter(Order.status == status_filter)
        orders_paged = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
        return render_template('restaurant/orders.html', orders=orders_paged, restaurants=restaurants, status_filter=status_filter)
    except Exception as exc:  # noqa: BLE001
        logger.error("Error in orders management: %s", exc)
        flash('An error occurred while loading orders.', 'error')
        return render_template('restaurant/orders.html')


@restaurant_bp.route('/update-order-status', methods=['POST'])
@login_required
def update_order_status():
    """Update order status."""
    if not current_user.is_restaurant_owner():
        return jsonify({'success': False, 'message': 'Access denied'})
    try:
        order_id = request.json.get('order_id')
        status = request.json.get('status')
        if not order_id or not status:
            return jsonify({'success': False, 'message': 'Invalid data'})
        order = Order.query.join(Restaurant).filter(
            Order.id == order_id, Restaurant.owner_id == current_user.id
        ).first()
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'})
        order.status = status
        order.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Order status updated successfully'})
    except Exception as exc:  # noqa: BLE001
        logger.error("Error updating order status: %s", exc)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'})


@restaurant_bp.route('/reviews')
@login_required
def owner_reviews():
    """List reviews for all restaurants owned by the current owner."""
    if not current_user.is_restaurant_owner():
        flash('Access denied. Restaurant owner access required.', 'error')
        return redirect(url_for('main.index'))
    try:
        restaurants = Restaurant.query.filter_by(owner_id=current_user.id).all()
        restaurant_ids = [r.id for r in restaurants]
        reviews = Review.query.filter(Review.restaurant_id.in_(restaurant_ids)).order_by(Review.created_at.desc()).all()
        return render_template('restaurant/orders.html', reviews=reviews, restaurants=restaurants)
    except Exception as exc:  # noqa: BLE001
        logger.error("Error loading owner reviews: %s", exc)
        flash('An error occurred while loading reviews.', 'error')
        return redirect(url_for('restaurant.dashboard'))



@restaurant_bp.route('/reply-review', methods=['POST'])
@login_required
def reply_review():
    """Allow restaurant owners to reply to a review for their restaurant."""
    if not current_user.is_restaurant_owner():
        return jsonify({'success': False, 'message': 'Access denied'})
    try:
        data = request.get_json(silent=True) or {}
        review_id = data.get('review_id')
        reply_text = (data.get('reply') or '').strip()
        if not review_id or not reply_text:
            return jsonify({'success': False, 'message': 'Invalid reply data'})

        # Ensure the review exists and belongs to one of the owner's restaurants
        review = (
            Review.query.join(Restaurant, Review.restaurant_id == Restaurant.id)
            .filter(Review.id == review_id, Restaurant.owner_id == current_user.id)
            .first()
        )
        if not review:
            return jsonify({'success': False, 'message': 'Review not found'})

        review.owner_reply = reply_text
        review.owner_reply_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Reply posted'})
    except Exception as exc:  # noqa: BLE001
        logger.error("Error replying to review: %s", exc)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'})

