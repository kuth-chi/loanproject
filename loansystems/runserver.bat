@echo off

rem Set the path to your Python environment activate script
set ENV_SCRIPT="venv\Scripts\activate.bat"

rem Activate the Python environment
call %ENV_SCRIPT%

rem Check and install libraries to environment
pip install -r requirements.txt

rem Check if db.sqlite3 exists, if not create it
if not exist db.sqlite3 (
    echo Creating db.sqlite3...
    python manage.py migrate
)

rem Check if superuser with username "admin" exists, if not create one
python manage.py shell -c "from django.contrib.auth.models import User; from usermanager.models import Company, OwnerLogo; user = User.objects.create_superuser('admin', 'lms@example.com', 'admin') if not User.objects.filter(username='admin').exists() else User.objects.get(username='admin'); company, created = Company.objects.get_or_create(id=1, owner=user, defaults={'name': 'My Company', 'short_name': 'MC', 'founder': 'admin', 'founded': '2023-04-11'}); OwnerLogo.objects.get_or_create(user=user, logo='default_owner_logo.png')"


rem Run Makemigrations development server command
python manage.py makemigrations

python manage.py migrate

rem Run the Django development server command
python manage.py runserver 0.0.0.0:8000

rem Deactivate the Python environment
deactivate
