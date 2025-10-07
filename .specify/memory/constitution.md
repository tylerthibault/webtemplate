<!--
SYNC IMPACT REPORT:
Version change: [NEW] → 1.0.0
Modified principles: [INITIAL CREATION]
Added sections: All core sections created
Removed sections: None
Templates requiring updates: 
  ✅ c:\Users\tyler\Documents\Coding\Flask\base_template\.specify\templates\plan-template.md (requires review)
  ✅ c:\Users\tyler\Documents\Coding\Flask\base_template\.specify\templates\spec-template.md (requires review)
  ✅ c:\Users\tyler\Documents\Coding\Flask\base_template\.specify\templates\tasks-template.md (requires review)
Follow-up TODOs: Review and align all template files with Flask MVC principles
-->

# Flask MVC Base Template Constitution

## Core Principles

### I. MVC Separation of Concerns
MUST maintain strict separation between Models, Views, and Controllers. Controllers handle routing and HTTP concerns only. Models manage database interactions and data validation. Logic layer contains all business rules and "heavy lifting" operations. Views (templates) handle presentation logic exclusively.

**Rationale**: Clear separation prevents tightly coupled code, improves testability, and ensures maintainable architecture as the application scales.

### II. Thin Controllers & Models
Controllers MUST be thin - only handling request/response flow, parameter validation, and delegation to logic layer. Models MUST be thin - only handling database schema, basic validation, and ORM concerns. ALL business logic MUST reside in the logic layer.

**Rationale**: Concentrating business logic in dedicated layer prevents duplication, improves reusability, and makes complex operations easier to test and maintain.

### III. Database Layer Standards
MUST use SQLite for development environment. MUST use SQLAlchemy as the ORM for all database interactions. Database models MUST inherit from a base model class. Migration scripts MUST be version controlled. Database connections MUST be properly managed and closed.

**Rationale**: Consistent ORM usage ensures portability, SQLite provides zero-config development environment, and proper connection management prevents resource leaks.

### IV. Template Inheritance
ALL HTML templates MUST extend from base templates in `templates/bases/`. Public pages extend `public.html`, authenticated pages extend `private.html`. Templates MUST use Jinja2 constructs for dynamic content. Template logic MUST be minimal - complex operations belong in logic layer.

**Rationale**: Template inheritance reduces duplication, ensures consistent styling/structure, and separates presentation from business logic.

### V. Static Asset Organization
CSS files MUST reside in `static/css/`. JavaScript files MUST reside in `static/script/`. Images MUST reside in `static/img/`. External assets are permitted only when internal organization is insufficient. Asset naming MUST be descriptive and follow kebab-case convention.

**Rationale**: Organized asset structure improves maintainability, enables efficient caching strategies, and simplifies asset management in production.

## Technology Stack Requirements

**Backend Framework**: Flask (latest stable version)
**Database**: SQLite (development), configurable for production
**ORM**: SQLAlchemy with Flask-SQLAlchemy extension
**Template Engine**: Jinja2 (Flask default)
**Asset Management**: Flask static file serving (development), CDN-ready for production
**Testing**: pytest for unit and integration tests
**Code Quality**: flake8 for linting, black for formatting

## Development Standards

**File Organization**: Follow established folder structure strictly. New folders require architectural justification.
**Code Style**: Follow PEP 8. Use black formatter. Maximum line length 88 characters.
**Documentation**: All public functions MUST have docstrings. Complex logic MUST include inline comments.
**Error Handling**: Use appropriate HTTP status codes. Log errors appropriately. Provide user-friendly error messages.
**Security**: Validate all inputs. Use parameterized queries. Implement CSRF protection. Secure session management.

## Governance

This constitution supersedes all other development practices. Amendments require documentation of rationale, impact assessment, and migration plan. All code reviews MUST verify compliance with these principles. Architectural decisions that deviate from these principles MUST be explicitly justified and documented.

**Version**: 1.0.0 | **Ratified**: 2025-10-05 | **Last Amended**: 2025-10-05