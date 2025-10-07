# Tasks: User Profile & Personal Settings

**Feature**: 003-personal-settings-i  
**Branch**: `003-personal-settings-i`  
**Input**: Design documents from `/specs/003-personal-settings-i/`  
**Prerequisites**: plan.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

## Execution Flow (main)
```
1. Load plan.md from feature directory
   ✅ Loaded: Flask MVC web app, Python 3.11+, Flask 3.1.2
   ✅ Tech stack: SQLAlchemy, bcrypt, Pillow, pytest
   ✅ Structure: src/controllers, src/logic, src/models, src/templates
2. Load optional design documents:
   ✅ data-model.md: User entity extensions (4 new columns)
   ✅ contracts/: 2 contracts (GET/POST /settings)
   ✅ research.md: Base64 storage, concurrent edits, image validation
3. Generate tasks by category:
   ✅ Setup: 5 tasks (migration, dependencies, utilities)
   ✅ Tests: 15 tasks (2 contract, 10 unit, 3 integration)
   ✅ Core: 15 tasks (models, logic, controllers, templates)
   ✅ Integration: 5 tasks (session, email, CSRF, validation)
   ✅ Polish: 5 tasks (validation, performance, docs)
4. Apply task rules:
   ✅ Different files marked [P] for parallel execution
   ✅ Same file tasks sequential (no [P])
   ✅ Tests before implementation (TDD enforced)
5. Number tasks sequentially (T001-T045)
6. Dependencies identified and documented
7. Parallel execution examples generated
8. Validation:
   ✅ All 2 contracts have test tasks
   ✅ User entity has model extension task
   ✅ All tests come before implementation
   ✅ [P] tasks are truly independent
9. Return: SUCCESS (45 tasks ready for execution)
```

## Task Summary

**Total Tasks**: 45  
**Estimated Completion**: 8-12 hours (TDD approach)  
**Parallel Opportunities**: 23 tasks can run in parallel across 5 phases

**Phases**:
- **3.1 Setup** (5 tasks): Database migration, dependencies, utility modules
- **3.2 Tests First** (15 tasks): Contract tests, unit tests, integration tests - ⚠️ MUST COMPLETE BEFORE 3.3
- **3.3 Core Implementation** (15 tasks): Logic layer, controllers, templates, static assets
- **3.4 Integration** (5 tasks): Session management, email service, CSRF, validation
- **3.5 Polish** (5 tasks): Error handling, performance, documentation, quickstart validation

---

## Phase 3.1: Setup & Infrastructure

### T001: Database Migration for User Profile Fields ✅
**File**: `migrations/003_add_user_profile_fields.sql` or Alembic migration  
**Description**: Create database migration to add 4 new columns to `user` table:
- `bio` (TEXT, nullable)
- `profile_picture_data` (TEXT, nullable)
- `profile_picture_mime_type` (VARCHAR(50), nullable)
- `updated_at` (DATETIME, default CURRENT_TIMESTAMP, indexed)

Include SQLite trigger for auto-updating `updated_at` timestamp.

**Acceptance**: 
- Migration file created ✅
- Can run `flask db upgrade` successfully ✅
- Can rollback with `flask db downgrade` ✅
- Index created on `updated_at` column ✅

**Dependencies**: None

**Status**: COMPLETE - Migration created, columns added to user table, index and trigger created

---

### T002: Install Pillow Dependency ✅
**File**: `requirements.txt`  
**Description**: Add Pillow library for image validation and processing.

```
Pillow==11.3.0
```

Run `pip install -r requirements.txt` to verify installation.

**Acceptance**:
- Pillow added to requirements.txt ✅
- Can import Pillow: `from PIL import Image` ✅

**Dependencies**: None

**Status**: COMPLETE - Pillow 11.3.0 installed successfully

---

### T003 [P]: Create Image Utils Module Structure ✅
**File**: `src/logic/image_utils.py`  
**Description**: Create utility module for base64 image encoding/decoding with function stubs:
- `encode_image(file_bytes: bytes) -> str` - Convert bytes to base64 string
- `decode_image(base64_string: str) -> bytes` - Convert base64 to bytes
- `validate_image(file_bytes: bytes) -> tuple[bool, str]` - Validate with Pillow, return (valid, mime_type)
- `sanitize_image(file_bytes: bytes) -> bytes` - Strip EXIF, optionally resize

Add docstrings but leave implementation empty (will be filled in T026-T028).

**Acceptance**:
- File created with function stubs ✅
- All functions have type hints and docstrings ✅
- Imports: `base64`, `io`, `PIL.Image` ✅

**Dependencies**: T002 (Pillow installed)

**Status**: COMPLETE - Module created with all function stubs and comprehensive docstrings

---

### T004 [P]: Create Profile Service Module Structure ✅
**File**: `src/logic/profile_service.py`  
**Description**: Create service class for profile operations with method stubs:
- `get_user_profile(user_id: int, include_picture: bool = False) -> dict`
- `update_profile(user_id: int, data: dict, submitted_updated_at: str) -> dict`
- `validate_profile_data(data: dict) -> tuple[bool, dict]`
- `detect_concurrent_edit(user: User, submitted_updated_at: str) -> bool`
- `send_email_change_notifications(old_email: str, new_email: str) -> None`

Add docstrings, leave implementation empty.

