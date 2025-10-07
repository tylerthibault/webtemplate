# Research: User Profile & Personal Settings

**Feature**: 003-personal-settings-i  
**Date**: 2025-10-06  
**Phase**: 0 (Research & Technical Discovery)

## Research Questions

### 1. Base64 Image Storage in SQLite

**Question**: What are the best practices, limitations, and performance implications of storing base64-encoded images in SQLite TEXT columns?

**Research Findings**:
- **SQLite TEXT Column Capacity**: SQLite TEXT columns can store up to 1GB (default max), sufficient for base64-encoded 5MB images (~6.7MB after encoding)
- **Base64 Overhead**: Base64 encoding increases size by ~33% (5MB → ~6.7MB)
- **Performance Considerations**:
  - Reading base64 TEXT is fast for single-user profile queries
  - Should use lazy loading (exclude `profile_picture_data` from SELECT unless needed)
  - Consider separate query for profile picture only when rendering avatar
- **Python Base64 Module**: Standard library `base64.b64encode()` and `b64decode()` are sufficient, no external dependencies
- **Query Optimization**: Use `defer('profile_picture_data')` in SQLAlchemy to exclude from default queries

**Decision**: Store images as base64-encoded TEXT in `User.profile_picture_data` column using Python's standard `base64` module. Implement lazy loading via SQLAlchemy's `deferred` columns.

**Rationale**: 
- Meets user requirement (no file system storage)
- SQLite TEXT capacity sufficient for 5MB limit
- Standard library solution (no dependencies)
- Lazy loading prevents performance degradation

**Alternatives Considered**:
- **File system storage**: Rejected per user requirement
- **BLOB datatype**: Base64 TEXT is more portable and easier to inspect/debug
- **External storage (S3, CDN)**: Overkill for MVP, adds complexity

### 2. Image Validation & Security

**Question**: How can we securely validate and sanitize user-uploaded images to prevent malicious files?

**Research Findings**:
- **Pillow Library**: Industry-standard Python image library, validates images by attempting to parse headers
- **Magic Number Validation**: Pillow's `Image.open()` checks file signature (magic bytes), rejects non-image files
- **MIME Type Detection**: Use `imghdr` module or Pillow to detect actual MIME type (vs trusting file extension)
- **EXIF Data Privacy**: Strip EXIF metadata (location, camera data) using `Image.getexif()` to protect user privacy
- **Size Validation**: Validate both pre-encoding file size and post-encoding base64 length
- **Format Restrictions**: Limit to JPEG, PNG, GIF (common formats, well-supported by Pillow)

**Decision**: 
1. Validate file type using Pillow `Image.open()` (rejects invalid images)
2. Enforce 5MB pre-encoding file size limit
3. Strip EXIF metadata for privacy
4. Store detected MIME type in `profile_picture_mime_type` column
5. Optional: Resize images > 1MB to 800x800px to reduce storage

**Rationale**:
- Pillow parsing validates image structure (detects malware disguised as images)
- EXIF stripping protects user privacy
- Size limit prevents abuse
- MIME type storage enables proper `Content-Type` headers when serving images

**Alternatives Considered**:
- **Extension-only validation**: Insecure (easily spoofed by attackers)
- **Antivirus scanning**: Overkill for MVP, requires external service
- **Allow all formats**: JPEG/PNG/GIF covers 99% of use cases, reduces attack surface

**Dependencies**:
```python
# requirements.txt
Pillow==10.0.0  # Image validation and processing
```

### 3. Concurrent Edit Detection

**Question**: What is the most effective pattern for detecting and resolving concurrent edits to user profiles?

**Research Findings**:
- **Optimistic Locking**: Assume conflicts are rare, detect on save using version/timestamp comparison
- **Pessimistic Locking**: Lock record during edit (prevents conflicts but complex for web apps)
- **Timestamp-Based**: Compare `updated_at` timestamp from form submission with current database value
- **Version Number**: Integer version column incremented on each save (functionally similar to timestamp)
- **HTTP 409 Conflict**: Standard status code for concurrent modification errors
- **Conflict Resolution UI**: Show user which fields changed, options to reload or force overwrite

**Decision**: Implement optimistic locking using `updated_at` timestamp:
1. Add `updated_at TIMESTAMP` column to User model (auto-updates on save)
2. Include `updated_at` in GET /settings response (hidden field in form)
3. On POST /settings, compare submitted `updated_at` with current database value
4. If mismatch: return 409 Conflict with current user data
5. Client displays conflict UI with changed fields, reload/overwrite options

**Rationale**:
- Profile edits are infrequent (conflicts unlikely), optimistic locking appropriate
- Timestamp comparison is simple and reliable
- 409 status code is semantically correct
- Gives user control over conflict resolution

**Alternatives Considered**:
- **Pessimistic locking**: Unnecessary complexity, poor UX (locks expire, user gets locked out)
- **Version number**: Functionally equivalent to timestamp but requires manual increment logic
- **Last-write-wins**: Loses user data, poor UX, no awareness of conflicts

**Implementation Pattern**:
```python
# Logic layer
def update_profile(user_id, data, submitted_updated_at):
    user = User.query.get(user_id)
    if user.updated_at > submitted_updated_at:
        raise ConcurrentEditError(current_data=user.to_dict())
    # Proceed with update...
```

