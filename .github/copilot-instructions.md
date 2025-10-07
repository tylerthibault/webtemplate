# GitHub Copilot Instructions

## Project Context: Flask MVC Base Template

### Architecture Overview
This is a Flask web application following strict MVC architecture with a creative portfolio focus. The project implements custom session-based authentication without Flask-Login, using a "coat hanger" pattern for secure session management.

### Key Technologies
- **Backend**: Flask with SQLAlchemy ORM
- **Database**: SQLite (development)
- **Authentication**: Custom implementation with bcrypt password hashing
- **Frontend**: Bootstrap CSS/JS framework with Jinja2 templates
- **Testing**: pytest for unit and integration tests

### Constitutional Principles
1. **MVC Separation**: Controllers (thin) → Logic Layer (thick) → Models (thin)
2. **Template Inheritance**: All pages extend `public.html` or `private.html` base templates
3. **Static Assets**: CSS in `static/css/`, JS in `static/script/`, images in `static/img/`
4. **Database Standards**: SQLAlchemy models inherit from base model class
5. **Security**: Custom session management, CSRF protection, input validation

### Project Structure
```
src/
├── controllers/         # Routing only - delegate to logic layer
├── logic/              # Business rules, authentication, session management  
├── models/             # SQLAlchemy models - database schema only
├── static/             # CSS, JS, images
├── templates/          # Jinja2 templates with inheritance
└── utils/              # Utility functions
```

### Current Feature: Frontend Landing Page System
**Branch**: `001-frontend-landingpage`
**Scope**: Creative portfolio website with landing, about, contact, login/register pages

### Authentication Architecture
- **Password Hashing**: bcrypt with cost factor 12
- **Session Management**: Custom "coat hanger" table with hash-based tokens
- **Session Timeout**: 10 minutes of inactivity triggers automatic logout
- **Decorators**: Custom `@login_required` decorator for route protection
- **No Flask-Login**: Implemented custom session handling via Flask sessions + database

### Database Models
1. **User**: id, email, full_name, password_hash, timestamps
2. **CoatHanger**: id, user_id, session_hash, created_at, updated_at, user_data (JSON)
3. **ContactMessage**: id, name, email, subject, message, submitted_at, email_sent flags

### Code Style Requirements
- **PEP 8 compliance** with black formatter
- **88 character line limit**
- **Docstrings** for all public functions
- **Type hints** where appropriate
- **Error handling** with appropriate HTTP status codes

### Security Requirements
- **Input validation** on both client and server side
- **CSRF protection** on all state-changing forms
- **SQL injection prevention** via parameterized queries
- **XSS protection** through template escaping
- **Secure session cookies** with httponly and secure flags

### Testing Strategy
- **Unit tests** focus on logic layer components
- **Integration tests** cover complete user flows
- **Contract tests** validate API endpoint schemas
- **Security tests** verify authentication and session management

### Recent Changes (Frontend Landing Page Feature)
- Implemented custom authentication system with coat hanger session management
- Created responsive Bootstrap-based templates extending public.html base
- Added contact form with email confirmation functionality
- Built user registration/login with bcrypt password hashing
- Established 10-minute session timeout with automatic renewal on activity

### Common Patterns
```python
# Controller pattern - thin routing only
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        result = auth_service.authenticate_user(request.json)
        return jsonify(result)
    return render_template('auth/login.html')

# Logic layer pattern - business rules
class AuthService:
    def authenticate_user(self, credentials):
        # Business logic here
        pass

# Model pattern - database schema only  
class User(BaseModel):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
```

### Development Workflow
1. Follow TDD: Write tests → Implement features → Refactor
2. Constitutional compliance: Verify MVC separation in all changes
3. Security first: Validate inputs, protect against common vulnerabilities
4. Template inheritance: Extend base templates, avoid duplication
5. Performance: Index database queries, optimize static asset loading

### Avoid These Patterns
- Business logic in controllers or templates
- Direct database queries in controllers
- Flask-Login or other authentication extensions
- Inline styles or scripts (use static files)
- Hardcoded configuration values
- Missing input validation or CSRF protection