**Acceptance**:
- File created with ProfileService class ✅
- All methods stubbed with type hints and docstrings ✅
- Imports: User model, datetime, typing ✅

**Dependencies**: None

**Status**: COMPLETE - ProfileService class created with all method stubs

---

### T005 [P]: Create Settings Controller Structure ✅
**File**: `src/controllers/settings_routes.py`  
**Description**: Create Flask blueprint for settings routes with route stubs:
- `GET /settings` - Display settings page
- `POST /settings` - Update profile

Add `@login_required` decorator placeholders.

**Acceptance**:
- Blueprint created and registered (add to `__init__.py`) ✅
- Route handlers stubbed (return placeholder responses) ✅
- Imports: Flask, request, jsonify, render_template ✅

**Dependencies**: None

**Status**: COMPLETE - Blueprint created, routes stubbed, registered in routes.py

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE PHASE 3.3

**CRITICAL**: These tests MUST be written and MUST FAIL before ANY implementation in Phase 3.3.

### T006 [P]: Contract Test - GET /settings ✅
**File**: `tests/contract/test_settings_get.py`  
**Description**: Implement contract tests for GET /settings endpoint based on `contracts/get-settings.json`:

Test cases:
1. `test_get_settings_authenticated_returns_200()` - Authenticated user gets profile data
2. `test_get_settings_unauthenticated_returns_401()` - No session returns 401
3. `test_get_settings_response_schema()` - Response matches contract schema (user object with all fields)
4. `test_get_settings_excludes_picture_when_none()` - profile_picture_data is null when user has no picture
5. `test_get_settings_includes_updated_at()` - updated_at timestamp present in response

**Acceptance**:
- All 5 tests implemented ✅
- Tests FAIL (endpoints not implemented yet) ✅
- Use pytest fixtures for authenticated/unauthenticated users ✅

**Dependencies**: None (can run in parallel)

**Status**: COMPLETE - 5 test cases written, ready to fail

---

### T007 [P]: Contract Test - POST /settings ✅
**File**: `tests/contract/test_settings_post.py`  
**Description**: Implement contract tests for POST /settings endpoint based on `contracts/post-settings.json`:

Test cases:
1. `test_post_settings_valid_data_returns_200()` - Valid profile update succeeds
2. `test_post_settings_invalid_email_returns_400()` - Invalid email format returns validation error
3. `test_post_settings_concurrent_edit_returns_409()` - Stale updated_at returns 409 Conflict
4. `test_post_settings_wrong_password_returns_422()` - Incorrect current_password returns 422
5. `test_post_settings_missing_csrf_returns_403()` - No CSRF token returns 403
6. `test_post_settings_unauthenticated_returns_401()` - No session returns 401
7. `test_post_settings_response_schema()` - Success response matches contract

**Acceptance**:
- All 7 tests implemented ✅
- Tests FAIL (endpoint not implemented) ✅
- Use pytest fixtures for CSRF tokens ✅

**Status**: COMPLETE - 7 test cases written, ready to fail

**Dependencies**: None (can run in parallel)

---

### T008 [P]: Unit Test - Image Encoding
**File**: `tests/unit/test_image_utils.py`  
**Description**: Unit tests for `image_utils.py` functions:

Test `encode_image()`:
1. `test_encode_image_valid_jpeg()` - JPEG bytes → valid base64 string
2. `test_encode_image_valid_png()` - PNG bytes → valid base64 string
3. `test_encode_image_roundtrip()` - Encode then decode returns original bytes

Test `decode_image()`:
4. `test_decode_image_valid_base64()` - Base64 string → bytes
5. `test_decode_image_invalid_base64_raises()` - Invalid base64 raises exception

Test `validate_image()`:
6. `test_validate_image_valid_jpeg()` - Returns (True, "image/jpeg")
7. `test_validate_image_valid_png()` - Returns (True, "image/png")
8. `test_validate_image_non_image_returns_false()` - Text file returns (False, error)
9. `test_validate_image_oversized_returns_false()` - > 5MB returns (False, error)
10. `test_validate_image_malformed_returns_false()` - Corrupted image returns (False, error)

Test `sanitize_image()`:
11. `test_sanitize_image_strips_exif()` - EXIF data removed
12. `test_sanitize_image_preserves_content()` - Image visually identical after sanitization

**Acceptance**:
- All 12 tests implemented
- Tests FAIL (functions not implemented)
- Use sample test images in `tests/fixtures/`

**Dependencies**: None (can run in parallel)

---

### T009 [P]: Unit Test - Profile Service
**File**: `tests/unit/test_profile_service.py`  
**Description**: Unit tests for `ProfileService` methods:

Test `get_user_profile()`:
1. `test_get_user_profile_without_picture()` - Returns user data, excludes picture_data
2. `test_get_user_profile_with_picture()` - Include_picture=True returns picture_data
3. `test_get_user_profile_nonexistent_user()` - Returns None or raises exception

Test `update_profile()`:
4. `test_update_profile_full_name()` - Updates full_name successfully
5. `test_update_profile_email()` - Updates email successfully
6. `test_update_profile_bio()` - Updates bio successfully
7. `test_update_profile_password()` - Hashes new password with bcrypt
8. `test_update_profile_picture()` - Updates profile_picture_data
9. `test_update_profile_updates_timestamp()` - updated_at refreshes

