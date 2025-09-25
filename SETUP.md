# 🍕 Food Ordering Application - Setup Guide

## Quick Setup (Recommended)

### Fresh Install / Reset (New or Existing Device)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run fresh setup script
python setup_fresh.py

# 3. Start the application
python app.py
```

The application will be available at: `http://localhost:5000`

---


## Optional: Manual Setup

If you prefer manual steps instead of the fresh script:

1) Install dependencies
```bash
pip install -r requirements.txt
```

2) Create a `.env` file in the project root
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/food_ordering.db
```

3) First run (creates tables and seeds automatically)
```bash
python app.py
```

---

## Demo Accounts

After setup, you can use these demo accounts:

### Customer Accounts
- **Username:** `ramneet` — **Password:** `ramneet`
- **Username:** `batman` — **Password:** `batman`

### Restaurant Owner Accounts
- **Username:** `chef_mario` — **Password:** `mario`
- **Username:** `chef_raj` — **Password:** `raj`

---

## Features Included

✅ **Customer Features:**
- Browse restaurants with beautiful background images
- View restaurant details with photos
- Add items to cart
- Place orders
- View order history
- User profile management

✅ **Restaurant Owner Features:**
- Restaurant dashboard
- Menu management
- Order management
- Restaurant statistics

✅ **Design Features:**
- Modern glass-morphism design
- Restaurant-specific background images
- Consistent color scheme (#85AA4A)
- Responsive layout
- Beautiful restaurant cards

---

## Troubleshooting

### Database Issues
If you encounter database issues and want a clean slate:
```bash
# Fresh reset (drops and recreates, then seeds)
python setup_fresh.py
```

If you modified `seed_data.py` and want to sync changes into an existing DB (no destructive reset):
```bash
py -3 -c "from app import app; from seed_data import sync_all_data; app.app_context().push(); sync_all_data()"
```

### Port Already in Use
If port 5000 is already in use, you can change it in `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change port here
```

### Missing Images
Make sure the `static/images/` directory contains restaurant images:
- `static/images/restaurants/` - Restaurant photos
- `static/images/header-bg.jpg` - Background image

---

## Project Structure

```
EXIT_TEST/
├── app.py                  # Main application (registers blueprints)
├── models.py               # Database models
├── blueprints/             # Modular routes (main, auth, customer, restaurant)
├── config.py               # Configuration
├── seed_data.py            # Seeding and idempotent sync helpers
├── setup_fresh.py          # Fresh setup/reset script
├── requirements.txt        # Python dependencies
├── static/                 # Static files (CSS, JS, images)
├── templates/              # HTML templates
└── instance/               # Database files (SQLite)
```

---

## Support

If you encounter any issues during setup, please check:
1. Python version (3.7+ recommended)
2. All dependencies are installed
3. Database permissions
4. File permissions for the instance directory
