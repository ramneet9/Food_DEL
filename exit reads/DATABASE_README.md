# Database Guide

This document explains the database schema, relationships, data flows, seeding/sync, and operational concerns for the JustEat Technology app.

## 1) Technology & Connection
- ORM: SQLAlchemy (Flask‑SQLAlchemy)
- Default DB: SQLite (file in `instance/food_ordering.db`)
- Switch DB: set `DATABASE_URL` in environment (e.g., Postgres)
- Config: see `app.py` and `config.py`

## 2) Schema Overview (ER)
- Users (1) —< Restaurants (N)
- Restaurants (1) —< MenuItems (N)
- Users (1) —< Orders (N) —< OrderItems (N)
- Users (1) —< Cart (N) (pending pre‑order items)
- Users (1) —< UserPreferences (N)
- Restaurants (1) —< Reviews (N)

## 3) Tables & Fields
- users
  - id PK, username (unique), email (unique), password_hash
  - role: 'customer' | 'restaurant_owner'
  - first_name, last_name, phone, address, created_at
  - relationships: restaurants, orders, preferences, reviews
- restaurants
  - id PK, owner_id FK→users.id (required)
  - name, description, cuisine_type, location, phone, email
  - rating (float), total_reviews (int), is_active (bool), created_at
  - relationships: menu_items, orders, reviews
- menu_items
  - id PK, restaurant_id FK→restaurants.id (required)
  - name, description, price (float), category, cuisine_type
  - flags: is_vegetarian, is_vegan, is_gluten_free, is_available
  - badges: is_special, is_deal_of_day
  - analytics: order_count (int), image_url, created_at
- orders
  - id PK, order_number (unique), status (default 'pending')
  - total_amount (float), notes, created_at, updated_at
  - customer_id FK→users.id (required), restaurant_id FK→restaurants.id (required)
  - relationship: order_items
- order_items
  - id PK, order_id FK→orders.id (required)
  - menu_item_id FK→menu_items.id (required)
  - quantity (int), price (float at time of order)
- cart
  - id PK, customer_id FK→users.id (required)
  - menu_item_id FK→menu_items.id (required)
  - quantity (int, default 1), created_at
- user_preferences
  - id PK, user_id FK→users.id (required)
  - preference_type: 'favorite_restaurant' | 'favorite_cuisine' | 'dietary_restriction'
  - preference_value (string)
  - created_at
- reviews
  - id PK, rating (1–5), comment, created_at
  - user_id FK→users.id (required)
  - restaurant_id FK→restaurants.id (nullable False in practice)
  - menu_item_id FK→menu_items.id (optional)
  - owner_reply (text), owner_reply_at (datetime)

## 4) Key Relationships & Integrity
- One owner (user) can have many restaurants (`restaurants.owner_id`)
- A restaurant can have many menu items, orders, and reviews
- An order belongs to one customer and one restaurant; line items store price at order time
- Cart rows reference a customer and a menu item
- Reviews are scoped to restaurants (and optionally menu items)
- Data integrity enforced via non‑nullable FKs; cascade deletes are handled at app level (restaurant delete):
  1) Delete reviews → delete cart/order_items referencing the restaurant’s menu items → delete orders → delete menu_items → delete restaurant

## 5) Data Lifecycle
- Add to cart: inserts/updates `cart` rows
- Place order: groups cart rows by `restaurant_id` → creates multiple `orders` → for each, creates `order_items` (price captured at time), updates `menu_items.order_count`, and clears cart
- Update order status: changes `orders.status`, updates `updated_at`
- Reviews: allowed only if delivered order exists for that restaurant; updates restaurant `rating` and `total_reviews`

## 6) Seeding & Syncing
- Initial seed: `seed_all_data()` creates baseline users, restaurants, menu items, preferences, reviews
- Idempotent sync: `sync_all_data()` upserts users, restaurants, menu items, preferences, reviews; then recomputes `rating` and `total_reviews`
- Run sync safely on live DB:
```bash
py -3 -c "from app import app; from seed_data import sync_all_data; app.app_context().push(); sync_all_data()"
```

## 7) Querying Patterns
- Common filters:
  - Restaurants: by `is_active`, name, cuisine_type, location
  - MenuItems: by restaurant, category, cuisine, price bands, dietary flags
  - Orders: by customer/restaurant, status, created_at
  - Reviews: by restaurant, newest first
- “Mostly ordered” heuristic (on MenuItem): counts today’s `OrderItem` rows for that menu item (threshold > 10)

## 8) Transactions & Errors
- Route handlers wrap DB changes in try/except and call `db.session.rollback()` on failure
- Multi‑entity operations (e.g., place order, delete restaurant) execute in a single logical transaction per request

## 9) Performance Notes
- Use filters and pagination for restaurants and orders
- `order_count` on menu items is updated incrementally at checkout for faster popularity queries
- For non‑SQLite DBs, add indexes as needed: e.g., `(orders.customer_id)`, `(orders.restaurant_id, created_at)`, `(menu_items.restaurant_id)`

## 10) Migrations
- SQLite is used by default; schema is created by `db.create_all()`
- A light migration step adds owner reply columns to `reviews` if missing
- For production DBs, adopt Alembic migrations (not included by default)

## 11) Environment & Switching DB
- `.env` (development):
```
SECRET_KEY=...
DATABASE_URL=sqlite:///instance/food_ordering.db
```
- Switch to Postgres:
```
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname
```

## 12) Backup & Restore (SQLite)
- Back up: copy `instance/food_ordering.db`
- Sample backup made by scripts: `instance/food_ordering.backup.YYYYMMDD_HHMMSS.db`
- Restore: replace the active `.db` with a backup copy (while app is stopped)

## 13) Testing & Reliability
- Tests use an in‑memory SQLite DB per run
- Relationship tests assert parent/child integrity
- End‑to‑end tests ensure cart→order flow and owner CRUD work

## 14) FAQ
- Why store price on `order_items`? Prices can change; orders must remain immutable audit records
- Why multiple orders on checkout? One per restaurant to simplify fulfillment and status flows
- Can owners reply to reviews? Yes; stored on `reviews.owner_reply` and timestamped
- How are ratings computed? On seed/sync, aggregated from current reviews; during runtime after inserts

## 15) Future Enhancements
- Normalize addresses and phone validation
- Soft deletes with `is_active` across more tables
- Alembic migrations & seed versioning
- Add DB‑side cascades and indexes for non‑SQLite engines
