# Data Model: User Profile & Personal Settings

**Feature**: 003-personal-settings-i  
**Date**: 2025-10-06  
**Phase**: 1 (Design & Contracts)

## Entity: User (Extended)

### Overview
Extends the existing `User` model from Feature 001 (authentication) with profile-specific fields for bio, profile picture storage (base64), and concurrent edit detection.

### Schema Changes

**Table**: `user` (existing table, adding columns)

| Column Name | Type | Constraints | Description |
|-------------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Existing - user ID |
| `email` | VARCHAR(120) | UNIQUE, NOT NULL | Existing - user email (login) |
| `full_name` | VARCHAR(100) | NOT NULL | Existing - user's full name |
| `password_hash` | VARCHAR(255) | NOT NULL | Existing - bcrypt hash |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Existing - account creation |
| **`bio`** | **TEXT** | **NULLABLE** | **NEW** - User biography (0-500 chars) |
| **`profile_picture_data`** | **TEXT** | **NULLABLE** | **NEW** - Base64-encoded image data |
| **`profile_picture_mime_type`** | **VARCHAR(50)** | **NULLABLE** | **NEW** - MIME type (e.g., "image/jpeg") |
| **`updated_at`** | **DATETIME** | **DEFAULT CURRENT_TIMESTAMP, ON UPDATE CURRENT_TIMESTAMP** | **NEW** - Last profile update timestamp |

### Field Specifications

#### bio (NEW)
- **Type**: TEXT (SQLAlchemy: `db.Text`)
- **Nullable**: Yes (user may not have bio)
- **Validation**: 
  - Maximum 500 characters (enforced in logic layer)
  - XSS sanitization (strip harmful HTML, preserve newlines)
  - Optional: Linkify URLs (future enhancement)
- **Default**: NULL
- **Index**: Not indexed (not queried frequently)

#### profile_picture_data (NEW)
- **Type**: TEXT (SQLAlchemy: `db.Text`)
- **Nullable**: Yes (user may not have profile picture)
- **Storage Format**: Base64-encoded image bytes (e.g., `/9j/4AAQSkZJRgABAQAA...`)
- **Size**: Up to ~6.7MB (5MB original × 1.33 base64 overhead)
- **Validation**:
  - Validated as proper base64 string (can be decoded)
  - Original image validated by Pillow before encoding
- **Default**: NULL
- **Index**: Not indexed
- **Lazy Loading**: Use SQLAlchemy `deferred()` to exclude from default queries
- **Note**: Does NOT include data URI prefix (no `data:image/jpeg;base64,` - just the base64 data)

#### profile_picture_mime_type (NEW)
- **Type**: VARCHAR(50) (SQLAlchemy: `db.String(50)`)
- **Nullable**: Yes (NULL when no profile picture)
- **Allowed Values**: `image/jpeg`, `image/png`, `image/gif`
- **Validation**: Must be one of allowed MIME types
- **Default**: NULL
- **Index**: Not indexed
- **Purpose**: Enables proper `Content-Type` header when serving image, facilitates format-specific handling

#### updated_at (NEW)
- **Type**: DATETIME (SQLAlchemy: `db.DateTime`)
- **Nullable**: No
- **Default**: CURRENT_TIMESTAMP
- **Auto-Update**: Yes - automatically updates on any profile modification
- **Index**: Yes - required for efficient concurrent edit detection queries
- **Precision**: Second-level precision (sufficient for concurrent edit detection)
- **Timezone**: UTC (consistent with `created_at`)

### SQLAlchemy Model Definition

**File**: `src/models/user.py` (extend existing model)

```python
from datetime import datetime
from sqlalchemy import Text, String, DateTime
from sqlalchemy.orm import deferred
from src.models.base_model import BaseModel, db

class User(BaseModel):
    __tablename__ = 'user'
    
    # Existing fields from Feature 001
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # NEW fields for Feature 003
    bio = db.Column(db.Text, nullable=True)
    profile_picture_data = deferred(db.Column(db.Text, nullable=True))  # Lazy loaded
    profile_picture_mime_type = db.Column(db.String(50), nullable=True)
    updated_at = db.Column(
        db.DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
        nullable=False,
        index=True
    )
    
    def to_dict(self, include_picture=False):
        """
        Serialize user to dictionary.
        
        Args:
            include_picture: If True, include profile_picture_data (large)
        
        Returns:
            dict with user fields
        """
        data = {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'bio': self.bio,
            'profile_picture_mime_type': self.profile_picture_mime_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_picture:
            data['profile_picture_data'] = self.profile_picture_data
        
        return data
    
    def has_profile_picture(self):
        """Check if user has profile picture without loading it."""
        return self.profile_picture_data is not None
```

### Database Migration

**Migration File**: `migrations/003_add_user_profile_fields.sql` (or Alembic migration)

