# Contact Form API Contract

## POST /contact

**Purpose**: Submit contact form message

**Request**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Inquiry about portfolio",
  "message": "I'm interested in discussing a potential project collaboration."
}
```

**Request Validation**:
- `name`: Required, 2-100 characters
- `email`: Required, valid email format, max 120 chars
- `subject`: Required, 5-200 characters  
- `message`: Required, 10-2000 characters

**Success Response** (201 Created):
```json
{
  "success": true,
  "message": "Message sent successfully. You will receive a confirmation email shortly.",
  "contact_id": 456
}
```

**Error Responses**:

400 Bad Request - Validation Error:
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "name": ["Name must be at least 2 characters"],
    "email": ["Invalid email format"],
    "message": ["Message must be at least 10 characters"]
  }
}
```

422 Unprocessable Entity - Invalid Data:
```json
{
  "success": false,
  "message": "Subject cannot be empty"
}
```

500 Internal Server Error - Email Delivery Issues:
```json
{
  "success": false,
  "message": "Message saved but confirmation email failed to send"
}
```

## Rate Limiting

**Limits**:
- 5 submissions per IP address per hour
- 2 submissions per email address per day

**Rate Limit Response** (429 Too Many Requests):
```json
{
  "success": false,
  "message": "Too many submissions. Please try again later.",
  "retry_after": 3600
}
```

## Email Confirmation

**Confirmation Email Content**:
- Sent to submitter's email address
- Contains copy of submitted message
- Includes expected response timeframe
- Provides contact information for urgent matters

**Email Delivery Tracking**:
- Asynchronous email sending
- Delivery status stored in database
- Retry mechanism for failed deliveries

## Security Measures

**CSRF Protection**: Required for all form submissions
**Input Sanitization**: All text fields sanitized for XSS prevention
**Spam Prevention**: Basic honeypot field and rate limiting
**Data Validation**: Server-side validation of all fields

## Headers

**Request Headers**:
- `Content-Type: application/json` or `application/x-www-form-urlencoded`
- `X-CSRF-Token: [token]` (required)

**Response Headers**:
- `Content-Type: application/json`
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`