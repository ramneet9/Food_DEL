# Tests Overview

This project includes a lightweight but complete unit test suite that covers models, routes (UI/back-end), and relationships.

## How to run
- Run all tests:
```bash
python tests.py
```
- Verbose mode:
```bash
python -m unittest -v tests.py
```
- Run a single test class or test method:
```bash
python -m unittest tests.TestMenuItemModel
python -m unittest tests.TestMenuItemModel.test_mostly_ordered_functionality
```

## What the tests cover (tests.py)
- TestUserModel
  - test_user_creation: password hashing, role helpers
  - test_restaurant_owner_role: owner vs customer role checks
- TestRestaurantModel
  - test_restaurant_creation: basic fields and owner assignment
- TestMenuItemModel
  - test_menu_item_creation: basic fields and restaurant FK
  - test_mostly_ordered_functionality: verifies the "mostly ordered" heuristic
- TestOrderModel
  - test_order_creation: default status, amount and identifiers
- TestCartModel
  - test_cart_item_creation: cart row creation and quantities
- TestUserPreferenceModel
  - test_user_preference_creation: preferences insert
- TestReviewModel
  - test_review_creation: review fields and FKs
- TestAuthenticationRoutes
  - test_login_page_loads: GET /auth/login returns 200 and expected text
  - test_login_with_valid_credentials: POST /auth/login success path
  - test_login_with_invalid_credentials: error message path
- TestCustomerRoutes
  - test_customer_dashboard_requires_login: protected route redirects
  - test_restaurants_page_loads: protected route redirects
- TestRestaurantRoutes
  - test_restaurant_dashboard_requires_login: protected route redirects
  - test_add_restaurant_page_loads: protected route redirects
- TestMainRoutes
  - test_home_page_loads: GET / returns 200 and expected text
  - test_logout_redirects: protected logout redirects properly
- TestDatabaseRelationships
  - test_user_restaurant_relationship: owner ↔ restaurants
  - test_restaurant_menu_items_relationship: restaurant ↔ menu_items
  - test_order_relationships: order ↔ customer/restaurant

## Notes on the test harness
- Uses an in-memory SQLite database per test run.
- Maintains an application context for the duration of each test, and stores IDs in setUp to avoid DetachedInstanceError by re-querying instances when needed.
- Tests can be extended by following the existing class structure.

## Troubleshooting
- If you see DetachedInstanceError, ensure tests re-query instances from the current session/app context.
- If you changed seed logic or models, re-run tests after reinstalling deps if necessary: `pip install -r requirements.txt`.
