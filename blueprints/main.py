"""
Main (public) routes blueprint.
"""

import logging
from flask import Blueprint, render_template, flash
from models import Restaurant, MenuItem

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page."""
    try:
        featured_restaurants = Restaurant.query.filter_by(is_active=True).limit(6).all()
        special_items = MenuItem.query.filter_by(is_special=True, is_available=True).limit(4).all()
        deal_items = MenuItem.query.filter_by(is_deal_of_day=True, is_available=True).limit(4).all()
        return render_template(
            'index.html',
            featured_restaurants=featured_restaurants,
            special_items=special_items,
            deal_items=deal_items,
        )
    except Exception as exc:  # noqa: BLE001 - log and render fallback
        logger.error("Error in index route: %s", exc)
        flash('An error occurred while loading the home page.', 'error')
        return render_template('index.html')


