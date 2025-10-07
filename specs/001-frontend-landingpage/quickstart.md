# Quickstart: Frontend Landing Page System

## Setup and Testing Guide

### Prerequisites
- Python 3.11+
- SQLite (included with Python)
- Web browser for testing

### Installation
```bash
# Install dependencies
pip install flask sqlalchemy bcrypt

# Initialize database
python -c "from src.models import db; db.create_all()"

# Run application
python run.py
```

### Manual Testing Scenarios

#### Scenario 1: New Visitor Experience
**Objective**: Verify landing page displays correctly and navigation works

**Steps**:
1. Open browser to `http://localhost:5000`
2. **Verify**: Landing page loads with creative portfolio content
3. **Verify**: Navigation menu shows Home, About, Contact, Login/Register
4. Click "About" link
5. **Verify**: About page loads with detailed information
6. Click "Contact" link  
7. **Verify**: Contact page loads with form fields (name, email, subject, message)
8. **Verify**: All pages are mobile responsive

**Expected Results**:
- All pages load without errors
- Bootstrap styling applied consistently
- Navigation works between all pages
- Mobile responsive design functions properly

#### Scenario 2: User Registration Flow
**Objective**: Test complete user registration process

**Steps**:
1. Navigate to `/auth/register`
2. Fill form with valid data:
   - Email: `test@example.com`
   - Full Name: `Test User`
   - Password: `securepass123`
3. Submit form
4. **Verify**: Success message displayed
5. **Verify**: User redirected to landing page or dashboard
6. **Verify**: Navigation shows "Logout" instead of "Login/Register"

**Expected Results**:
- Registration succeeds with valid data
- Password properly hashed in database
- User automatically logged in after registration
- Session created in coat hanger table

#### Scenario 3: User Login Flow  
**Objective**: Test user authentication

**Steps**:
1. Navigate to `/auth/login`
2. Enter credentials from Scenario 2
3. Submit form
4. **Verify**: Login successful
5. **Verify**: User redirected appropriately
6. **Verify**: Session created with 10-minute timeout

**Expected Results**:
- Login succeeds with correct credentials
- Session hash stored in coat hanger table
- Updated_at timestamp tracks activity
- User remains logged in across page navigation

#### Scenario 4: Contact Form Submission
**Objective**: Test contact form functionality

**Steps**:
1. Navigate to `/contact`
2. Fill contact form:
   - Name: `Jane Doe`
   - Email: `jane@example.com`
   - Subject: `Portfolio Inquiry`
   - Message: `Interested in discussing a project collaboration.`
3. Submit form
4. **Verify**: Success message displayed
5. **Verify**: Confirmation email sent (check logs)
6. **Verify**: Message stored in database

**Expected Results**:
- Form validation works for all fields
- Success message appears on submission
- Confirmation email sent to submitter
- Contact message stored with timestamp

#### Scenario 5: Session Timeout
**Objective**: Verify automatic session expiration

**Steps**:
1. Login as user from Scenario 2
2. Wait 11 minutes (or adjust system time for testing)
3. Navigate to any page
4. **Verify**: User redirected to login page
5. **Verify**: Session marked as expired in database

**Expected Results**:
- Sessions automatically expire after 10 minutes
- Users redirected to login when session expires
- Expired sessions cleaned up in database

#### Scenario 6: Form Validation
**Objective**: Test client and server-side validation

**Steps**:
1. Test registration with invalid data:
   - Empty email field
   - Password less than 8 characters
   - Invalid email format
2. Test contact form with invalid data:
   - Empty required fields
   - Message too short (< 10 characters)
3. **Verify**: Validation errors displayed appropriately
4. **Verify**: Forms don't submit with invalid data

**Expected Results**:
- Client-side validation prevents submission
- Server-side validation provides backup
- Clear error messages guide user corrections
- CSRF protection active on all forms

### Database Verification

#### Check User Registration
```sql
SELECT id, email, full_name, created_at FROM user WHERE email = 'test@example.com';
```

#### Check Session Management
```sql
SELECT user_id, session_hash, created_at, updated_at FROM coat_hanger WHERE user_id = 1;
```

#### Check Contact Messages
```sql
SELECT name, email, subject, submitted_at, email_sent FROM contact_message ORDER BY submitted_at DESC;
```

### Performance Testing

#### Page Load Times
- **Target**: All pages load under 500ms
- **Test**: Use browser dev tools Network tab
- **Verify**: No unnecessary resource loading

#### Session Performance
- **Target**: Session validation under 50ms
- **Test**: Check database query performance
- **Verify**: Proper indexing on session_hash and user_id

### Security Testing

#### Password Security
- **Verify**: Passwords stored as bcrypt hashes
- **Test**: Check database for plaintext passwords (should be none)
- **Verify**: Password complexity requirements enforced

#### Session Security
- **Verify**: Session tokens are cryptographically secure
- **Test**: Attempt session fixation attacks
- **Verify**: Sessions properly invalidated on logout

#### CSRF Protection
- **Verify**: All forms include CSRF tokens
- **Test**: Submit forms without CSRF tokens (should fail)
- **Verify**: CSRF tokens change per session

### Browser Compatibility Testing

#### Desktop Browsers
- Chrome (latest)
- Firefox (latest)  
- Safari (latest)
- Edge (latest)

#### Mobile Browsers
- Mobile Chrome
- Mobile Safari
- Mobile Firefox

#### Responsive Design Testing
- Test all breakpoints: <576px, 576-768px, >768px
- Verify navigation menu collapse on mobile
- Check form usability on touch devices

### Troubleshooting Common Issues

#### Database Connection Errors
- Verify SQLite file permissions
- Check database initialization
- Confirm model relationships

#### Session Issues
- Check session configuration
- Verify coat hanger table creation
- Confirm session cleanup process

#### Email Delivery Problems
- Check email configuration (if using SMTP)
- Verify contact form validation
- Test with different email providers

### Success Criteria

**Functional Requirements Met**:
- ✅ All pages load and display correctly
- ✅ User registration and login work
- ✅ Contact form submits and sends confirmation
- ✅ Session management with 10-minute timeout
- ✅ Bootstrap responsive design implemented

**Non-Functional Requirements Met**:
- ✅ Performance targets achieved (<500ms page loads)
- ✅ Security measures implemented (password hashing, CSRF, session security)
- ✅ Mobile responsiveness across devices
- ✅ Database integrity maintained
- ✅ Error handling graceful and user-friendly