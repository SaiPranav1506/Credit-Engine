#!/usr/bin/env python3
"""
Script to run the Credit Engine API server
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("Starting Credit Engine API Server...")
    print("Make sure your virtual environment is activated!")
    print("API will be available at: http://localhost:5000")
    print("Frontend will be available at: http://localhost:3000")
    print("")

    # Import and run Flask app
    from api import app
    app.run(debug=True, port=5000, host='0.0.0.0')

if __name__ == "__main__":
    main()