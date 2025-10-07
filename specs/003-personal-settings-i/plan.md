# Implementation Plan: User Profile & Personal Settings

**Branch**: `003-personal-settings-i` | **Date**: 2025-10-06 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/003-personal-settings-i/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   ✅ Loaded from specs/003-personal-settings-i/spec.md
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   ✅ Detected Project Type: Flask MVC web application
   ✅ Set Structure Decision: Flask MVC (controllers + logic + models)
3. Fill the Constitution Check section
   ✅ Based on .specify/memory/constitution.md v1.0.0
4. Evaluate Constitution Check section
   ✅ No violations detected
   ✅ Update Progress Tracking: Initial Constitution Check PASS
5. Execute Phase 0 → research.md
   ⏳ In progress
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, .github/copilot-instructions.md
   ⏳ Pending Phase 0 completion
7. Re-evaluate Constitution Check section
   ⏳ Pending Phase 1 completion
8. Plan Phase 2 → Describe task generation approach
   ⏳ Pending Phase 1 completion
9. STOP - Ready for /tasks command
   ⏳ Pending all phases
```

## Summary

Implement a comprehensive personal settings page where authenticated users can view and edit their profile information including full name, email address, bio/description, password, and profile picture. The system will provide real-time validation, concurrent edit detection, email notifications on changes, and secure image storage as base64-encoded data in SQLite. All changes follow the existing MVC architecture with session management integration.

**Key Features**:
- Profile field editing (name, email, bio, password, profile picture)
- Base64 image encoding/decoding for SQLite storage
- Concurrent modification detection via timestamp comparison
- Email notifications for email address changes
- Client-side and server-side validation
- CSRF protection and XSS prevention
- Integration with existing authentication system

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Flask 3.1.2, Flask-SQLAlchemy, bcrypt, Pillow (image processing)  
**Storage**: SQLite with base64-encoded images stored as TEXT fields  
**Testing**: pytest 8.4.2, pytest-flask for integration tests  
**Target Platform**: Cross-platform web application (development on Windows/Linux)  
**Project Type**: Flask MVC web application (thin controllers, thick logic layer, thin models)  
**Performance Goals**: Page load < 500ms, profile updates < 2 seconds, image encoding < 1 second  
**Constraints**: 
- Profile pictures maximum 5MB file size
- Bio limited to 500 characters
- Images stored as base64 TEXT in SQLite (not file system)
- Must integrate with existing session management system
- Concurrent edit detection required (optimistic locking)
**Scale/Scope**: Single-user profile editing, ~5-10 editable fields, image conversion utilities

**User-Provided Implementation Details**:
- Store images (and future audio/video) as base64 inside SQLite database
- Need conversion function for base64 encoding/decoding
- No file system storage for media assets

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### MVC Separation of Concerns
✅ **PASS**: Controllers will handle routing only (`/settings` routes), logic layer will contain profile update operations, validation, image conversion, and email notification logic. Models remain thin with only database schema.

### Thin Controllers & Models
✅ **PASS**: Controllers delegate to `ProfileService` in logic layer. Models (`User`) only define schema and relationships. Business logic for password validation, image encoding, concurrent edit detection resides in logic layer.

### Database Layer Standards
✅ **PASS**: Using SQLite with SQLAlchemy ORM. User model extends existing base model. New fields added to User table via migration. Profile picture stored as TEXT (base64).

### Template Inheritance
✅ **PASS**: Personal settings page extends `private.html` base template. Uses Jinja2 for form rendering. Minimal template logic - data preparation in logic layer.

### Static Asset Organization
✅ **PASS**: CSS for settings page in `static/css/settings.css`. JavaScript for image preview/validation in `static/script/settings.js`. No new image assets needed (user uploads).

**Overall**: ✅ PASS - No constitutional violations. Design follows Flask MVC principles.

## Project Structure

### Documentation (this feature)
```
specs/003-personal-settings-i/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
│   ├── get-settings.json
│   ├── post-settings.json
│   └── post-upload-image.json
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
src/
├── controllers/
│   └── settings_routes.py         # GET/POST /settings routes (thin)
├── logic/
│   ├── profile_service.py          # Profile update operations (thick)
│   └── image_utils.py              # Base64 encoding/decoding utilities
├── models/
│   └── user.py                     # Extended with bio, profile_picture_data, updated_at
├── static/
│   ├── css/
│   │   └── settings.css            # Settings page styles
│   ├── script/
│   │   └── settings.js             # Client-side validation, image preview, unsaved changes warning
│   └── img/                        # (no new assets)
├── templates/
│   ├── bases/
│   │   └── private.html            # (existing - settings extends this)
│   └── privates/
│       └── settings/
│           └── index.html          # Personal settings form
└── utils/
    └── validators.py               # (extend existing - add bio validation)

