# JustEat Technology - Viva Cheat Sheet

A fast, high-signal briefing to explain and demo the project in minutes.

## What this app is
- A Flask-based food ordering platform with two roles:
  - Customer: browse restaurants, add to cart, place orders, review
  - Restaurant Owner: manage restaurants, menus, and process orders
- SQLite database (default) with SQLAlchemy ORM
- Bootstrap 5 UI with a modern look and client-side enhancements (jQuery)

## How it’s structured
- `app.py`: App boot, blueprint registration, error handlers, context helpers
- `blueprints/`: Modular route groups
  - `main.py`: Home/landing
  - `auth.py`: Login, logout, change password
  - `customer.py`: Customer dashboard, restaurants, cart, orders, profile, reviews
  - `restaurant.py`: Owner dashboard, restaurants, menu CRUD, orders, reviews
- `models.py`: SQLAlchemy models and relationships
- `seed_data.py`: Initial data seeding + safe upsert sync (`sync_all_data`)
- `templates/`: Jinja2 pages; `static/`: CSS/JS and images

## How to run
1. Python 3.10+
2. Install deps: `pip install -r requirements.txt`
3. Initialize DB and seed:
   - First run: `python app.py` (auto-creates tables + seeds)
   - Or later sync: `py -3 -c "from app import app; from seed_data import sync_all_data; app.app_context().push(); sync_all_data()"`
4. Start: `python app.py` → visit `http://localhost:5000`

## Demo credentials
- Customers: `ramneet/ramneet`, `batman/batman`
- Owners: `chef_mario/mario`, `chef_raj/raj`

## Key features to show
- Customer
  - Browse/filter restaurants; location dropdown prioritizes matching restaurants
  - Add to cart, apply coupons (PIZZA50, BIRYANI30, HEALTHY40, SUSHI25)
  - Place order (split per restaurant; discounted line prices)
  - Order history and reviews (only after delivered order)
- Restaurant Owner
  - Dashboard: stats, recent orders, recent reviews
  - Manage restaurants (add/delete) and menus (add/update/delete items)
  - Orders: filter by status; update statuses

## Database essentials (short)
- Users (customers/owners)
- Restaurants (owner_id FK) → MenuItems → OrderItems
- Orders (customer_id, restaurant_id) split by restaurant at checkout
- Cart: customer pending selections
- Reviews: for restaurants; owners can reply

## What sets this apart
- Modular Flask blueprints; PEP 8 compliant
- Idempotent seed sync for safe updates on live DB
- Thoughtful UI touches: fixed navbar, full-bleed backgrounds, smooth reorder on location

## Common Q&A
- Why SQLite? Simple to run anywhere; easily swapped for Postgres via `DATABASE_URL`.
- How are coupons applied? Session-level code; per-line discounts; totals recomputed in API.
- How do you ensure roles? Flask-Login + role checks on endpoints + UI.
- Can owners reply to reviews? Yes; stored on Review model, timestamped.

## Quick troubleshooting
- If images don’t appear for a restaurant: helper slugifies names and tries extensions; or add explicit mapping in `app.py` context.
- If seed ran previously but you updated data: run `sync_all_data()`.