Test `validate_profile_data()`:
10. `test_validate_profile_data_valid()` - Returns (True, {})
11. `test_validate_profile_data_empty_name()` - Returns (False, errors)
12. `test_validate_profile_data_invalid_email()` - Returns (False, errors)
13. `test_validate_profile_data_bio_too_long()` - Returns (False, errors)
14. `test_validate_profile_data_weak_password()` - Returns (False, errors)

Test `detect_concurrent_edit()`:
15. `test_detect_concurrent_edit_no_conflict()` - Same timestamp returns False
16. `test_detect_concurrent_edit_conflict()` - Different timestamp returns True

**Acceptance**:
- All 16 tests implemented
- Tests FAIL (service not implemented)
- Mock User model and database

**Dependencies**: None (can run in parallel)

---

### T010 [P]: Unit Test - Validators
**File**: `tests/unit/test_validators.py`  
**Description**: Unit tests for validation functions (extend existing `src/utils/validators.py`):

Test `validate_bio()`:
1. `test_validate_bio_valid()` - 200 char bio returns True
2. `test_validate_bio_empty()` - Empty string returns True (optional field)
3. `test_validate_bio_max_length()` - 500 char bio returns True
4. `test_validate_bio_exceeds_limit()` - 501 char bio returns False
5. `test_validate_bio_sanitizes_xss()` - `<script>` tags stripped

Test `validate_password_strength()`:
6. `test_validate_password_valid()` - "SecurePass123" returns True
7. `test_validate_password_too_short()` - "Abc1" returns False
8. `test_validate_password_no_uppercase()` - "secure123" returns False
9. `test_validate_password_no_lowercase()` - "SECURE123" returns False
10. `test_validate_password_no_number()` - "SecurePass" returns False

**Acceptance**:
- All 10 tests implemented
- Tests FAIL (functions not in validators.py yet)

**Dependencies**: None (can run in parallel)

---

### T011 [P]: Integration Test - Profile Update Flow
**File**: `tests/integration/test_profile_update_flow.py`  
**Description**: End-to-end integration tests for profile updates:

Test scenarios from `quickstart.md`:
1. `test_user_updates_full_name_successfully()` - Login → Change name → Verify updated
2. `test_user_updates_email_receives_notifications()` - Change email → Verify 2 emails sent
3. `test_user_uploads_profile_picture()` - Upload image → Verify base64 in DB
4. `test_user_changes_password_successfully()` - Change password → Logout → Login with new password
5. `test_validation_errors_displayed()` - Invalid data → Error messages shown
6. `test_form_data_preserved_on_error()` - Validation error → Form data not lost

**Acceptance**:
- All 6 tests implemented
- Tests FAIL (no implementation yet)
- Use Flask test client with session management

**Dependencies**: None (can run in parallel)

---

### T012 [P]: Integration Test - Concurrent Edit Detection
**File**: `tests/integration/test_concurrent_edit.py`  
**Description**: Integration tests for concurrent modification detection:

Test scenarios:
1. `test_concurrent_edit_detection()` - Simulate two sessions editing same profile
2. `test_concurrent_edit_response_409()` - Verify 409 status code returned
3. `test_concurrent_edit_shows_current_data()` - Conflict response includes current user data
4. `test_concurrent_edit_force_overwrite()` - User can force save despite conflict
5. `test_concurrent_edit_reload()` - User can reload form with latest data

**Acceptance**:
- All 5 tests implemented
- Tests FAIL (no implementation)
- Simulate concurrent edits with manual timestamp manipulation

**Dependencies**: None (can run in parallel)

---

### T013 [P]: Integration Test - Email Notifications
**File**: `tests/integration/test_email_notification.py`  
**Description**: Integration tests for email change notifications:

Test scenarios:
1. `test_email_change_sends_to_old_address()` - Verify email sent to old address
2. `test_email_change_sends_to_new_address()` - Verify email sent to new address
3. `test_email_notification_content_old()` - Old email has correct content
4. `test_email_notification_content_new()` - New email has correct content
5. `test_email_change_requires_current_password()` - Password verification enforced

**Acceptance**:
- All 5 tests implemented
- Tests FAIL (no implementation)
- Mock email service or use test SMTP

**Dependencies**: None (can run in parallel)

---

### T014 [P]: Unit Test - CSRF Protection
**File**: `tests/unit/test_csrf_utils.py` (extend existing from Feature 001)  
**Description**: Add tests for CSRF protection on settings route:

Test cases:
1. `test_settings_post_without_csrf_fails()` - POST without token returns 403
2. `test_settings_post_with_valid_csrf_succeeds()` - Valid token allows POST
3. `test_settings_post_with_invalid_csrf_fails()` - Invalid token returns 403

**Acceptance**:
- 3 new tests added to existing test file
- Tests pass or fail appropriately based on existing CSRF implementation

**Dependencies**: None (can run in parallel)

---

### T015 [P]: Unit Test - Session Updates
**File**: `tests/unit/test_session_management.py` (extend existing from Feature 001)  
**Description**: Add tests for session updates after profile changes:

Test cases:
1. `test_profile_update_refreshes_session()` - Name change updates session data
2. `test_email_change_maintains_session()` - Email change doesn't log out user
3. `test_session_includes_updated_profile()` - Session contains latest user data

**Acceptance**:
- 3 new tests added to existing session tests
- Tests FAIL (session update logic not implemented)

**Dependencies**: None (can run in parallel)

---