tests/
├── contract/
│   ├── test_settings_get.py        # Contract test for GET /settings
│   ├── test_settings_post.py       # Contract test for POST /settings
│   └── test_image_upload.py        # Contract test for image upload endpoint
├── integration/
│   ├── test_profile_update_flow.py # End-to-end profile update
│   ├── test_concurrent_edit.py     # Concurrent modification detection
│   └── test_email_notification.py  # Email change notifications
└── unit/
    ├── test_profile_service.py     # Profile update logic
    ├── test_image_utils.py         # Base64 conversion functions
    └── test_validators.py          # Bio/image validation
```

**Structure Decision**: Flask MVC architecture with thin controllers delegating to thick logic layer. Image storage uses base64 TEXT encoding in SQLite to avoid file system complexity. New `image_utils.py` provides reusable conversion functions for future audio/video features.

## Phase 0: Outline & Research

### Unknowns Identified
1. Best practices for base64 image storage in SQLite (size limits, performance)
2. Image validation and security (malicious file detection, MIME type verification)
3. Concurrent edit detection patterns (optimistic locking vs pessimistic)
4. Email notification best practices for profile changes
5. Client-side image preview and compression before upload

### Research Tasks

#### Task 1: Base64 Image Storage in SQLite
**Research**: Investigate base64-encoded image storage in SQLite TEXT fields
- Maximum practical size for TEXT columns in SQLite
- Performance implications of base64 encoding (33% size increase)
- Efficient query patterns when profile picture is included
- Base64 encoding/decoding libraries in Python (built-in `base64` module)

**Decision**: Use built-in Python `base64` module, store as TEXT in `User.profile_picture_data` column, implement lazy loading (exclude from default queries).

**Rationale**: SQLite TEXT columns can handle multi-megabyte data. Base64 standard encoding is reliable. Lazy loading prevents performance impact on user queries that don't need profile pictures.

**Alternatives Considered**: 
- File system storage: Rejected per user requirement
- BLOB storage: Rejected because base64 TEXT is more portable and easier to debug

#### Task 2: Image Validation & Security
**Research**: Security best practices for user-uploaded images
- File type validation (magic number vs extension)
- Image malware scanning techniques
- Pillow library for image validation and sanitization
- Size limits and compression strategies

**Decision**: Use Pillow to validate image format by reading headers, reject non-image files, enforce 5MB pre-encoding limit, optionally resize large images before encoding.

**Rationale**: Pillow validates images by attempting to parse them, which detects malicious files. Size limit prevents abuse. Optional resizing reduces storage requirements.

**Alternatives Considered**:
- Extension-only validation: Insecure (easily spoofed)
- Antivirus scanning: Overkill for MVP, adds external dependency

#### Task 3: Concurrent Edit Detection
**Research**: Optimistic locking patterns for web applications
- Timestamp-based version comparison
- Version number increment patterns
- UI/UX for conflict resolution

**Decision**: Add `updated_at` timestamp to User model, compare on save, return 409 Conflict if timestamp changed, display conflict resolution UI with current values.

**Rationale**: Timestamp comparison is simple and effective for single-user profile edits. 409 status code is semantically correct for conflicts.

**Alternatives Considered**:
- Version number column: Functionally equivalent but requires additional field
- Pessimistic locking: Unnecessary complexity for infrequent edits

#### Task 4: Email Notification Service
**Research**: Email notification patterns for profile changes
- Transactional email best practices
- Template structure for change notifications
- Integration with existing email service (if any)

**Decision**: Extend existing email service (from Feature 001 contact form), create email templates for old/new email notifications, send asynchronously to avoid blocking user.

**Rationale**: Reuse existing infrastructure. Asynchronous sending ensures fast user response times.

**Alternatives Considered**:
- Synchronous email: Blocks user, poor UX
- No notifications: Security risk, user unaware of changes

#### Task 5: Client-Side Image Preview & Compression
**Research**: JavaScript techniques for image preview before upload
- FileReader API for preview
- Canvas API for client-side compression/resizing
- Progressive upload UI patterns

**Decision**: Use FileReader API to preview image immediately after selection, display file size warning if > 5MB, optionally implement Canvas-based resize on client side.

**Rationale**: Immediate preview improves UX. Size warning prevents failed uploads. Client-side resize reduces server load.

**Alternatives Considered**:
- Server-only processing: Works but slower feedback to user
- No preview: Poor UX, user uncertain if upload worked

### Consolidated Findings

**Image Storage Architecture**:
- Use Python `base64.b64encode()` and `base64.b64decode()` (standard library)
- Store in `User.profile_picture_data` as SQLAlchemy `Text` column
- Implement `ProfileService.encode_image(file_bytes)` utility
- Implement `ProfileService.decode_image(base64_string)` utility
- Lazy load images: exclude `profile_picture_data` from default User queries
- Consider adding `User.profile_picture_mime_type` to store original MIME type

**Validation Architecture**:
- Server-side: Pillow to validate image format, check file size <= 5MB pre-encoding
- Client-side: FileReader API for instant preview, file size check before submit
- Security: Pillow image parsing rejects malformed/malicious files
- Sanitization: Strip EXIF data using `Pillow.Image.getexif()` and re-save

**Concurrent Edit Architecture**:
- Add `updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` to User model
- Send `updated_at` value to client with form (hidden field)
- On POST, compare `updated_at` from form with current database value
- If mismatch: return 409 Conflict with current data
- Client displays conflict UI showing changed fields, options to reload or force overwrite

**Email Notification Architecture**:
- Reuse `EmailService` from Feature 001 (if exists) or create minimal SMTP wrapper
- Create templates: `email_change_old.html`, `email_change_new.html`
- Send both emails when email changes (old address: "Your email was changed", new address: "Confirm your new email")
- Queue emails for async sending (simple in-memory queue for MVP, Redis/Celery for production)

**Output**: research.md created

## Phase 1: Design & Contracts

### Data Model Design

**User Model Extensions** (extend existing `src/models/user.py`):
```python
class User(BaseModel):
    # Existing fields from Feature 001:
    # id, email, full_name, password_hash, created_at
    
    # NEW fields for Feature 003:
    bio = db.Column(db.Text, nullable=True)  # 0-500 chars, validated in logic layer
    profile_picture_data = db.Column(db.Text, nullable=True)  # base64-encoded image
    profile_picture_mime_type = db.Column(db.String(50), nullable=True)  # e.g., "image/jpeg"
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Lazy load relationship to avoid loading images in list queries
    # (no relationship needed - direct column access)
