web: python manage.py migrate && python manage.py seed_admin && gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 2
