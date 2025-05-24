#!/bin/bash

# Stop on error
set -e

echo "🔧 Creating virtual environment at backend/venv ..."
python3 -m venv backend/venv

echo "📦 Activating virtual environment ..."
source backend/venv/bin/activate

echo "⬆️ Upgrading pip ..."
pip install --upgrade pip

echo "📂 Installing dependencies from backend/requirements.txt ..."
pip install -r backend/requirements.txt

echo "✅ Validating import of backend.app ..."
python -c "import backend.app; print('OK')"

echo "🚀 Starting backend server ..."
# Adjust if different entry point or port
FLASK_APP=backend/app.py FLASK_ENV=development flask run &
BACKEND_PID=$!

echo "🌐 Starting frontend server ..."
cd frontend
# Use npm or yarn depending on your setup
if [ -f package-lock.json ]; then
  npm install
  npm run dev &
else
  yarn install
  yarn dev &
fi
cd ..

echo "✅ Both backend (PID: $BACKEND_PID) and frontend are running."