```

**No New Models**: All data stored in existing `User` model.

**Migration**:
- Add columns: `bio`, `profile_picture_data`, `profile_picture_mime_type`, `updated_at`
- Set defaults: NULL for optional fields, CURRENT_TIMESTAMP for updated_at
- Add index on `updated_at` for concurrent edit queries

### API Contracts

**Contract 1: GET /settings**
```json
{
  "endpoint": "/settings",
  "method": "GET",
  "authentication": "required (session)",
  "request": {},
  "response": {
    "status": 200,
    "body": {
      "user": {
        "id": "integer",
        "full_name": "string (2-100 chars)",
        "email": "string (valid email)",
        "bio": "string | null (0-500 chars)",
        "profile_picture_data": "string | null (base64)",
        "profile_picture_mime_type": "string | null",
        "updated_at": "ISO 8601 timestamp"
      }
    }
  },
  "errors": {
    "401": "Not authenticated",
    "403": "Forbidden (accessing another user's settings)"
  }
}
```

**Contract 2: POST /settings**
```json
{
  "endpoint": "/settings",
  "method": "POST",
  "authentication": "required (session + CSRF token)",
  "request": {
    "body": {
      "full_name": "string (required, 2-100 chars)",
      "email": "string (required, valid email)",
      "bio": "string | null (0-500 chars)",
      "current_password": "string | null (required if email/password changing)",
      "new_password": "string | null (8+ chars, uppercase, lowercase, number)",
      "profile_picture_data": "string | null (base64, <= 5MB original)",
      "profile_picture_mime_type": "string | null",
      "updated_at": "ISO 8601 timestamp (for concurrent edit detection)"
    }
  },
  "response": {
    "status": 200,
    "body": {
      "success": true,
      "message": "Profile updated successfully",
      "user": {
        "full_name": "string",
        "email": "string",
        "bio": "string | null",
        "profile_picture_data": "string | null",
        "updated_at": "ISO 8601 timestamp (new value)"
      }
    }
  },
  "errors": {
    "400": "Validation error (invalid email, password too weak, bio too long, image too large)",
    "401": "Not authenticated",
    "403": "CSRF token invalid or missing",
    "409": "Concurrent modification detected (updated_at mismatch)",
    "422": "Current password incorrect (when changing email/password)"
  }
}
```

**Contract 3: POST /settings/upload-image** (optional separate endpoint)
```json
{
  "endpoint": "/settings/upload-image",
  "method": "POST",
  "authentication": "required (session + CSRF token)",
  "request": {
    "content_type": "multipart/form-data",
    "fields": {
      "image": "file (JPEG, PNG, GIF, <= 5MB)"
    }
  },
  "response": {
    "status": 200,
    "body": {
      "success": true,
      "preview_data": "base64 string",
      "mime_type": "string",
      "file_size": "integer (bytes)"
    }
  },
  "errors": {
    "400": "Invalid file type or size",
    "401": "Not authenticated",
    "403": "CSRF token invalid"
  }
}
```

**Note**: May combine image upload with main POST /settings for simplicity. Separate endpoint allows AJAX preview upload.

### Contract Test Skeletons

**tests/contract/test_settings_get.py**:
```python
def test_get_settings_authenticated_returns_200():
    # GIVEN authenticated user
    # WHEN GET /settings
    # THEN status 200 with user profile data
    assert False  # Placeholder - implement after routes exist

