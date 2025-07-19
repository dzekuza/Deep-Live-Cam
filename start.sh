#!/bin/bash

echo "🚀 Starting Deep-Live-Cam Web API..."

# Check if we're in a production environment
if [ -n "$PORT" ]; then
    echo "📋 Production environment detected"
    echo "   PORT: $PORT"
    echo "   HOST: ${HOST:-0.0.0.0}"
    
    # Try to use gunicorn if available
    if command -v gunicorn &> /dev/null; then
        echo "🐳 Using Gunicorn server"
        exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --keep-alive 2 web_api:app
    else
        echo "🐍 Using Flask development server"
        exec python3 web_api.py
    fi
else
    echo "🐍 Development environment - using Flask server"
    exec python3 web_api.py
fi 