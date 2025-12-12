#!/bin/bash
set -o

# backend
pip install -r requirements.txt
alembic upgrade head

# frontend
cd frontend
npm install
npm run build