def test_get_settings_unauthenticated_returns_401():
    # GIVEN no session
    # WHEN GET /settings
    # THEN status 401
    assert False
```

**tests/contract/test_settings_post.py**:
```python
def test_post_settings_valid_data_returns_200():
    # GIVEN authenticated user with valid profile updates
    # WHEN POST /settings with CSRF token
    # THEN status 200, profile updated
    assert False

def test_post_settings_invalid_email_returns_400():
    # GIVEN authenticated user with invalid email format
    # WHEN POST /settings
    # THEN status 400 with validation error
    assert False

def test_post_settings_concurrent_edit_returns_409():
    # GIVEN authenticated user with stale updated_at
    # WHEN POST /settings
    # THEN status 409 with conflict message
    assert False

def test_post_settings_wrong_password_returns_422():
    # GIVEN authenticated user changing email with wrong current_password
    # WHEN POST /settings
    # THEN status 422
    assert False
```

**tests/contract/test_image_upload.py**:
```python
def test_upload_valid_image_returns_200():
    # GIVEN authenticated user with valid image file
    # WHEN POST /settings/upload-image
    # THEN status 200 with base64 preview
    assert False

def test_upload_oversized_image_returns_400():
    # GIVEN image > 5MB
    # WHEN POST /settings/upload-image
    # THEN status 400 with size error
    assert False