## Phase 3.3: Core Implementation (ONLY after Phase 3.2 tests are failing)

**GATE CHECK**: Before starting Phase 3.3, verify ALL tests in Phase 3.2 are written and FAILING.

### T016: Extend User Model with Profile Fields
**File**: `src/models/user.py`  
**Description**: Add new columns to User model as defined in `data-model.md`:

```python
bio = db.Column(db.Text, nullable=True)
profile_picture_data = deferred(db.Column(db.Text, nullable=True))
profile_picture_mime_type = db.Column(db.String(50), nullable=True)
updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, index=True)
```

Update `to_dict()` method with `include_picture` parameter.
Add `has_profile_picture()` method.

**Acceptance**:
- Model compiles without errors
- Can query User with new fields
- Lazy loading works for profile_picture_data
- Tests T016 related tests start passing

**Dependencies**: T001 (migration run), T006-T015 (tests written and failing)

---

### T017 [P]: Implement Image Encoding Function
**File**: `src/logic/image_utils.py`  
**Description**: Implement `encode_image()` function:

```python
def encode_image(file_bytes: bytes) -> str:
    """Convert image bytes to base64 string."""
    return base64.b64encode(file_bytes).decode('utf-8')
```

**Acceptance**:
- Function implemented
- Tests from T008 (test_encode_image_*) pass
- Handles JPEG, PNG, GIF correctly

**Dependencies**: T008 (tests failing), T003 (module structure)

---

### T018 [P]: Implement Image Decoding Function
**File**: `src/logic/image_utils.py`  
**Description**: Implement `decode_image()` function:

```python
def decode_image(base64_string: str) -> bytes:
    """Convert base64 string to image bytes."""
    return base64.b64decode(base64_string)
```

Handle invalid base64 gracefully (raise ValueError).

**Acceptance**:
- Function implemented
- Tests from T008 (test_decode_image_*) pass
- Raises appropriate exceptions for invalid input

**Dependencies**: T008 (tests failing), T003 (module structure)

---

### T019 [P]: Implement Image Validation Function
**File**: `src/logic/image_utils.py`  
**Description**: Implement `validate_image()` function using Pillow:

```python
def validate_image(file_bytes: bytes) -> tuple[bool, str]:
    """Validate image using Pillow, return (is_valid, mime_type_or_error)."""
    try:
        image = Image.open(io.BytesIO(file_bytes))
        # Check size, format
        # Return (True, f"image/{image.format.lower()}")
    except Exception as e:
        return (False, str(e))
```

Check file size < 5MB, format in [JPEG, PNG, GIF].

**Acceptance**:
- Function implemented with Pillow
- Tests from T008 (test_validate_image_*) pass
- Rejects invalid/oversized/malicious images

**Dependencies**: T008 (tests failing), T002 (Pillow installed), T003 (module structure)

---

### T020 [P]: Implement Image Sanitization Function
**File**: `src/logic/image_utils.py`  
**Description**: Implement `sanitize_image()` function:

```python
def sanitize_image(file_bytes: bytes) -> bytes:
    """Strip EXIF data, optionally resize, return sanitized bytes."""
    image = Image.open(io.BytesIO(file_bytes))
    # Remove EXIF: image.getexif().clear()
    # Optional: resize if > 800x800
    # Save to BytesIO and return bytes
```

**Acceptance**:
- Function implemented
- Tests from T008 (test_sanitize_image_*) pass
- EXIF data removed
- Image content preserved

**Dependencies**: T008 (tests failing), T002 (Pillow), T003 (module structure)

---

### T021: Implement ProfileService.get_user_profile()
**File**: `src/logic/profile_service.py`  
**Description**: Implement method to retrieve user profile:

```python
def get_user_profile(user_id: int, include_picture: bool = False) -> dict:
    """Get user profile data, optionally including picture."""
    if include_picture:
        user = User.query.get(user_id)
    else:
        user = User.query.options(defer('profile_picture_data')).get(user_id)
    
    return user.to_dict(include_picture=include_picture) if user else None
```

**Acceptance**:
- Method implemented
- Tests from T009 (test_get_user_profile_*) pass
- Lazy loading works correctly

**Dependencies**: T009 (tests failing), T016 (User model extended), T004 (service structure)

---

### T022: Implement ProfileService.validate_profile_data()
**File**: `src/logic/profile_service.py`  
**Description**: Implement validation method:

```python
def validate_profile_data(data: dict) -> tuple[bool, dict]:
    """Validate profile update data, return (is_valid, errors)."""
    errors = {}
    
    # Validate full_name (required, 2-100 chars)
    # Validate email (required, valid format, unique)
    # Validate bio (optional, max 500 chars)
    # Validate password (if changing: min 8 chars, complexity)
    # Validate profile_picture_data (if present: valid base64, size)
    
    return (len(errors) == 0, errors)
```

Use validators from `src/utils/validators.py`.

**Acceptance**:
- Method implemented
- Tests from T009 (test_validate_profile_data_*) pass
- Returns field-specific error messages

**Dependencies**: T009 (tests failing), T010 (validator tests), T004 (service structure)

---

### T023: Implement ProfileService.detect_concurrent_edit()
**File**: `src/logic/profile_service.py`  
**Description**: Implement concurrent edit detection:

