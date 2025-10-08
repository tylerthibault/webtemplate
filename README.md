# Flask MVC Base Template

A Flask web application following strict MVC architecture with custom session-based authentication.

## Features

### Feature 003: User Profile & Personal Settings

Authenticated users can view and edit their profile information through a comprehensive settings page.

**Profile Fields:**
- **Full Name**: User's display name
- **Email Address**: Login credential (triggers notifications on change)
- **Bio/Description**: Up to 500 characters with XSS sanitization
- **Password**: With strength validation (8+ chars, uppercase, lowercase, digit)
- **Profile Picture**: JPEG/PNG/GIF format, max 5MB, stored as base64

**Key Features:**
- **Concurrent Edit Detection**: Optimistic locking using `updated_at` timestamps prevents data loss from simultaneous edits
- **Email Notifications**: Automatic emails sent to both old and new addresses when email changes
- **Client-Side Validation**: Real-time form validation with image preview and unsaved changes warning
- **Server-Side Validation**: Comprehensive validation with user-friendly error messages
- **CSRF Protection**: All state-changing operations protected against cross-site request forgery
- **Image Security**: Automatic EXIF stripping, format validation, size limits, and image sanitization
- **Session Management**: Custom "coat hanger" session system with 10-minute timeout

**API Routes:**
- `GET /settings` - Display personal settings page (authentication required)
- `POST /settings` - Update profile information (authentication + CSRF token required)

**Security Measures:**
- Base64 image storage with deferred loading for performance
- XSS prevention through input sanitization and template escaping
- Password hashing with bcrypt (cost factor 12)
- SQL injection prevention via SQLAlchemy ORM
- Secure session cookies (httponly, secure in production)
- Input validation on both client and server

**Dependencies:**
- `Pillow==11.3.0` - Image validation and processing
- `pytest==8.4.2` - Testing framework
- `pytest-flask==1.3.0` - Flask testing utilities

## Architecture

### MVC Pattern
- **Models** (`src/models/`): Thin SQLAlchemy models - database schema only
- **Logic** (`src/logic/`): Thick business logic layer - all application rules
- **Controllers** (`src/controllers/`): Thin routing layer - delegates to logic

### Technology Stack
- **Backend**: Flask 3.1.2 with SQLAlchemy ORM
- **Database**: SQLite (development), PostgreSQL-ready
- **Authentication**: Custom implementation with bcrypt password hashing
- **Frontend**: Bootstrap CSS/JS framework with Jinja2 templates
- **Testing**: pytest with >80% code coverage target

### Project Structure
```
src/
├── controllers/      # Flask blueprints - routing only
├── logic/           # Business rules, authentication, services
├── models/          # SQLAlchemy models - database schema
├── static/          # CSS, JavaScript, images
├── templates/       # Jinja2 templates with inheritance
└── utils/           # Utility functions and validators

specs/               # Feature specifications and planning
tests/               # Contract, unit, integration, and performance tests
migrations/          # Database migration scripts
```

## Development

### Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python run.py  # Auto-creates tables on first run
```

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/contract/ -v      # API contract tests
pytest tests/unit/ -v          # Unit tests
pytest tests/integration/ -v   # Integration tests
pytest tests/performance/ -v   # Performance tests

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Code Quality
```bash
# Format code with black
black src/ tests/

# Lint with flake8
flake8 src/ tests/
```

## Configuration

Environment variables (create `.env` file):
```
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///portfolio.db
EMAIL_ENABLED=false
SMTP_SERVER=localhost
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
FROM_EMAIL=noreply@example.com
```

## Contributing

1. Follow the MVC architecture strictly
2. Write tests before implementation (TDD)
3. Maintain constitutional principles (thin controllers, thick logic)
4. Use feature branches for new work
5. Ensure all tests pass before merging

## License

[Your License Here]