def test_upload_non_image_returns_400():
    # GIVEN non-image file (e.g., .exe)
    # WHEN POST /settings/upload-image
    # THEN status 400 with type error
    assert False
```

### Integration Test Scenarios

**tests/integration/test_profile_update_flow.py**:
```python
def test_user_updates_full_name_successfully():
    # Create user -> Login -> Navigate to /settings -> Submit new name -> Verify updated

def test_user_updates_email_receives_notifications():
    # Create user -> Login -> Change email -> Verify both emails sent

def test_user_uploads_profile_picture():
    # Create user -> Login -> Upload image -> Verify base64 stored in DB

def test_user_changes_password_successfully():
    # Create user -> Login -> Change password with current password -> Logout -> Login with new password

def test_validation_errors_displayed_on_invalid_input():
    # Submit empty name, invalid email, weak password -> Verify error messages
```

**tests/integration/test_concurrent_edit.py**:
```python
def test_concurrent_edit_detection():
    # User A loads settings -> User B updates profile -> User A submits -> Verify 409 conflict

def test_concurrent_edit_resolution_overwrite():
    # Simulate conflict -> User chooses "force overwrite" -> Verify user's changes saved

def test_concurrent_edit_resolution_reload():
    # Simulate conflict -> User chooses "reload" -> Verify form refreshed with latest data
```

**tests/integration/test_email_notification.py**:
```python
def test_email_change_sends_to_old_and_new():
    # Change email -> Verify 2 emails sent (old address, new address)

def test_email_notification_content():
    # Verify email templates contain correct information (old email, new email, change time)
```

### Quickstart Test Plan

**File**: `specs/003-personal-settings-i/quickstart.md`

```markdown
# Personal Settings Feature Quickstart

## Prerequisites
- Feature 001 (authentication) complete
- Test database initialized
- Email service configured (SMTP or mock)

## Test Scenario 1: Profile Update
1. Register new user: john@example.com / SecurePass123
2. Login as john@example.com
3. Navigate to /settings
4. **Verify**: Form pre-populated with "john@example.com", empty bio, no profile picture
5. Update full name to "John Doe"
6. Add bio: "Software engineer passionate about Python"
7. Click Save
8. **Verify**: Success message displayed
9. **Verify**: Name appears as "John Doe" in navigation/header

## Test Scenario 2: Profile Picture Upload
1. Login as existing user
2. Navigate to /settings
3. Click "Upload Profile Picture"
4. Select valid JPEG (< 5MB)
5. **Verify**: Image preview appears
6. Click Save
7. **Verify**: Profile picture displays in navigation/header
8. **Database Check**: Query user record, verify `profile_picture_data` contains base64 string starting with valid base64 chars

## Test Scenario 3: Email Change with Notifications
1. Login as user@example.com
2. Navigate to /settings
3. Change email to newuser@example.com
4. Enter current password
5. Click Save
6. **Verify**: Success message displayed
7. **Email Check**: Verify email sent to user@example.com (subject: "Email Address Changed")
8. **Email Check**: Verify email sent to newuser@example.com (subject: "Confirm Your New Email")

## Test Scenario 4: Password Change
1. Login as user with password "OldPass123"
2. Navigate to /settings
3. Enter current password: "OldPass123"
4. Enter new password: "NewPass456"
5. Click Save
6. **Verify**: Success message
7. Logout
8. Login with "NewPass456"
9. **Verify**: Login successful

## Test Scenario 5: Validation Errors
1. Login as existing user
2. Navigate to /settings
3. Clear full name field
4. Enter invalid email: "notanemail"
5. Enter bio with 600 characters (exceeds 500 limit)
6. Click Save
7. **Verify**: Error messages displayed for each invalid field
8. **Verify**: Form data preserved (bio text not lost)

