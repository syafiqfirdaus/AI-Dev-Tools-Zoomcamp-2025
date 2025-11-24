# Homework Answers

## Question 1: Install Django

**Command used:** `uv add django` (or `pip install django`)

## Question 2: Project and App

**File to edit:** `settings.py` (specifically adding the app to `INSTALLED_APPS`)

## Question 3: Django Models

**Next step:** Run migrations
(Command: `python manage.py makemigrations` and `python manage.py migrate`)

## Question 4: TODO Logic

**Where to put logic:** `views.py`

## Question 5: Templates

**Where to register directory:** `TEMPLATES['DIRS']` in project's `settings.py`
*(Note: App-level templates in `todo_app/templates` are automatically discovered if `APP_DIRS` is True, but `DIRS` is where you explicitly register directories.)*

## Question 6: Tests

**Command to run tests:** `python manage.py test`
