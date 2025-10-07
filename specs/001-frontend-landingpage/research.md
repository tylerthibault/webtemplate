# Research: Frontend Landing Page System

## Custom Flask Session Management Patterns

**Decision**: Implement custom session management using Flask's built-in session object with server-side token tracking

**Rationale**: 
- Provides more control over session lifecycle compared to Flask-Login
- Allows implementation of custom timeout logic (10-minute automatic logout)
- Separates authentication concerns from Flask extensions for better testability
- Maintains constitutional requirement for custom business logic in logic layer

**Alternatives considered**: 
- Flask-Login: Rejected to maintain custom control over session management
- JWT tokens: Rejected as sessions are simpler for this use case and don't require token refresh logic
- Redis sessions: Overkill for SQLite-based development environment

## bcrypt Password Hashing Best Practices

**Decision**: Use bcrypt with cost factor 12 for password hashing

**Rationale**:
- Industry standard for password hashing with built-in salt generation
- Adaptive cost factor provides future-proofing against hardware improvements
- Cost factor 12 provides good security/performance balance for web applications
- Python bcrypt library is well-maintained and constitutional compliant

**Alternatives considered**:
- PBKDF2: Bcrypt preferred for its adaptive cost factor
- Argon2: Bcrypt chosen for simpler integration and broader ecosystem support
- SHA256 with salt: Rejected as bcrypt provides superior protection against rainbow table attacks

## SQLite Session Table Design Patterns

**Decision**: Implement "coat hanger" table with hash-based session tokens and timestamp-based expiration

**Rationale**:
- Separates session data from user credentials for security
- Hash-based tokens prevent session hijacking through predictable IDs
- Timestamp-based expiration allows automatic cleanup and timeout enforcement
- Follows SQLAlchemy patterns for ORM integration

**Table Schema**:
```sql
coat_hanger (
    id: Primary Key
    user_id: Foreign Key to users table
    session_hash: Unique token stored in user session
    created_at: Session creation timestamp
    updated_at: Last activity timestamp (for 10-minute timeout)
    user_data: JSON field for caching user information
)
```

**Alternatives considered**:
- Storing session data directly in Flask session: Rejected for security and scalability concerns
- External session store (Redis): Overkill for development environment
- Database session table without hash tokens: Rejected for security reasons

## Bootstrap Integration with Flask Templates

**Decision**: Include Bootstrap CSS/JS via static files with template inheritance

**Rationale**:
- Bootstrap files already placed in static folders per constitutional requirements
- Template inheritance ensures consistent styling across all pages
- Local static files provide better performance and offline development capability
- Follows established asset organization patterns

**Implementation Pattern**:
- Include Bootstrap CSS/JS in base templates (public.html)
- Override Bootstrap styles with custom CSS in main.css
- Use Bootstrap grid system for responsive design
- Implement Bootstrap form components for consistent UX

**Alternatives considered**:
- CDN-hosted Bootstrap: Rejected for development environment to ensure offline capability
- Custom CSS framework: Rejected as Bootstrap is already integrated per user requirements
- CSS preprocessors: Deferred as unnecessary complexity for current scope

## Custom Authentication Decorators Implementation

**Decision**: Create custom decorators for route protection with session validation

**Rationale**:
- Provides fine-grained control over authentication logic
- Integrates seamlessly with coat hanger session management
- Allows custom redirect logic and error handling
- Maintains thin controller pattern by delegating logic to service layer

**Decorator Pattern**:
```python
@login_required
def protected_route():
    # Route logic here
    pass
```

**Implementation Strategy**:
- Decorator checks session for valid hash token
- Validates token against coat hanger table
- Updates timestamp for session renewal
- Redirects to login page for invalid/expired sessions
- Provides user context to protected routes

**Alternatives considered**:
- Flask-Login decorators: Rejected to maintain custom control
- Middleware-based authentication: Decorator pattern preferred for explicitness
- Route-level session checks: Decorators provide better code reuse

## Security Considerations

**CSRF Protection**: Implement custom CSRF tokens using Flask sessions instead of Flask-WTF
**Input Validation**: Validate all form inputs on both client and server side using custom validation functions
**SQL Injection Prevention**: Use SQLAlchemy parameterized queries exclusively
**Session Security**: Implement secure session cookies with httponly and secure flags
**Password Requirements**: Enforce minimum password length and complexity

## Performance Considerations

**Database Indexing**: Add indexes on coat_hanger.session_hash and coat_hanger.user_id
**Session Cleanup**: Implement automatic cleanup of expired sessions
**Query Optimization**: Use SQLAlchemy lazy loading and relationship optimization
**Static Asset Caching**: Configure appropriate cache headers for CSS/JS files

## Testing Strategy

**Unit Tests**: Focus on logic layer components (authentication, session management)
**Integration Tests**: Test complete user flows (registration, login, session timeout)
**Contract Tests**: Validate API endpoints match expected request/response patterns
**Security Tests**: Verify password hashing, session management, and CSRF protection