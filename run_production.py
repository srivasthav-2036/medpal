#!/usr/bin/env python3
"""
Production runner script for MedPal Flask application.
This script can be used to run the application in production mode.
"""

import os
import sys
from app import app, initialize_database

def main():
    """Run the application in production mode."""
    # Initialize database
    initialize_database()
    
    # Set production environment variables
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = 'False'
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=False,
        threaded=True
    )

if __name__ == '__main__':
    main()
