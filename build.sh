#!/bin/bash
set -e

echo ">>> Building React frontend..."
cd frontend
npm install
npm run build
cd ..

echo ">>> Copying build into backend/static..."
rm -rf backend/static
cp -r frontend/dist backend/static

echo ">>> Installing Python dependencies..."
cd backend
pip install -r requirements.txt

echo ">>> Build complete!"
