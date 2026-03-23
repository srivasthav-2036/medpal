#!/usr/bin/env python3
"""
Development runner for MedPal Flask application.
This script runs the app in development mode with optimized settings to prevent
frequent restarts caused by AI library file changes.
"""

import os
import sys
from app import app, initialize_database

def main():
    """Run the application in development mode with optimized settings."""
    # Initialize database
    initialize_database()
    
    # Set development environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = 'True'
    
    print("🚀 Starting MedPal in development mode...")
    print("📝 Debug mode: ON")
    print("🔄 Auto-reload: DISABLED (to prevent AI library restarts)")
    print("🌐 Server: http://127.0.0.1:5000")
    print("=" * 50)
    
    # Run with optimized settings
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=False,  # Prevents restarts from AI library file changes
        threaded=True
    )

if __name__ == '__main__':
    main()
