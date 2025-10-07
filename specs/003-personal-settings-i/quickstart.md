# Personal Settings Feature Quickstart

**Feature**: 003-personal-settings-i  
**Purpose**: Manual testing guide for user profile settings functionality  
**Prerequisites**: Feature 001 (authentication) complete, test database initialized

## Setup

1. **Start Flask development server**:
   ```bash
   python run.py
   ```

2. **Initialize test database** (if not already done):
   ```bash
   flask db upgrade  # Run migrations
   ```

3. **Create test user** (via registration or direct SQL):
   ```bash
   # Register via UI at http://localhost:5000/register
   # Or use existing test account from Feature 001
   ```

4. **Email service** (optional for email notification tests):
   - Configure SMTP settings in config
   - Or use mock email service for development

## Test Scenarios

### Scenario 1: View Personal Settings Page

**Objective**: Verify authenticated users can access settings page with pre-populated form

**Steps**:
1. Navigate to `http://localhost:5000/login`
2. Login with test credentials:
   - Email: `testuser@example.com`
   - Password: `TestPass123`
3. After login, navigate to `http://localhost:5000/settings`

**Expected Results**:
- ✅ Page loads successfully (< 500ms)
- ✅ Form displays with current user data:
  - Full name field pre-populated
  - Email field pre-populated
  - Bio field empty (or existing bio if set)
  - Profile picture placeholder (or existing picture)
- ✅ "Save" and "Cancel" buttons visible
- ✅ Navigation shows user's current name

---

### Scenario 2: Update Full Name

**Objective**: Verify users can change their full name

**Steps**:
1. From settings page (Scenario 1)
2. Change "Full Name" field to: `Jane Smith`
3. Click "Save" button

**Expected Results**:
- ✅ Success message displayed: "Profile updated successfully"
- ✅ Page remains on `/settings` or redirects back
- ✅ Form shows updated name: `Jane Smith`
- ✅ Navigation/header shows new name: `Jane Smith`
- ✅ Update completes in < 2 seconds

**Database Verification**:
```sql
SELECT full_name, updated_at FROM user WHERE email = 'testuser@example.com';
-- Expected: full_name = 'Jane Smith', updated_at = [recent timestamp]
```

---

### Scenario 3: Update Bio

**Objective**: Verify users can add/edit biography

**Steps**:
1. From settings page
2. Enter bio text (try ~200 characters):
   ```
   Full-stack developer with 5 years experience in Python, JavaScript, and cloud technologies. Passionate about building scalable web applications and contributing to open source projects.
   ```
3. Click "Save"

**Expected Results**:
- ✅ Success message displayed
- ✅ Bio saved successfully
- ✅ Bio displays in settings form on reload

**Edge Case - Bio Length Limit**:
1. Try entering 501+ characters in bio field
2. Click "Save"
3. **Expected**: Validation error message: "Bio must be 500 characters or less"
4. **Expected**: Character counter shows "501/500" (red)

---

### Scenario 4: Upload Profile Picture

**Objective**: Verify image upload, validation, and base64 storage

**Steps**:
1. From settings page
2. Click "Choose File" button for profile picture
3. Select a valid JPEG image (< 5MB): `test-profile.jpg`
4. **Expected**: Image preview appears immediately (client-side)
5. Click "Save" button

**Expected Results**:
- ✅ Image uploads successfully
- ✅ Success message displayed
- ✅ Profile picture appears in settings page
- ✅ Profile picture appears in navigation/header
- ✅ Upload completes in < 2 seconds (including encoding)

**Database Verification**:
```sql
SELECT 
    length(profile_picture_data) as base64_length,
    profile_picture_mime_type,
    substr(profile_picture_data, 1, 20) as preview
FROM user 
WHERE email = 'testuser@example.com';

-- Expected:
-- base64_length: 100000+ (depending on image size)
-- profile_picture_mime_type: 'image/jpeg'
-- preview: '/9j/4AAQSkZJRgABAQ...' (valid base64 start)
```

**Edge Case - Oversized Image**:
1. Try uploading image > 5MB
2. **Expected**: Client-side warning before upload: "Image exceeds 5MB limit"
3. If uploaded anyway: **Expected** Server validation error: "Image too large (max 5MB)"

**Edge Case - Invalid File Type**:
1. Try uploading non-image file (e.g., `document.pdf`)
2. **Expected**: Validation error: "Invalid file type. Allowed: JPEG, PNG, GIF"

---

### Scenario 5: Change Email Address

**Objective**: Verify email change with password confirmation and notifications

**Steps**:
1. From settings page
2. Change email from `testuser@example.com` to `newemail@example.com`
3. Enter current password in "Current Password" field: `TestPass123`
4. Click "Save"

**Expected Results**:
- ✅ Success message displayed
- ✅ Email updated in form
- ✅ Can logout and login with new email: `newemail@example.com`

**Email Notification Verification**:
- ✅ Email sent to OLD address (`testuser@example.com`):
  - Subject: "Email Address Changed"
  - Body contains: old email, new email, timestamp, "If this wasn't you" warning
- ✅ Email sent to NEW address (`newemail@example.com`):
  - Subject: "Confirm Your New Email Address"
  - Body contains: welcome message, security note

**Edge Case - Email Already Exists**:
1. Try changing email to another existing user's email
2. **Expected**: Validation error: "Email address already in use"

**Edge Case - Wrong Current Password**:
1. Enter wrong current password
2. **Expected**: Error message: "Current password is incorrect"
3. **Expected**: Email NOT changed

---

### Scenario 6: Change Password

**Objective**: Verify password change with proper validation