### 4. Email Notification Service

**Question**: What is the best approach for sending email notifications when users change their email address?

**Research Findings**:
- **Existing Infrastructure**: Feature 001 may have email service for contact form
- **Transactional Emails**: Profile change notifications are transactional (not marketing), need reliable delivery
- **Template Structure**: Separate templates for old email ("Your email was changed") and new email ("Confirm your new email")
- **Asynchronous Sending**: Queue emails to avoid blocking user response (simple in-memory queue for MVP)
- **Email Content**: Include timestamp, IP address, "If this wasn't you" warning for security
- **SMTP Libraries**: Python `smtplib` (standard library) or Flask-Mail extension

**Decision**:
1. Check for existing `EmailService` from Feature 001, extend if present
2. If not present: Create minimal `EmailService` wrapper around `smtplib`
3. Create templates: `templates/emails/email_change_old.html`, `email_change_new.html`
4. Queue emails in simple in-memory list, send asynchronously after response
5. For production: Recommend Celery + Redis for robust async email

**Rationale**:
- Reusing existing email infrastructure reduces code duplication
- Asynchronous sending prevents slow email providers from blocking user
- Security notifications build user trust

**Alternatives Considered**:
- **Synchronous email**: Blocks user response, poor UX (can take 5+ seconds)
- **No notifications**: Security risk (user unaware of unauthorized changes)
- **External service (SendGrid, Mailgun)**: Overkill for MVP, adds cost and complexity

**Implementation Strategy**:
```python
# Logic layer
def update_email(user, new_email):
    old_email = user.email
    user.email = new_email
    db.session.commit()
    
    # Queue asynchronous emails
    email_service.send_email_change_notification(old_email, new_email)
```

### 5. Client-Side Image Preview & Compression

**Question**: How can we provide instant image preview and reduce upload sizes using client-side JavaScript?

**Research Findings**:
- **FileReader API**: Browser API to read file contents, create data URL for preview
- **Canvas API**: Draw image to canvas, resize, export as compressed base64
- **Progressive Enhancement**: Image preview enhances UX but shouldn't be required (server validates anyway)
- **Size Warning**: Display file size before upload, warn if > 5MB
- **Browser Support**: FileReader supported in all modern browsers (IE10+)

**Decision**:
1. Use FileReader API to preview selected image immediately (no server round-trip)
2. Display file size, warn if > 5MB (suggest reducing image quality/size)
3. Optional: Implement Canvas-based client-side resize for large images
4. Show loading spinner during upload
5. Fallback: Server handles all validation (client-side is enhancement only)

**Rationale**:
- Instant preview improves UX (user knows image selected correctly)
- File size warning prevents failed uploads (user can fix before submitting)
- Progressive enhancement: works without JavaScript, enhanced with JavaScript

**Alternatives Considered**:
- **Server-only processing**: Works but user doesn't see preview until after upload
- **No preview**: Poor UX, user uncertain if image uploaded correctly
- **Mandatory client-side resize**: Breaks for users with JavaScript disabled

**Implementation Pattern**:
```javascript
// static/script/settings.js
function previewImage(fileInput) {
    const file = fileInput.files[0];
    if (file.size > 5 * 1024 * 1024) {
        alert('Warning: Image exceeds 5MB limit. Upload may fail.');
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('preview').src = e.target.result;
    };
    reader.readAsDataURL(file);
}
```

## Technology Decisions

### Core Technologies
- **Language**: Python 3.11+
- **Framework**: Flask 3.1.2 (existing)
- **ORM**: SQLAlchemy (existing)
- **Database**: SQLite (existing)
- **Image Processing**: Pillow 10.0.0 (new dependency)
- **Encoding**: Python standard library `base64` module
- **Email**: Python `smtplib` or Flask-Mail (TBD based on existing infrastructure)

### Architecture Patterns
- **MVC**: Thin controllers, thick logic layer, thin models (constitutional requirement)
- **TDD**: Tests first, implementation second (constitutional requirement)
- **Optimistic Locking**: Timestamp-based concurrent edit detection
- **Lazy Loading**: Defer profile_picture_data column in SQLAlchemy queries
- **Progressive Enhancement**: Client-side features enhance but don't replace server-side validation

### Performance Targets
- Page load: < 500ms (constitutional requirement)
- Profile update: < 2 seconds including image encoding (spec requirement)
- Image encoding: < 1 second for 5MB image
- Lazy loading: Exclude profile_picture_data from queries where not needed (50%+ performance improvement)

## Open Questions Resolved

| Question | Resolution |
|----------|-----------|
| How to store images? | Base64 TEXT in SQLite, lazy loaded |
| How to validate images? | Pillow library with magic number validation |
| How to handle concurrent edits? | Optimistic locking with `updated_at` timestamp |
| How to notify on email change? | Asynchronous emails to both old and new addresses |
| How to preview images? | FileReader API (client-side, progressive enhancement) |

## Next Steps

**Phase 1**: Design & Contracts
1. Define User model extensions in `data-model.md`
2. Create API contracts for GET/POST /settings
3. Generate contract tests (failing initially)
4. Create integration test scenarios
5. Generate `quickstart.md` manual test plan
6. Update `.github/copilot-instructions.md` with Feature 003 context

**Blocked By**: None - all research complete

**Ready to Proceed**: ✅ Yes