## Test Scenario 6: Concurrent Edit Detection
1. Login as user in two different browsers (A and B)
2. Browser A: Navigate to /settings
3. Browser B: Navigate to /settings
4. Browser B: Change name to "User B", click Save
5. Browser A: Change name to "User A", click Save
6. **Verify**: Browser A shows conflict warning
7. **Verify**: Conflict UI displays "Name changed from [original] to 'User B'"
8. Browser A: Click "Reload" button
9. **Verify**: Form refreshes with "User B" name
```

### Agent Context File Update

**File**: `.github/copilot-instructions.md` (GitHub Copilot)

**Incremental Update Strategy**:
1. Run `.specify/scripts/bash/update-agent-context.sh copilot`
2. Script will:
   - Detect existing file
   - Add new technical details under appropriate sections
   - Preserve manual annotations between `<!-- MANUAL START -->` and `<!-- MANUAL END -->` markers
   - Update "Recent Changes" section with Feature 003 entry (keep last 3)
   - Keep total file under 150 lines

**New Content to Add**:
- **Current Feature** section: Feature 003 - Personal Settings (scope, branch)
- **Database Models** section: User model extensions (bio, profile_picture_data, updated_at)
- **Key Technologies** section: Pillow for image validation, base64 module for encoding
- **Common Patterns** section: Base64 image storage pattern, concurrent edit detection pattern
- **Recent Changes**: Feature 003 personal settings with base64 image storage

**Execution**:
```bash
bash .specify/scripts/bash/update-agent-context.sh copilot
```

**Output**: `.github/copilot-instructions.md` updated with Feature 003 context (≤150 lines total)

### Phase 1 Artifacts Summary

**Generated Files**:
1. `specs/003-personal-settings-i/data-model.md` - User model extensions, migration details
2. `specs/003-personal-settings-i/contracts/get-settings.json` - GET /settings contract
3. `specs/003-personal-settings-i/contracts/post-settings.json` - POST /settings contract
4. `specs/003-personal-settings-i/contracts/post-upload-image.json` - Image upload contract (optional)
5. `specs/003-personal-settings-i/quickstart.md` - Manual test scenarios
6. `tests/contract/test_settings_get.py` - Failing contract tests for GET
7. `tests/contract/test_settings_post.py` - Failing contract tests for POST
8. `tests/contract/test_image_upload.py` - Failing contract tests for image upload
9. `tests/integration/test_profile_update_flow.py` - Failing integration tests
10. `tests/integration/test_concurrent_edit.py` - Failing concurrent edit tests
11. `tests/integration/test_email_notification.py` - Failing email notification tests
12. `.github/copilot-instructions.md` - Updated agent context

**Phase 1 Complete**: ✅

## Phase 2: Task Planning Approach

*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base structure
- Parse Phase 1 artifacts (contracts, data model, integration tests)
- Generate tasks in TDD order: Tests → Implementation → Validation
- Each contract → one contract test task [P] (parallel execution safe)
- Each model change → one migration task, one unit test task
- Each integration test → one implementation task
- Each user story → one validation task

**Task Categories**:
1. **Setup Tasks** (T001-T005):
   - Database migration for User model extensions
   - Create image_utils.py module structure
   - Create profile_service.py module structure
   - Create settings_routes.py controller
   - Create settings template and static files

2. **Contract Test Tasks** (T006-T010) [P]:
   - Implement test_settings_get.py contract tests
   - Implement test_settings_post.py contract tests
   - Implement test_image_upload.py contract tests
   - Run tests (expect failures)
   - Verify test coverage of all contracts

3. **Unit Test Tasks** (T011-T020) [P]:
   - Test ProfileService.get_user_profile()
   - Test ProfileService.update_profile()
   - Test ProfileService.validate_profile_data()
   - Test ImageUtils.encode_image()
   - Test ImageUtils.decode_image()
   - Test ImageUtils.validate_image()
   - Test concurrent edit detection logic
   - Test email notification triggers
   - Test password change validation
   - Test bio validation

4. **Integration Test Tasks** (T021-T025):
   - Implement test_profile_update_flow.py scenarios
   - Implement test_concurrent_edit.py scenarios
   - Implement test_email_notification.py scenarios
   - Run integration tests (expect failures)
   - Verify end-to-end coverage

5. **Implementation Tasks** (T026-T040):
   - Implement ImageUtils.encode_image() (base64 encoding)
   - Implement ImageUtils.decode_image() (base64 decoding)
   - Implement ImageUtils.validate_image() (Pillow validation)
   - Implement ProfileService.get_user_profile()
   - Implement ProfileService.update_profile() with validation
   - Implement ProfileService.detect_concurrent_edit()
   - Implement ProfileService.send_email_change_notifications()
   - Implement settings_routes.py GET /settings
   - Implement settings_routes.py POST /settings
   - Implement settings/index.html template
   - Implement static/css/settings.css
   - Implement static/script/settings.js (validation, preview, unsaved warning)
   - Integrate with existing session management
   - Implement CSRF protection on POST
   - Implement password change with bcrypt

6. **Validation Tasks** (T041-T045):
   - Run all contract tests → verify PASS
   - Run all unit tests → verify PASS
   - Run all integration tests → verify PASS
   - Execute quickstart.md scenarios manually
   - Performance validation (page load < 500ms, updates < 2s)

**Ordering Strategy**:
- **Phase order**: Setup → Contract Tests → Unit Tests → Integration Tests → Implementation → Validation
- **TDD principle**: All tests written and failing before implementation
- **Dependency order**: 
  - Models/migrations before services
  - Services before controllers
  - Controllers before templates
  - Utils (image_utils) can be parallel with tests
- **Parallel markers [P]**: Contract tests are independent, unit tests are independent
- **Sequential dependencies**: Integration tests depend on contract tests, implementation depends on tests

**Estimated Task Count**: 45 tasks total
- Setup: 5 tasks
- Contract Tests: 5 tasks
- Unit Tests: 10 tasks
- Integration Tests: 5 tasks
- Implementation: 15 tasks
- Validation: 5 tasks

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation

*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md with 45 numbered tasks)  
**Phase 4**: Implementation (execute tasks T001-T045 following TDD, constitutional MVC principles)  
**Phase 5**: Validation (run all tests, execute quickstart.md, verify performance < 2s, security audit, code quality review)

**Constitutional Compliance Checkpoints**:
- After models: Verify thin (only schema, no business logic)
- After services: Verify thick (all validation, conversion, email logic here)
- After controllers: Verify thin (only routing, delegation to services)
- After templates: Verify minimal logic (data prep in services)
- After completion: Full architecture review against constitution v1.0.0

## Complexity Tracking

*No constitutional violations identified. No entries required.*

## Progress Tracking

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) ✅
- [x] Phase 1: Design complete (/plan command) ✅
- [x] Phase 2: Task planning complete (/plan command - described approach) ✅
- [ ] Phase 3: Tasks generated (/tasks command) ⏳ READY
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS ✅
- [x] Post-Design Constitution Check: PASS ✅
- [x] All NEEDS CLARIFICATION resolved (via /clarify command) ✅
- [x] Complexity deviations documented (none) ✅

**Artifacts Generated**:
- [x] research.md (Phase 0) ✅
- [x] data-model.md (Phase 1) ✅
- [x] contracts/get-settings.json (Phase 1) ✅
- [x] contracts/post-settings.json (Phase 1) ✅
- [x] quickstart.md (Phase 1) ✅
- [x] .github/copilot-instructions.md updated (Phase 1) ✅
- [ ] tasks.md (Phase 2 - /tasks command) ⏳ READY

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
*Plan generated: 2025-10-06*
*Ready for: /tasks command to generate tasks.md*