```sql
-- Add profile fields to user table
ALTER TABLE user ADD COLUMN bio TEXT NULL;
ALTER TABLE user ADD COLUMN profile_picture_data TEXT NULL;
ALTER TABLE user ADD COLUMN profile_picture_mime_type VARCHAR(50) NULL;
ALTER TABLE user ADD COLUMN updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- Create index for concurrent edit detection
CREATE INDEX idx_user_updated_at ON user(updated_at);

-- Add trigger to auto-update updated_at (SQLite version)
CREATE TRIGGER update_user_timestamp 
AFTER UPDATE ON user
FOR EACH ROW
BEGIN
    UPDATE user SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

**Rollback**:
```sql
DROP TRIGGER IF EXISTS update_user_timestamp;
DROP INDEX IF EXISTS idx_user_updated_at;
ALTER TABLE user DROP COLUMN updated_at;
ALTER TABLE user DROP COLUMN profile_picture_mime_type;
ALTER TABLE user DROP COLUMN profile_picture_data;
ALTER TABLE user DROP COLUMN bio;
```

### Relationships

**No New Relationships**: All profile data stored directly in `User` entity.

**Potential Future Enhancement**: 
- Separate `ProfileAuditLog` table for tracking changes (NFR-007 requirement)
- Structure: `id`, `user_id`, `field_name`, `old_value`, `new_value`, `changed_at`, `ip_address`
- Relationship: `User.audit_logs` (one-to-many)
- Deferred to future feature if audit requirements expand

### Data Lifecycle

#### Create (User Registration)
- **Existing**: `email`, `full_name`, `password_hash`, `created_at`
- **New Defaults**: `bio=NULL`, `profile_picture_data=NULL`, `profile_picture_mime_type=NULL`, `updated_at=CURRENT_TIMESTAMP`
- **Effect**: New users start with empty profile fields

#### Read (Profile Display)
- **Without Picture**: `SELECT id, email, full_name, bio, profile_picture_mime_type, updated_at FROM user WHERE id = ?`
- **With Picture**: `SELECT * FROM user WHERE id = ?` (or explicitly list all columns including profile_picture_data)
- **Lazy Loading**: Default queries exclude `profile_picture_data` to improve performance
- **Use Case**: Avatar display queries only `profile_picture_data` when needed

#### Update (Profile Edit)
- **Fields Updated**: Any of `full_name`, `email`, `bio`, `password_hash`, `profile_picture_data`, `profile_picture_mime_type`
- **Automatic**: `updated_at` timestamp refreshes on ANY update (trigger/ORM)
- **Concurrent Detection**: Compare `updated_at` before update, raise conflict if changed
- **Validation**: All validation in logic layer before model update

#### Delete (User Deletion)
- **Out of Scope**: User deletion not in Feature 003
- **Future Consideration**: CASCADE delete profile data when user account deleted

### Validation Rules

| Field | Rule | Enforced By |
|-------|------|-------------|
| `bio` | Max 500 characters | Logic layer |
| `bio` | XSS sanitization | Logic layer |
| `profile_picture_data` | Valid base64 | Logic layer |
| `profile_picture_data` | Max ~6.7MB | Logic layer (5MB pre-encoding) |
| `profile_picture_mime_type` | One of: `image/jpeg`, `image/png`, `image/gif` | Logic layer |
| `updated_at` | Not in future | Database (default constraint) |

### Performance Considerations

**Query Optimization**:
- Lazy load `profile_picture_data` (deferred column) - reduces query size by ~6MB per user
- Index on `updated_at` for concurrent edit checks
- Use `session.query(User).options(defer('profile_picture_data'))` for list views

**Storage Optimization**:
- Optional: Resize images to max 800x800px before encoding (reduces storage by 50-80%)
- Vacuum SQLite database periodically to reclaim space from deleted images

**Expected Storage Per User**:
- No profile picture: ~200 bytes (bio + metadata)
- With profile picture: ~200 bytes + ~6.7MB (worst case) = ~6.7MB
- Typical: ~2-3MB (JPEG compression effective)

### Security Considerations

**SQL Injection**: Prevented by SQLAlchemy parameterized queries (no raw SQL in logic layer)

**XSS Prevention**: 
- Sanitize `bio` input (strip `<script>` tags, preserve line breaks)
- Escape bio in templates using Jinja2 `{{ bio | e }}` or `| safe` after sanitization

**Image Security**:
- Validate with Pillow before encoding (rejects malformed images)
- Strip EXIF metadata to prevent privacy leaks
- MIME type validation prevents executable files

**Data Privacy**:
- Profile pictures may contain sensitive information (faces, locations)
- EXIF data (GPS coordinates, camera model) stripped before storage
- Consider future: user-controlled profile visibility settings

## Summary

**Changes**: 4 new columns added to existing `user` table  
**Migration Complexity**: Low (ALTER TABLE, no data transformation required)  
**Constitutional Compliance**: ✅ Models remain thin (schema only, no business logic)  
**Performance Impact**: Minimal (lazy loading prevents degradation)  
**Ready for**: Contract definition and test generation
