# Page Routes Contract

## GET /

**Purpose**: Landing page with creative portfolio showcase

**Request**: No parameters required

**Response** (200 OK):
```html
<!DOCTYPE html>
<html>
<!-- Creative portfolio landing page with Bootstrap styling -->
</html>
```

**Content Requirements**:
- Hero section with portfolio highlights
- Navigation to about, contact, login/register
- Responsive Bootstrap grid layout
- Creative work showcase section
- Call-to-action buttons

## GET /about

**Purpose**: About page with detailed information

**Request**: No parameters required

**Response** (200 OK):
```html
<!DOCTYPE html>
<html>
<!-- About page extending public.html base template -->
</html>
```

**Content Requirements**:
- Personal/professional background
- Skills and expertise
- Work philosophy or approach
- Professional experience highlights

## GET /contact

**Purpose**: Contact page with form

**Request**: No parameters required

**Response** (200 OK):
```html
<!DOCTYPE html>
<html>
<!-- Contact page with form extending public.html base template -->
</html>
```

**Content Requirements**:
- Contact form with name, email, subject, message fields
- CSRF token embedded in form
- Bootstrap form styling
- Client-side validation
- Success/error message display area

## GET /auth/login

**Purpose**: Login page for existing users

**Request**: No parameters required

**Response** (200 OK):
```html
<!DOCTYPE html>
<html>
<!-- Login page extending public.html base template -->
</html>
```

**Content Requirements**:
- Email and password input fields
- Bootstrap form styling
- "Remember me" option
- Link to registration page
- CSRF protection
- Client-side validation

## GET /auth/register

**Purpose**: Registration page for new users

**Request**: No parameters required

**Response** (200 OK):
```html
<!DOCTYPE html>
<html>
<!-- Registration page extending public.html base template -->
</html>
```

**Content Requirements**:
- Email, full name, and password input fields
- Password confirmation field
- Bootstrap form styling
- Link to login page
- CSRF protection
- Client-side validation with password strength indicator

## Template Structure

**Base Template** (public.html):
- Bootstrap CSS/JS includes
- Navigation menu (responsive)
- Footer with copyright
- Meta tags for SEO and mobile
- CSRF token meta tag

**Navigation Menu**:
- Home (landing page)
- About
- Contact
- Login/Register (conditional based on auth status)
- Logout (authenticated users only)

## Error Pages

**404 Not Found**:
```html
<!DOCTYPE html>
<html>
<!-- 404 page extending public.html base template -->
</html>
```

**500 Internal Server Error**:
```html
<!DOCTYPE html>
<html>
<!-- 500 page extending public.html base template -->
</html>
```

## Security Headers

**All Page Responses**:
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`

## Mobile Responsiveness

**Bootstrap Breakpoints**:
- Mobile: <576px
- Tablet: 576px-768px  
- Desktop: >768px

**Requirements**:
- Navigation collapses to hamburger menu on mobile
- Forms stack vertically on small screens
- Images and content scale appropriately
- Touch-friendly button and link sizes