#!/usr/bin/env python3
"""
WSGI entry point for Deep-Live-Cam Web API
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from web_api import app

if __name__ == "__main__":
    # Get port from environment variable (for Railway) or use default
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🚀 Starting Deep-Live-Cam Web API via WSGI...")
    print(f"📋 Environment:")
    print(f"   PORT: {port}")
    print(f"   HOST: {host}")
    
    app.run(host=host, port=port, debug=False) 