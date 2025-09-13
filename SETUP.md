# 🍕 Food Ordering Application - Setup Guide

## Quick Setup (Recommended)

### Option A: Fresh Install (New Device)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run fresh setup script
python setup_fresh.py

# 3. Start the application
python app.py
```

### Option B: Interactive Setup (Existing Device)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run interactive setup script
python setup.py

# 3. Start the application
python app.py
```

The application will be available at: `http://localhost:5000`

---

## Manual Setup (Alternative)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file in the project root:
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/food_ordering.db
```

### 3. Initialize Database
```bash
# Create database tables
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 4. Seed Database
```bash
python seed_data.py
```

### 5. Start Application
```bash
python app.py
```

---

## Demo Accounts

After setup, you can use these demo accounts:

### Customer Account
- **Username:** `john_doe`
- **Password:** `password123`

### Restaurant Owner Account
- **Username:** `chef_mario`
- **Password:** `password123`

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
If you encounter database issues, you can reset the database:
```bash
python setup.py
# Choose 'y' when prompted to reset
```

### Port Already in Use
If port 5000 is already in use, you can change it in `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change port here
```

### Missing Images
Make sure the `static/images/` directory contains all the restaurant images:
- `static/images/restaurants/` - Restaurant photos
- `static/images/header-bg.jpg` - Background image

---

## Project Structure

```
EXIT_TEST/
├── app.py                 # Main application file
├── models.py              # Database models
├── routes.py              # Application routes
├── config.py              # Configuration
├── seed_data.py           # Database seeding
├── setup.py               # Setup script
├── requirements.txt       # Python dependencies
├── static/                # Static files (CSS, JS, images)
├── templates/             # HTML templates
└── instance/              # Database files
```

---

## Support

If you encounter any issues during setup, please check:
1. Python version (3.7+ recommended)
2. All dependencies are installed
3. Database permissions
4. File permissions for the instance directory