```python
def detect_concurrent_edit(user: User, submitted_updated_at: str) -> bool:
    """Return True if user.updated_at is newer than submitted timestamp."""
    from dateutil.parser import parse
    submitted = parse(submitted_updated_at)
    return user.updated_at > submitted
```

**Acceptance**:
- Method implemented
- Tests from T009 (test_detect_concurrent_edit_*) pass
- Correctly compares ISO 8601 timestamps

**Dependencies**: T009 (tests failing), T016 (updated_at field), T004 (service structure)

---

### T024: Implement ProfileService.update_profile()
**File**: `src/logic/profile_service.py`  
**Description**: Implement main profile update logic:

```python
def update_profile(user_id: int, data: dict, submitted_updated_at: str) -> dict:
    """Update user profile with validation and concurrent edit detection."""
    user = User.query.get(user_id)
    
    # Detect concurrent edit (raise exception if conflict)
    # Validate data
    # Update fields: full_name, email, bio, password, profile_picture
    # Hash password with bcrypt if changing
    # Encode image with image_utils if uploading
    # Save to database
    # Return updated user dict
```

Handle email change notifications (call separate method).

**Acceptance**:
- Method implemented
- Tests from T009 (test_update_profile_*) pass
- Integrates with image_utils for picture encoding
- Raises exception on concurrent edit
- Returns updated user data

**Dependencies**: T009 (tests failing), T017-T020 (image utils), T021-T023 (other service methods), T004 (service structure)

---

### T025: Implement ProfileService.send_email_change_notifications()
**File**: `src/logic/profile_service.py`  
**Description**: Implement email notification logic:

```python
def send_email_change_notifications(old_email: str, new_email: str) -> None:
    """Send notification emails to both old and new email addresses."""
    # Import EmailService (from Feature 001 or create minimal version)
    # Send to old email: "Your email was changed to {new_email}"
    # Send to new email: "Your email address was changed from {old_email}"
    # Queue for async sending (simple in-memory queue for MVP)
```

**Acceptance**:
- Method implemented
- Tests from T013 (email notification tests) pass
- Emails queued/sent asynchronously
- Templates used for email content

**Dependencies**: T013 (tests failing), T004 (service structure), existing email service from Feature 001

---

### T026: Implement GET /settings Route
**File**: `src/controllers/settings_routes.py`  
**Description**: Implement GET endpoint:

```python
@settings_bp.route('/settings', methods=['GET'])
@login_required
def get_settings():
    """Display personal settings page."""
    user_id = session.get('user_id')
    user_data = ProfileService.get_user_profile(user_id, include_picture=True)
    
    return render_template('privates/settings/index.html', user=user_data)
```

**Acceptance**:
- Route implemented
- Tests from T006 (GET contract tests) pass
- Returns 200 with user data for authenticated users
- Returns 401 for unauthenticated users
- Includes CSRF token in template

**Dependencies**: T006 (tests failing), T021 (get_user_profile), T005 (route structure), T016 (User model)

---

### T027: Implement POST /settings Route
**File**: `src/controllers/settings_routes.py`  
**Description**: Implement POST endpoint:

```python
@settings_bp.route('/settings', methods=['POST'])
@login_required
@csrf_protect
def update_settings():
    """Update user profile."""
    user_id = session.get('user_id')
    data = request.get_json()
    
    try:
        updated_user = ProfileService.update_profile(
            user_id, 
            data, 
            data.get('updated_at')
        )
        
        # Update session with new user data
        session['user_name'] = updated_user['full_name']
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': updated_user
        }), 200
        
    except ConcurrentEditError as e:
        return jsonify({
            'error': 'Profile was modified by another session',
            'current_data': e.current_data,
            'conflicting_fields': e.fields
        }), 409
    except ValidationError as e:
        return jsonify({'error': str(e), 'errors': e.errors}), 400
```

Handle all error cases per contract (400, 401, 403, 409, 422).

**Acceptance**:
- Route implemented
- Tests from T007 (POST contract tests) pass
- All status codes handled correctly
- CSRF protection active
- Session updated with new data

**Dependencies**: T007 (tests failing), T024 (update_profile), T005 (route structure), existing CSRF utilities

---

### T028: Create Settings Template
**File**: `src/templates/privates/settings/index.html`  
**Description**: Create Jinja2 template extending `private.html`:

```html
{% extends "bases/private.html" %}

{% block content %}
<div class="container">
    <h1>Personal Settings</h1>
    
    <form id="settings-form" method="POST" action="{{ url_for('settings.update_settings') }}">
        <!-- CSRF token -->
        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
        <input type="hidden" name="updated_at" value="{{ user.updated_at }}">
        
        <!-- Full Name -->
        <div class="form-group">
            <label for="full_name">Full Name</label>
            <input type="text" id="full_name" name="full_name" value="{{ user.full_name }}" required>
        </div>
        
        <!-- Email -->
        <!-- Bio -->
        <!-- Current Password (for email/password changes) -->
        <!-- New Password -->
        <!-- Profile Picture Upload -->
        
        <button type="submit">Save</button>
        <button type="button" onclick="window.history.back()">Cancel</button>
    </form>
    
    <div id="preview"></div>
</div>
{% endblock %}
```

**Acceptance**:
- Template created extending private.html
- All form fields present
- Pre-populated with user data
- CSRF token included
- Hidden updated_at field for concurrent edit detection

**Dependencies**: T026 (GET route), existing private.html base template

---

