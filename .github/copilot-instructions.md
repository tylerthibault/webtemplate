# GitHub Copilot Instructions

## Project Context: Flask MVC Base Template

### Architecture Overview
This is a Flask web application base template following strict MVC architecture. The project implements custom session-based authentication without Flask-Login, using a "coat hanger" pattern for secure session management.

### Key Technologies
- **Backend**: Flask with SQLAlchemy ORM
- **Database**: SQLite (development)
- **Authentication**: Custom implementation with bcrypt password hashing
- **Frontend**: Bootstrap CSS/JS framework with Jinja2 templates
- **Testing**: pytest for unit and integration tests

### Constitutional Principles
1. **MVC Separation**: Controllers (thin) → Logic Layer (thick) → Models (thin)
2. **Template Inheritance**: All pages extend `public.html` or `private.html` base templates
3. **Static Assets**: CSS in `static/css/`, JS in `static/js/`, images in `static/img/`
4. **Database Standards**: SQLAlchemy models inherit from `BaseModel` class
5. **Security**: Custom session management, CSRF protection, input validation

### Project Structure
```
src/
├── controllers/         # Routing only - delegate to logic layer
├── logic/              # Business rules, authentication, session management
├── models/             # SQLAlchemy models - database schema only
├── static/             # CSS, JS, images
├── templates/          # Jinja2 templates with inheritance
│   ├── bases/          # Base templates (public.html, private.html)
│   ├── public/         # Unauthenticated pages
│   └── private/        # Authenticated pages
└── utils/              # Utility functions
```

### Development Workflow

#### Starting the Application
```bash
# From project root
python run.py
```

#### Application Factory Pattern
- Flask app created via `create_app()` function in `src/__init__.py`
- Configuration via environment variables or defaults
- Database initialization with `db.create_all()` in app context

#### Authentication Architecture
- **Password Hashing**: bcrypt with cost factor 12
- **Session Management**: Custom "coat hanger" table with hash-based tokens
- **Session Timeout**: 10 minutes of inactivity triggers automatic logout
- **Decorators**: Custom `@login_required` decorator for route protection
- **No Flask-Login**: Implemented custom session handling via Flask sessions + database

### Code Patterns

#### Controller Pattern (Thin Controllers)
```python
# Controllers handle routing only - delegate to logic layer
@main_bp.route('/dashboard')
@login_required
def dashboard():
    user_data = user_service.get_user_dashboard_data(current_user_id)
    return render_template('private/dashboard/index.html', **user_data)
```

#### Logic Layer Pattern (Business Rules)
```python
# Logic layer contains business rules and service methods
class AuthService:
    @staticmethod
    def authenticate_user(credentials):
        # Validation, password checking, session creation
        pass
```

#### Model Pattern (Database Schema Only)
```python
# Models inherit from BaseModel and define schema only
class User(BaseModel):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
```

#### Template Structure
- **Base Templates**: `bases/public.html` (unauthenticated), `bases/private.html` (authenticated)
- **Component System**: Reusable components in `00_*_components/` directories
- **Page Templates**: Extend base templates, inherit navigation and layout

### Database Models
1. **User**: id, email, full_name, password_hash, timestamps
2. **CoatHanger**: id, user_id, session_hash, created_at, updated_at, user_data (JSON)
3. **ContactMessage**: id, name, email, subject, message, submitted_at, email_sent flags

### Security Requirements
- **Input validation** on both client and server side
- **CSRF protection** on all state-changing forms via custom utils
- **SQL injection prevention** via SQLAlchemy parameterized queries
- **XSS protection** through Jinja2 template auto-escaping
- **Secure session cookies** with httponly and secure flags

### Testing Strategy
- **Unit tests**: Focus on logic layer components (`tests/unit/`)
- **Integration tests**: Complete user flows (`tests/integration/`)
- **Contract tests**: API endpoint schemas (`tests/contract/`)
- **Performance tests**: Load testing (`tests/performance/`)

### Code Style Requirements
- **PEP 8 compliance** with 88 character line limit
- **Docstrings** for all public functions
- **Type hints** where appropriate
- **Error handling** with appropriate HTTP status codes

### Branch Naming Convention
- Feature branches: `###-feature-description` (e.g., `004-user-roles-and`)
- Use descriptive names for clarity in git history

### Common Dependencies
```python
# Core Flask dependencies
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from src import db
from src.logic.decorators import login_required
from src.utils.csrf_utils import generate_csrf_token
```

### Configuration Management
- Environment variables via `python-dotenv`
- Session timeout: 10 minutes (600 seconds)
- Database: SQLite for development, configurable for production
- Email configuration for contact forms and notifications

### Avoid These Patterns
- Business logic in controllers or templates
- Direct database queries in controllers
- Flask-Login or other authentication extensions (use custom implementation)
- Inline styles or scripts (use static files)
- Hardcoded configuration values
- Missing input validation or CSRF protection
- Deep nesting in template inheritance (max 3 levels)

### When Adding New Features
1. **Follow TDD**: Write tests → Implement features → Refactor
2. **MVC Compliance**: Ensure controllers remain thin, logic layer handles business rules
3. **Security First**: Validate inputs, protect against common vulnerabilities
4. **Template Inheritance**: Extend appropriate base templates
5. **Database Migrations**: Update models and handle schema changes properly