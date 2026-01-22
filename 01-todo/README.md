# Django TODO App

A simple, modern TODO application built with Django and Vanilla CSS.

**Status:** ✅ Done

## Features

- **Manage Tasks**: Create, read, update, and delete (CRUD) tasks.
- **Task Details**: Add titles, descriptions, and due dates.
- **Status Tracking**: Mark tasks as resolved/completed.
- **Responsive Design**: Clean interface styled with Vanilla CSS.

## Prerequisites

- Python 3.12+
- `uv` (for package management)

## Setup

1. **Clone the repository** (if applicable) or navigate to the project folder:

    ```bash
    cd 01-todo
    ```

2. **Install dependencies**:

    ```bash
    uv sync
    ```

    Or manually:

    ```bash
    uv add django
    ```

3. **Apply migrations**:

    ```bash
    uv run python manage.py migrate
    ```

## Running the Application

Start the development server:

```bash
uv run python manage.py runserver
```

Access the app at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Running Tests

Run the automated test suite:

```bash
uv run python manage.py test todo_app
```

## Project Structure

- `todo_project/`: Main Django project configuration.
- `todo_app/`: The TODO application app.
  - `models.py`: Database models (`Todo`).
  - `views.py`: View logic for CRUD operations.
  - `urls.py`: URL routing for the app.
  - `templates/`: HTML templates (`base.html`, `home.html`, `update.html`).
  - `tests.py`: Automated tests.
