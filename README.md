# JustEat Technology - Food Ordering Web Application

A comprehensive food ordering web application built with Flask, featuring role-based authentication for customers and restaurant owners.

## 🚀 Quick Setup

### For New Devices:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run setup script
python setup.py

# 3. Start the application
python app.py
```

**Demo Accounts:**
- **Customers:** `ramneet` / `ramneet`, `batman` / `batman`
- **Restaurant Owners:** `chef_mario` / `mario`, `chef_raj` / `raj`

For detailed setup instructions, see [SETUP.md](SETUP.md)

## Features

### Common Functionality
- **Authentication System**: Role-based login for customers and restaurant owners
- **Password Reset**: Secure password reset functionality
- **Responsive Design**: Modern, mobile-friendly UI with Bootstrap 5
- **Toast Notifications**: Real-time feedback for user actions
- **Error Handling**: Comprehensive error handling with custom error pages

### Customer Features
- **Restaurant Discovery**: Browse and search restaurants by location, cuisine, or name
- **Menu Browsing**: View detailed menus with filters for cuisine type, price, and dietary restrictions
- **Shopping Cart**: Add items to cart with quantity selection
- **Order Management**: Place orders and track order status
- **Order History**: View past orders with search functionality
- **Profile Management**: Update personal information and preferences
- **Smart Recommendations**: Personalized recommendations based on order history and preferences
- **Dietary Preferences**: Support for vegetarian, vegan, and gluten-free options

### Restaurant Owner Features
- **Restaurant Registration**: Add and manage multiple restaurants
- **Menu Management**: Add, edit, and delete menu items
- **Order Processing**: Manage and update order status
- **Special Items**: Highlight today's special and deal of the day items
- **Analytics**: View order statistics and popular items
- **Automatic Tags**: "Mostly Ordered" tag for items ordered more than 10 times daily

### Bonus Features
- **Reviews & Ratings**: Customer reviews and ratings for restaurants and menu items
- **Customer Feedback**: Feedback system for continuous improvement

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: Jinja2 Templates, Bootstrap 5, JavaScript
- **Database**: SQLAlchemy with SQLite
- **Authentication**: Flask-Login
- **Styling**: Bootstrap 5, Font Awesome, Custom CSS
- **Testing**: Python unittest

## Database Schema

### Core Tables
- **users**: Customer and restaurant owner accounts
- **restaurants**: Restaurant information and details
- **menu_items**: Menu items with pricing and dietary information
- **orders**: Customer orders with status tracking
- **order_items**: Individual items within orders
- **cart**: Shopping cart items
- **user_preferences**: Customer preferences and dietary restrictions
- **reviews**: Customer reviews and ratings

### Key Relationships
- Users can own multiple restaurants (one-to-many)
- Restaurants have multiple menu items (one-to-many)
- Orders contain multiple order items (one-to-many)
- Users can have multiple preferences (one-to-many)
- Users can write multiple reviews (one-to-many)

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd food-ordering-app
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///food_ordering.db
```

### Step 5: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Demo Accounts

See the demo accounts listed at the top of this README under Quick Setup.

If you updated `seed_data.py` and want to sync changes into an existing DB, run:
```bash
py -3 -c "from app import app; from seed_data import sync_all_data; app.app_context().push(); sync_all_data()"
```

## Testing

Run the test suite:
```bash
python tests.py
```

The test suite includes:
- Model functionality tests
- Authentication tests
- Route tests
- Database relationship tests
- Form validation tests

## Project Structure

```
food-ordering-app/
├── app.py                  # Main Flask application (registers blueprints)
├── models.py               # Database models
├── blueprints/             # Modular route groups
│   ├── __init__.py         # Exports main/auth/customer/restaurant blueprints
│   ├── main.py             # Public home routes
│   ├── auth.py             # Authentication routes
│   ├── customer.py         # Customer routes & APIs
│   └── restaurant.py       # Restaurant owner routes & APIs
├── seed_data.py            # Database seeding and idempotent sync
├── tests.py                # Unit tests
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── README_VIVA.md          # Viva/demo cheat sheet
├── README_DEEP_DIVE.md     # In-depth architecture guide
├── templates/              # Jinja2 templates
│   ├── base.html           # Base template
│   ├── index.html          # Home page
│   ├── auth/               # Authentication templates
│   ├── customer/           # Customer templates
│   ├── restaurant/         # Restaurant owner templates
│   └── errors/             # Error pages
└── static/                 # Static files
    ├── css/                # Stylesheets
    ├── js/                 # JavaScript files
    └── images/             # Images
```

## Key Features Implementation

### Authentication & Authorization
- Role-based access control (Customer vs Restaurant Owner)
- Secure password hashing with Werkzeug
- Session management with Flask-Login
- Protected routes with decorators

### Database Design
- Normalized database schema
- Foreign key relationships
- Indexes for performance
- Cascade deletes for data integrity

### User Experience
- Responsive design for all devices
- Real-time cart updates
- Toast notifications for feedback
- Loading states for async operations
- Form validation and error handling

### Business Logic
- Smart recommendation algorithm
- Order status workflow
- Inventory management
- Pricing calculations
- Dietary restriction filtering

## API Endpoints

### Authentication
- `GET /auth/login` - Login page
- `POST /auth/login` - Process login
- `GET /auth/logout` - Logout user
- `GET /auth/reset-password` - Password reset page

### Customer Routes
- `GET /customer/dashboard` - Customer dashboard
- `GET /customer/restaurants` - Browse restaurants
- `GET /customer/restaurant/<id>` - Restaurant details
- `POST /customer/add-to-cart` - Add item to cart
- `GET /customer/cart` - View cart
- `POST /customer/place-order` - Place order
- `GET /customer/orders` - Order history

### Restaurant Routes
- `GET /restaurant/dashboard` - Restaurant dashboard
- `GET /restaurant/restaurants` - Manage restaurants
- `POST /restaurant/add-restaurant` - Add restaurant
- `GET /restaurant/restaurant/<id>/menu` - Menu management
- `POST /restaurant/add-menu-item` - Add menu item
- `GET /restaurant/orders` - Manage orders

## Security Features

- Password hashing with salt
- CSRF protection
- SQL injection prevention
- XSS protection
- Input validation and sanitization
- Secure session management

## Performance Optimizations

- Database query optimization
- Pagination for large datasets
- Lazy loading of relationships
- Efficient filtering and searching
- Caching of frequently accessed data

## Future Enhancements

- Payment integration
- Real-time order tracking
- Push notifications
- Advanced analytics dashboard
- Mobile app development
- Multi-language support
- Advanced recommendation engine

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.

---

**Note**: This application is for educational purposes and demonstrates modern web development practices with Flask, SQLAlchemy, and responsive design principles.