### T029 [P]: Create Settings CSS
**File**: `src/static/css/settings.css`  
**Description**: Create stylesheet for settings page:

```css
/* Settings page styles */
.settings-form {
    max-width: 600px;
    margin: 0 auto;
}

.form-group {
    margin-bottom: 1.5rem;
}

.error-message {
    color: #dc3545;
    font-size: 0.875rem;
}

#preview img {
    max-width: 200px;
    border-radius: 50%;
}

.character-count {
    font-size: 0.75rem;
    color: #6c757d;
}

.conflict-warning {
    background: #fff3cd;
    border: 1px solid #ffc107;
    padding: 1rem;
    margin-bottom: 1rem;
}
```

**Acceptance**:
- CSS file created
- Styles for form, errors, preview, conflict warning
- Responsive design (mobile-friendly)

**Dependencies**: None (static asset, can be parallel)

---

### T030 [P]: Create Settings JavaScript
**File**: `src/static/script/settings.js`  
**Description**: Create client-side validation and image preview:

```javascript
// Image preview
document.getElementById('profile_picture').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        // Check size
        if (file.size > 5 * 1024 * 1024) {
            alert('Warning: Image exceeds 5MB limit');
        }
        
        // Preview
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('preview').innerHTML = 
                `<img src="${e.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(file);
    }
});

// Character counter for bio
document.getElementById('bio').addEventListener('input', function(e) {
    const count = e.target.value.length;
    document.getElementById('bio-count').textContent = `${count}/500`;
    if (count > 500) {
        e.target.classList.add('error');
    } else {
        e.target.classList.remove('error');
    }
});

// Unsaved changes warning
let formChanged = false;
document.getElementById('settings-form').addEventListener('change', () => {
    formChanged = true;
});

window.addEventListener('beforeunload', (e) => {
    if (formChanged) {
        e.preventDefault();
        e.returnValue = '';
    }
});
```

**Acceptance**:
- JavaScript file created
- Image preview working
- Character counter working
- Unsaved changes warning working
- File size validation

**Dependencies**: None (static asset, can be parallel)

---

### T031: Add Validators to Utils
**File**: `src/utils/validators.py` (extend existing)  
**Description**: Add new validation functions:

```python
def validate_bio(bio: str) -> bool:
    """Validate bio length and sanitize."""
    if not bio:
        return True  # Optional field
    if len(bio) > 500:
        return False
    # Sanitize XSS
    return True

def validate_password_strength(password: str) -> bool:
    """Validate password meets security requirements."""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True
```

**Acceptance**:
- Functions added to existing validators.py
- Tests from T010 pass
- Used by ProfileService validation

**Dependencies**: T010 (tests failing), existing validators.py from Feature 001

---

## Phase 3.4: Integration & Polish

### T032: Integrate Session Management ✅
**File**: `src/controllers/settings_routes.py`  
**Description**: Update session data when profile changes:

In POST /settings handler, after successful update:
```python
# Update session with new user data
session['user_name'] = updated_user['full_name']
session['user_email'] = updated_user['email']
# Update CoatHanger table with new session data
```

**Acceptance**:
- Session updates after profile change ✅
- Tests from T015 (session update tests) pass ✅
- User doesn't get logged out on email change ✅
- Updated name appears in navigation immediately ✅

**Dependencies**: T027 (POST route), T015 (tests), existing session management from Feature 001

**Status**: COMPLETE - Session and CoatHanger table updated in POST route

---

### T033: Add CSRF Protection to POST Route ✅
**File**: `src/controllers/settings_routes.py`  
**Description**: Ensure `@csrf_protect` decorator applied to POST /settings.

Verify CSRF token checked in:
- Form submissions
- JSON API calls
- Returns 403 on invalid/missing token

**Acceptance**:
- CSRF decorator active ✅
- Tests from T014 pass ✅
- Token validated before processing update ✅

**Dependencies**: T027 (POST route), T014 (tests), existing CSRF utils from Feature 001

**Status**: COMPLETE - @csrf_protect decorator already applied

---

### T034: Create Email Templates ✅
**Files**: 
- `src/templates/emails/email_change_old.html`
- `src/templates/emails/email_change_new.html`

**Description**: Create HTML email templates for notifications:

**email_change_old.html**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Email Address Changed</title>
</head>
<body>
    <h2>Your Email Address Was Changed</h2>
    <p>Your email address was changed from <strong>{{ old_email }}</strong> to <strong>{{ new_email }}</strong>.</p>
    <p>Date: {{ change_date }}</p>
    <p><strong>If you did not make this change, please contact support immediately.</strong></p>
</body>
</html>
```

**email_change_new.html**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Confirm Your New Email Address</title>
</head>
<body>
    <h2>Your Email Address Was Updated</h2>
    <p>Your email address was successfully changed to <strong>{{ new_email }}</strong>.</p>
    <p>You can now use this email to log in.</p>
</body>
</html>
```

**Acceptance**:
- Both templates created ✅
- Templates include all required variables ✅
- Tests from T013 pass (emails sent with correct content) ✅

**Dependencies**: T025 (send_email_change_notifications), T013 (tests)

**Status**: COMPLETE - Email templates created, ProfileService.send_email_change_notifications updated to use them

---

### T035: Error Handling and Logging ✅
**File**: `src/controllers/settings_routes.py`, `src/logic/profile_service.py`  
**Description**: Add comprehensive error handling and logging:

```python
import logging

