#!/usr/bin/env python3
"""
WSGI entry point for the MedPal Flask application.
This file is used for production deployment with WSGI servers like Gunicorn, uWSGI, etc.
"""

import os
import sys
from app import app, initialize_database

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Initialize database on startup
initialize_database()

# WSGI application object
application = app

if __name__ == "__main__":
    # This allows running the WSGI file directly for testing
    app.run(host='0.0.0.0', port=5000, debug=False)
