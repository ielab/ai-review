#!/bin/bash
# Navigate to the Django application directory
cd /app/backend/src;

# Migrations table
echo "Migrations tables...";
python manage.py migrate;
sleep 2;

# Finally, start the daphne server
echo "Starting daphne server...";
daphne ai_review.asgi:application -b 0.0.0.0 -p 8000;