**Steps**:
1. From settings page
2. Enter current password: `TestPass123`
3. Enter new password: `NewSecurePass456`
4. Click "Save"
5. **Expected**: Success message displayed
6. Logout
7. Try logging in with OLD password: `TestPass123`
8. **Expected**: Login fails
9. Login with NEW password: `NewSecurePass456`
10. **Expected**: Login succeeds

**Edge Case - Weak Password**:
1. Try new password: `weak` (no uppercase, no number)
2. **Expected**: Validation error: "Password must contain uppercase, lowercase, and number"

**Edge Case - Password Too Short**:
1. Try new password: `Ab1` (only 3 characters)
2. **Expected**: Validation error: "Password must be at least 8 characters"

---

### Scenario 7: Validation Errors Preserved Form Data

**Objective**: Verify form data not lost on validation errors

**Steps**:
1. From settings page
2. Make multiple changes:
   - Full name: `Test User`
   - Bio: Write 200 character bio
   - Email: `invalid-email` (intentionally invalid)
3. Click "Save"

**Expected Results**:
- ✅ Validation error displayed for email field
- ✅ Full name still shows `Test User` (not reverted)
- ✅ Bio still shows the 200 characters (not lost)
- ✅ Only email field highlighted as error

---

### Scenario 8: Concurrent Edit Detection

**Objective**: Verify system detects and handles concurrent modifications

**Setup**: Open two browser windows (or incognito + regular)

**Steps**:
1. **Browser A**: Login as `testuser@example.com`, navigate to `/settings`
2. **Browser B**: Login as same user, navigate to `/settings`
3. **Browser B**: Change full name to `User B`, click "Save"
4. **Browser B**: Success message shown, name updated
5. **Browser A** (without refreshing): Change full name to `User A`, click "Save"

**Expected Results**:
- ✅ **Browser A**: Shows conflict warning (status 409)
- ✅ Conflict message: "Profile was modified by another session"
- ✅ Shows current data: `Full Name: User B`
- ✅ Shows conflicting fields list
- ✅ Two options presented:
  - "Reload Form" (discard changes, use latest data)
  - "Force Overwrite" (save changes anyway)

**Test Resolution - Reload**:
1. Click "Reload Form" button
2. **Expected**: Form refreshes with `User B` name
3. **Expected**: User can now make changes safely

**Test Resolution - Force Overwrite**:
1. Instead, click "Force Overwrite" button
2. **Expected**: `User A` name saved
3. **Expected**: `updated_at` timestamp updated

---

### Scenario 9: Cancel Button Discards Changes

**Objective**: Verify cancel button reverts changes

**Steps**:
1. From settings page
2. Change full name to `Temporary Name`
3. Change bio to `Temporary bio text`
4. Click "Cancel" button

**Expected Results**:
- ✅ Form reverts to original values (no changes saved)
- ✅ Navigates away from settings page (e.g., to dashboard)
- ✅ Confirmation prompt if unsaved changes: "Discard changes?"

---

### Scenario 10: Unsaved Changes Warning

**Objective**: Verify browser warns when navigating away with unsaved changes

**Steps**:
1. From settings page
2. Change full name to `Test Name`
3. Without saving, click browser back button (or try to navigate to another page)

**Expected Results**:
- ✅ Browser shows warning dialog: "You have unsaved changes. Leave page?"
- ✅ If "Stay on Page": Remain on settings page with changes intact
- ✅ If "Leave Page": Navigate away, changes discarded

---

## Performance Testing

### Page Load Performance
**Test**: Measure settings page load time
```
1. Clear browser cache
2. Open DevTools Network tab
3. Navigate to /settings
4. Check "DOMContentLoaded" time
```
**Expected**: < 500ms (constitutional requirement)

### Profile Update Performance
**Test**: Measure profile update time (with image upload)
```
1. Upload 4MB JPEG image
2. Change name and bio
3. Measure time from "Save" click to success message
```
**Expected**: < 2 seconds (spec requirement)

### Image Encoding Performance
**Test**: Measure base64 encoding time
```
1. Select 5MB image (maximum allowed)
2. Measure time from file selection to preview display
```
**Expected**: < 1 second for client-side preview

---

## Security Testing

### CSRF Protection
**Test**: Verify CSRF token required for POST
```
1. Inspect HTML source of settings form
2. Verify CSRF token present in hidden field
3. Try POST request without CSRF token (using cURL or Postman)
```
**Expected**: 403 Forbidden error

### XSS Prevention
**Test**: Verify bio sanitization
```
1. Enter bio with HTML/JavaScript:
   Bio: <script>alert('XSS')</script>Hello world
2. Save and reload page
```
**Expected**: Script tags stripped, displays: "Hello world"

### Image Security
**Test**: Verify non-image files rejected
```
1. Rename executable file to .jpg: malware.exe → malware.jpg
2. Try uploading
```
**Expected**: Validation error (Pillow detects invalid image format)

---

## Cleanup

After testing, reset test data if needed:
```sql
UPDATE user 
SET 
    full_name = 'Test User',
    email = 'testuser@example.com',
    bio = NULL,
    profile_picture_data = NULL,
    profile_picture_mime_type = NULL
WHERE email LIKE 'test%';
```

---

## Success Criteria Checklist

- [ ] All 10 scenarios pass
- [ ] Page load < 500ms
- [ ] Profile updates < 2 seconds
- [ ] Validation errors clear and helpful
- [ ] Concurrent edit detection works
- [ ] Email notifications sent
- [ ] Password change works
- [ ] Image upload and base64 storage works
- [ ] CSRF protection active
- [ ] XSS sanitization active
- [ ] Form data preserved on errors
- [ ] Unsaved changes warning works

**Feature Ready**: ✅ When all checkboxes complete
