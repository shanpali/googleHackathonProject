#!/bin/bash
# Build script for flask-backend
set -e

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
fi

# Export environment variables from .env if exists
if [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Run database migrations (if any)
# echo "No DB migrations configured. Add Alembic or Flask-Migrate if needed."

# Build complete
echo "Build complete. To run: source venv/bin/activate && python app.py"
