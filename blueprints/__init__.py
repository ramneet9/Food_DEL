"""
Application blueprints package.

This module exposes the four blueprints used by the app:
- main_bp
- auth_bp
- customer_bp
- restaurant_bp
"""

from .main import main_bp  # noqa: F401
from .auth import auth_bp  # noqa: F401
from .customer import customer_bp  # noqa: F401
from .restaurant import restaurant_bp  # noqa: F401


