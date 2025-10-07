# Data Model: Frontend Landing Page System

## Entity Relationships

```
User (1) ←→ (0..n) CoatHanger
ContactMessage (standalone entity)
```

## User Entity

**Purpose**: Represents registered users with authentication credentials and profile information

**Attributes**:
- `id`: Integer, Primary Key, Auto-increment
- `email`: String(120), Unique, Not Null, Index
- `full_name`: String(100), Not Null
- `password_hash`: String(128), Not Null
- `created_at`: DateTime, Not Null, Default=UTC Now
- `updated_at`: DateTime, Not Null, Default=UTC Now, OnUpdate=UTC Now

**Validation Rules**:
- Email must be valid email format
- Email must be unique across all users
- Full name must be 2-100 characters
- Password must be minimum 8 characters before hashing
- All fields required except timestamps (auto-generated)

**Relationships**:
- One-to-many with CoatHanger (user can have multiple active sessions)

**Business Rules**:
- Email serves as unique username
- Password stored as bcrypt hash only
- Created/updated timestamps for audit trail
- Soft delete not implemented (hard delete for GDPR compliance)

## CoatHanger Entity

**Purpose**: Session tracking table for secure authentication management with automatic timeout

**Attributes**:
- `id`: Integer, Primary Key, Auto-increment
- `user_id`: Integer, Foreign Key to User.id, Not Null, Index
- `session_hash`: String(64), Unique, Not Null, Index
- `created_at`: DateTime, Not Null, Default=UTC Now
- `updated_at`: DateTime, Not Null, Default=UTC Now, OnUpdate=UTC Now
- `user_data`: JSON, Nullable (cached user information for performance)

**Validation Rules**:
- Session hash must be unique across all active sessions
- User ID must reference existing user
- Updated_at must be within 10 minutes of current time for active sessions
- Session hash must be 64-character hexadecimal string

**Relationships**:
- Many-to-one with User (multiple sessions per user allowed)

**Business Rules**:
- Session expires after 10 minutes of inactivity (updated_at + 10 minutes < now)
- Session hash generated using secure random + user ID + timestamp
- User_data field caches frequently accessed user information
- Automatic cleanup of expired sessions via background process

**State Transitions**:
1. **Created**: New session created on successful login
2. **Active**: Session updated_at refreshed on each authenticated request
3. **Expired**: Session older than 10 minutes, user redirected to login
4. **Deleted**: Explicit logout or cleanup process removes session

## ContactMessage Entity

**Purpose**: Stores messages submitted through contact form with delivery tracking

**Attributes**:
- `id`: Integer, Primary Key, Auto-increment
- `name`: String(100), Not Null
- `email`: String(120), Not Null
- `subject`: String(200), Not Null
- `message`: Text, Not Null
- `submitted_at`: DateTime, Not Null, Default=UTC Now
- `email_sent`: Boolean, Not Null, Default=False
- `email_sent_at`: DateTime, Nullable

**Validation Rules**:
- Name must be 2-100 characters
- Email must be valid email format
- Subject must be 5-200 characters
- Message must be 10-2000 characters
- All fields required except email tracking fields

**Relationships**:
- Standalone entity (no foreign key relationships)

**Business Rules**:
- Contact form submissions stored immediately
- Confirmation email sent asynchronously
- Email_sent flag prevents duplicate email sending
- Email_sent_at tracks delivery timestamp
- No user account required for contact form

## Database Indexes

**Performance Optimization**:
- `User.email` - Unique index for login lookups
- `CoatHanger.session_hash` - Unique index for session validation
- `CoatHanger.user_id` - Index for user session queries
- `CoatHanger.updated_at` - Index for session cleanup queries
- `ContactMessage.submitted_at` - Index for admin message browsing

## Migration Strategy

**Initial Migration**:
1. Create User table with indexes
2. Create CoatHanger table with foreign key constraint
3. Create ContactMessage table
4. Add database constraints and indexes

**Future Considerations**:
- User profile extensions (avatar, bio, preferences)
- Session device tracking (IP, user agent)
- Contact message categorization and status tracking
- User role/permission system for admin access

## Data Validation

**Client-Side Validation**:
- Email format validation
- Password strength requirements
- Form field length limits
- Required field highlighting

**Server-Side Validation**:
- SQLAlchemy model validation
- Custom validators for business rules
- Database constraint enforcement
- Input sanitization for XSS prevention

## Security Considerations

**Password Security**:
- Bcrypt hashing with cost factor 12
- No plaintext password storage
- Password complexity requirements

**Session Security**:
- Cryptographically secure session hash generation
- Session token rotation on privilege escalation
- Automatic session cleanup
- Session fixation protection

**Data Protection**:
- Input validation and sanitization
- SQL injection prevention via parameterized queries
- XSS protection in template rendering
- CSRF token validation for state-changing operations