logger = logging.getLogger(__name__)

# In routes
try:
    updated_user = ProfileService.update_profile(...)
except ConcurrentEditError as e:
    logger.warning(f"Concurrent edit detected for user {user_id}")
    return jsonify(...), 409
except ValidationError as e:
    logger.info(f"Validation error for user {user_id}: {e.errors}")
    return jsonify(...), 400
except Exception as e:
    logger.error(f"Unexpected error updating profile: {str(e)}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500
```

**Acceptance**:
- All exceptions caught and logged ✅
- Appropriate log levels used ✅
- User-friendly error messages returned ✅
- No sensitive data in logs ✅

**Dependencies**: T027 (POST route), T024 (update_profile)

**Status**: COMPLETE - Comprehensive logging added to routes and ProfileService with appropriate log levels

---

## Phase 3.5: Validation & Documentation

### T036: Run All Tests and Fix Failures
**Files**: All test files  
**Description**: Execute complete test suite:

```bash
pytest tests/contract/test_settings_get.py -v
pytest tests/contract/test_settings_post.py -v
pytest tests/unit/test_image_utils.py -v
pytest tests/unit/test_profile_service.py -v
pytest tests/unit/test_validators.py -v
pytest tests/integration/test_profile_update_flow.py -v
pytest tests/integration/test_concurrent_edit.py -v
pytest tests/integration/test_email_notification.py -v
```

Fix any remaining test failures.

**Acceptance**:
- All contract tests pass ✅
- All unit tests pass ✅
- All integration tests pass ✅
- Code coverage > 80%

**Dependencies**: T006-T015 (tests), T016-T035 (implementation)

---

### T037 [P]: Performance Testing
**File**: `tests/performance/test_settings_performance.py`  
**Description**: Create performance tests:

```python
def test_settings_page_load_time():
    """Verify page loads in < 500ms."""
    # Measure GET /settings response time
    assert response_time < 500  # milliseconds

def test_profile_update_time():
    """Verify profile update completes in < 2 seconds."""
    # Measure POST /settings with image upload
    assert response_time < 2000  # milliseconds

def test_image_encoding_time():
    """Verify 5MB image encodes in < 1 second."""
    # Measure encode_image() with 5MB file
    assert encoding_time < 1000  # milliseconds
```

**Acceptance**:
- All 3 performance tests created
- Tests pass (meet performance targets)
- Performance documented in test output

**Dependencies**: T026-T027 (routes), T017-T020 (image utils)

---

### T038 [P]: Execute Quickstart Manual Tests
**File**: `specs/003-personal-settings-i/quickstart.md`  
**Description**: Execute all 10 manual test scenarios from quickstart.md:

1. View Personal Settings Page
2. Update Full Name
3. Update Bio
4. Upload Profile Picture
5. Change Email Address
6. Change Password
7. Validation Errors Preserved Form Data
8. Concurrent Edit Detection
9. Cancel Button Discards Changes
10. Unsaved Changes Warning

Document results in quickstart.md (check boxes).

**Acceptance**:
- All 10 scenarios executed manually
- All scenarios pass ✅
- Screenshots captured (optional)
- Results documented in quickstart.md

**Dependencies**: T016-T035 (all implementation complete)

---

### T039 [P]: Update Documentation
**File**: `docs/features.md` or `README.md`  
**Description**: Document Feature 003 in project documentation:

```markdown
## Feature 003: User Profile & Personal Settings

Authenticated users can view and edit their profile information including:
- Full name, email address
- Bio/description (up to 500 characters)
- Password (with strength validation)
- Profile picture (JPEG/PNG/GIF, max 5MB, stored as base64)

**Key Features**:
- Concurrent edit detection (optimistic locking)
- Email notifications on email changes
- Client-side and server-side validation
- CSRF protection
- Image validation and EXIF stripping

**Routes**:
- `GET /settings` - Display settings page
- `POST /settings` - Update profile

**Dependencies**: Pillow==10.0.0
```

**Acceptance**:
- Documentation updated
- Feature described clearly
- API routes documented
- Dependencies listed

**Dependencies**: T016-T035 (implementation complete)

---

### T040 [P]: Code Quality Review
**Description**: Review all code for quality and constitutional compliance:

**Checklist**:
- [ ] MVC separation maintained (thin controllers, thick logic, thin models)
- [ ] No business logic in controllers or templates
- [ ] All functions have docstrings and type hints
- [ ] PEP 8 compliance (run `black` formatter)
- [ ] No hardcoded values (use config)
- [ ] Error messages are user-friendly
- [ ] Sensitive data not logged
- [ ] Database queries use parameterized queries (SQLAlchemy)
- [ ] CSRF protection on state-changing operations
- [ ] XSS prevention (input sanitization, output escaping)

**Acceptance**:
- All checklist items verified ✅
- Code formatted with `black`
- No linting errors (`flake8`)
- Constitutional compliance verified

**Dependencies**: T016-T035 (all code written)

---

## Task Dependencies Graph

```
Setup Phase (T001-T005)
├── T001: Database Migration
├── T002: Install Pillow
├── T003 [P]: Image Utils Structure
├── T004 [P]: Profile Service Structure
└── T005 [P]: Settings Controller Structure

Tests Phase (T006-T015) - ALL PARALLEL, depend on setup
├── T006 [P]: Contract Test GET
├── T007 [P]: Contract Test POST
├── T008 [P]: Unit Test Image Utils
├── T009 [P]: Unit Test Profile Service
├── T010 [P]: Unit Test Validators
├── T011 [P]: Integration Test Profile Update
├── T012 [P]: Integration Test Concurrent Edit
├── T013 [P]: Integration Test Email
├── T014 [P]: Unit Test CSRF
└── T015 [P]: Unit Test Session

Core Implementation (T016-T031) - depends on tests written
├── T016: Extend User Model → depends on T001
├── T017 [P]: Implement encode_image → depends on T008, T003
├── T018 [P]: Implement decode_image → depends on T008, T003
├── T019 [P]: Implement validate_image → depends on T008, T002, T003
├── T020 [P]: Implement sanitize_image → depends on T008, T002, T003
├── T021: Implement get_user_profile → depends on T009, T016, T004
├── T022: Implement validate_profile_data → depends on T009, T010, T004
├── T023: Implement detect_concurrent_edit → depends on T009, T016, T004
├── T024: Implement update_profile → depends on T009, T017-T023, T004
├── T025: Implement send_email_notifications → depends on T013, T004
├── T026: Implement GET /settings → depends on T006, T021, T005, T016
├── T027: Implement POST /settings → depends on T007, T024, T005
├── T028: Create Settings Template → depends on T026
├── T029 [P]: Create Settings CSS
├── T030 [P]: Create Settings JavaScript
└── T031: Add Validators → depends on T010

Integration (T032-T035) - depends on core
├── T032: Integrate Session → depends on T027, T015
├── T033: Add CSRF Protection → depends on T027, T014
├── T034: Create Email Templates → depends on T025, T013
└── T035: Error Handling → depends on T027, T024

Validation (T036-T040) - depends on all implementation
├── T036: Run All Tests → depends on T006-T035
├── T037 [P]: Performance Testing → depends on T026-T027, T017-T020
├── T038 [P]: Execute Quickstart → depends on T016-T035
├── T039 [P]: Update Documentation → depends on T016-T035
└── T040 [P]: Code Quality Review → depends on T016-T035
```

---

## Parallel Execution Examples

**Phase 3.1 - Setup (3 parallel tasks)**:
```
Task: "Create Image Utils Module Structure in src/logic/image_utils.py"
Task: "Create Profile Service Module Structure in src/logic/profile_service.py"
Task: "Create Settings Controller Structure in src/controllers/settings_routes.py"
```

**Phase 3.2 - Tests (10 parallel tasks)**:
```
Task: "Contract Test GET /settings in tests/contract/test_settings_get.py"
Task: "Contract Test POST /settings in tests/contract/test_settings_post.py"
Task: "Unit Test Image Encoding in tests/unit/test_image_utils.py"
Task: "Unit Test Profile Service in tests/unit/test_profile_service.py"
Task: "Unit Test Validators in tests/unit/test_validators.py"
Task: "Integration Test Profile Update Flow in tests/integration/test_profile_update_flow.py"
Task: "Integration Test Concurrent Edit in tests/integration/test_concurrent_edit.py"
Task: "Integration Test Email Notifications in tests/integration/test_email_notification.py"
Task: "Unit Test CSRF Protection in tests/unit/test_csrf_utils.py"
Task: "Unit Test Session Updates in tests/unit/test_session_management.py"
```

**Phase 3.3 - Image Utils (4 parallel tasks)**:
```
Task: "Implement Image Encoding Function in src/logic/image_utils.py"
Task: "Implement Image Decoding Function in src/logic/image_utils.py"
Task: "Implement Image Validation Function in src/logic/image_utils.py"
Task: "Implement Image Sanitization Function in src/logic/image_utils.py"
```

**Phase 3.5 - Final Validation (4 parallel tasks)**:
```
Task: "Performance Testing in tests/performance/test_settings_performance.py"
Task: "Execute Quickstart Manual Tests in specs/003-personal-settings-i/quickstart.md"
Task: "Update Documentation in docs/features.md"
Task: "Code Quality Review - verify MVC compliance and formatting"
```

---

## Execution Notes

**TDD Enforcement**: 
- Phase 3.2 (all tests) MUST be completed before starting Phase 3.3 (implementation)
- Verify tests are failing before implementing features
- Re-run tests after each implementation task

**Parallel Execution**:
- Tasks marked [P] can be executed simultaneously by different team members or AI agents
- Non-parallel tasks must be executed sequentially (file conflicts or dependencies)

**Git Workflow**:
- Commit after completing each task
- Use descriptive commit messages: "T026: Implement GET /settings route"
- Create PR after Phase 3.3 complete, merge after Phase 3.5 validation

**Constitutional Compliance**:
- T040 (Code Quality Review) verifies MVC separation maintained
- Controllers remain thin (routing only)
- Logic layer contains all business logic
- Models remain thin (schema only)

---

## Success Criteria

**Feature Complete When**:
- [ ] All 40 tasks (T001-T040) completed
- [ ] All tests passing (contract, unit, integration)
- [ ] Performance targets met (< 500ms page load, < 2s updates)
- [ ] Quickstart scenarios all pass
- [ ] Constitutional compliance verified
- [ ] Documentation updated
- [ ] Code quality review passed

**Ready for**: Feature 004 or production deployment (after Feature 001-003 complete)
