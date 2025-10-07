# Authentication API Contract

## POST /auth/register

**Purpose**: User registration endpoint

**Request**:
```json
{
  "email": "user@example.com",
  "full_name": "John Doe", 
  "password": "securepassword123"
}
```

**Request Validation**:
- `email`: Required, valid email format, max 120 chars, unique
- `full_name`: Required, 2-100 characters
- `password`: Required, minimum 8 characters

**Success Response** (201 Created):
```json
{
  "success": true,
  "message": "Account created successfully",
  "user": {
    "id": 123,
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

**Error Responses**:

400 Bad Request - Validation Error:
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "email": ["Email already exists"],
    "password": ["Password must be at least 8 characters"]
  }
}
```

422 Unprocessable Entity - Invalid Data:
```json
{
  "success": false,
  "message": "Invalid email format"
}
```

## POST /auth/login

**Purpose**: User authentication endpoint

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Request Validation**:
- `email`: Required, valid email format
- `password`: Required

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 123,
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

**Error Responses**:

401 Unauthorized - Invalid Credentials:
```json
{
  "success": false,
  "message": "Invalid email or password"
}
```

400 Bad Request - Missing Fields:
```json
{
  "success": false,
  "message": "Email and password are required"
}
```

## POST /auth/logout

**Purpose**: User logout endpoint

**Request**: No body required (uses session)

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Logout successful"
}
```

**Error Responses**:

401 Unauthorized - Not Logged In:
```json
{
  "success": false,
  "message": "No active session"
}
```

## GET /auth/session

**Purpose**: Check current session status

**Request**: No body required (uses session)

**Success Response** (200 OK):
```json
{
  "success": true,
  "authenticated": true,
  "user": {
    "id": 123,
    "email": "user@example.com",
    "full_name": "John Doe"
  },
  "session_expires_in": 540
}
```

**Response - Not Authenticated** (200 OK):
```json
{
  "success": true,
  "authenticated": false
}
```

## Headers

**All Requests**:
- `Content-Type: application/json`
- `X-Requested-With: XMLHttpRequest` (for AJAX requests)

**All Responses**:
- `Content-Type: application/json`
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`

## Session Management

**Session Cookie**:
- Name: `session`
- HttpOnly: true
- Secure: true (production)
- SameSite: Lax
- Max-Age: 600 seconds (10 minutes)

**CSRF Protection**:
- All state-changing requests require CSRF token
- Token provided in form or response header
- Token validation on server side