# JustEat Technology - Deep Dive

An in-depth guide to understand the architecture, code, and database.

## 1. Overview
- Tech stack: Flask, SQLAlchemy, Flask-Login, Bootstrap 5, jQuery
- Runtime: Python 3.10+, SQLite by default (switchable via `DATABASE_URL`)
- App entry: `app.py`

## 2. App lifecycle and configuration
- `app.py` initializes Flask, config, logging, SQLAlchemy, and LoginManager.
- Blueprints are registered here with their URL prefixes.
- Context processors:
  - `inject_user`: exposes `current_user` to templates
  - `inject_image_paths`: provides `restaurant_image(name)` and a dictionary of image URLs
  - `inject_cart_count`: computes cart count (sum of quantities) for navbar
- Startup helpers:
  - `create_tables()`: `db.create_all()` + light SQLite migration for Review reply columns
  - `seed_database()`: calls `seed_all_data()` once for a fresh environment

## 3. Modular routing (blueprints/)
- `blueprints/main.py`:
  - `/`: home page; loads featured restaurants & curated items
- `blueprints/auth.py`:
  - `/auth/login`: login and role-based redirect
  - `/auth/logout`: logs out
  - `/auth/reset-password`: change password for authenticated user
- `blueprints/customer.py`:
  - `/customer/dashboard`: recent orders, recommendations, cart count
  - `/customer/restaurants`: paginated, filtered list
  - `/customer/restaurant/<id>`: menu with filters; reviews
  - Cart APIs: add/remove/update, apply-coupon, place-order
  - `/customer/orders`: order history
  - `/customer/profile`: preferences management; update profile
  - `/customer/add-review`: gated by delivered order
- `blueprints/restaurant.py`:
  - `/restaurant/dashboard`: owner stats, recent orders, recent reviews
  - `/restaurant/restaurants`: manage owned restaurants
  - `/restaurant/add-restaurant`, `/restaurant/delete-restaurant`
  - Menu APIs: add/update/delete menu items
  - `/restaurant/orders`: filter by status; update order status
  - `/restaurant/reviews`: list reviews across owned restaurants

## 4. Models (models.py)
- `User` (customers and restaurant owners)
  - `role` in {`customer`, `restaurant_owner`}
  - Relationships: `restaurants`, `orders`, `preferences`, `reviews`
  - Methods: `set_password`, `check_password`, role helpers
- `Restaurant`
  - `owner_id` → `User`
  - `rating`, `total_reviews` maintained via review inserts and seed sync
  - Relationships: `menu_items`, `orders`, `reviews`
- `MenuItem`
  - Pricing and flags: `is_special`, `is_deal_of_day`, `is_available`
  - `order_count` used for “mostly ordered” heuristic
  - Relationship helpers; `is_mostly_ordered()` checks today’s order volume
- `Order` and `OrderItem`
  - Orders are created per-restaurant on checkout; line prices store the price at order time
- `Cart`
  - Staging area before orders; quantities summed for badge
- `UserPreference`
  - Favorite cuisines, favorite restaurants, dietary restrictions
- `Review`
  - Stores rating/comment; owner replies: `owner_reply`, `owner_reply_at`

## 5. Seeding and data sync (seed_data.py)
- `seed_all_data()`: initial seed once on clean DB
- `sync_all_data()`: idempotent upsert that updates existing data safely in live DB
  - Upserts: users, restaurants, menu items, preferences, reviews
  - Recomputes `Restaurant.rating` and `Restaurant.total_reviews`
- Usage to sync live:
  ```bash
  py -3 -c "from app import app; from seed_data import sync_all_data; app.app_context().push(); sync_all_data()"
  ```

## 6. Request flow highlights
- Authentication: Flask-Login; role checks enforced server-side on every route
- Coupons: session-level `coupon_code`; `_COUPON_MAP` defines discount and keyword scope
- Checkout: cart items grouped by `restaurant_id`, multiple `Order`s created in one go
- Reviews: gated by delivered order check; owner replies stored on Review

## 7. Frontend behavior
- Navbar: fixed, with location selector (stored in `localStorage`)
- Restaurants list: when location is chosen, matching locations are reordered to the top with a subtle grid fade
- Cards: hover micro-interactions, consistent spacing, accessible contrast
- Assets: `restaurant_image(name)` slugifies and checks common extensions; explicit overrides available

## 8. Styling and scripts
- `static/css/style.css`: design system, components, utilities
- `static/js/main.js`: toasts, cart actions, filters, location selection, reorder logic

## 9. Configuration (config.py)
- Ensure `SECRET_KEY` and `DATABASE_URL` are set in environment for production

## 10. Running in production
- Use a WSGI server (gunicorn/uwsgi) behind a reverse proxy
- Set `FLASK_ENV=production`, proper logging, strong `SECRET_KEY`
- Prefer Postgres/MySQL via `DATABASE_URL`

## 11. PEP 8, quality, and conventions
- Blueprints split by domain; readable functions with early returns
- Logging on errors; DB rollbacks on failures
- Type hints where helpful; docstrings on modules and functions

## 12. Future improvements
- Pagination improvements for large menus
- Realtime notifications (WebSocket/SSE) for order status updates
- Service layer + unit tests; CI with ruff/black/pytest
