# PlayaTewsIdentityMasker API Documentation

## Overview

The PlayaTewsIdentityMasker API is a secure RESTful API for real-time face swapping and identity masking operations. It follows RESTful principles and implements comprehensive security measures.

**Base URL**: `http://localhost:8000`  
**API Version**: v1  
**Documentation**: `/docs` (Swagger UI) or `/redoc` (ReDoc)

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. All protected endpoints require a valid Bearer token in the Authorization header.

### Authentication Flow

1. **Register**: Create a new user account
2. **Login**: Authenticate and receive access/refresh tokens
3. **Use**: Include Bearer token in requests to protected endpoints

### Headers

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Endpoints

### Health & Status

#### GET /
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01 12:00:00"
}
```

#### GET /health
Detailed health check.

**Response:** Same as root endpoint.

#### GET /api/v1/status
API status and feature availability.

**Response:**
```json
{
  "status": "operational",
  "version": "1.0.0",
  "timestamp": "2024-01-01 12:00:00",
  "features": {
    "face_swapping": "available",
    "model_management": "available",
    "user_management": "available"
  }
}
```

### Authentication

#### POST /api/v1/auth/register
Register a new user account.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe"
}
```

**Validation Rules:**
- Username: 3-20 characters, alphanumeric and underscore only
- Email: Valid email format
- Password: Minimum 8 characters, must contain uppercase, lowercase, and digit

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "user_id",
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

#### POST /api/v1/auth/login
Authenticate user and receive tokens.

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### GET /api/v1/auth/me
Get current user information (requires authentication).

**Response:**
```json
{
  "user": {
    "id": "user_id",
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00Z",
    "last_login": "2024-01-01T12:00:00Z"
  }
}
```

### Model Management

#### GET /api/v1/models
List available face swap models.

**Response:**
```json
[
  {
    "name": "Albica_Johns",
    "size_mb": 685.2,
    "quality": "high",
    "description": "Face swap model: Albica_Johns",
    "is_available": true
  }
]
```

#### GET /api/v1/models/{model_name}
Get specific model information.

**Parameters:**
- `model_name` (path): Name of the model

**Response:**
```json
{
  "name": "Albica_Johns",
  "size_mb": 685.2,
  "quality": "high",
  "description": "Face swap model: Albica_Johns",
  "is_available": true
}
```

### Face Swapping

#### POST /api/v1/faceswap
Perform face swap operation (requires authentication).

**Request:**
- `source_image` (file): Source face image
- `target_image` (file): Target image to swap face into
- `model_name` (form, optional): Specific model to use
- `quality` (form, optional): Quality level (low/medium/high, default: high)
- `preserve_expression` (form, optional): Preserve facial expression (default: true)

**Supported Image Formats:**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)

**Response:**
```json
{
  "result_image": "base64_encoded_result_image",
  "processing_time": 2.5,
  "model_used": "Albica_Johns",
  "confidence_score": 0.95
}
```

### File Upload

#### POST /api/v1/upload
Upload a file for processing (requires authentication).

**Request:**
- `file` (file): File to upload

**Supported File Types:**
- Images: .jpg, .jpeg, .png, .gif, .webp
- Videos: .mp4, .avi, .mov

**Response:**
```json
{
  "message": "File uploaded successfully",
  "filename": "image.jpg",
  "file_path": "uploads/user_id_image.jpg",
  "file_size": 1024000
}
```

## Error Handling

The API uses standard HTTP status codes and returns consistent error responses.

### Error Response Format

```json
{
  "error": "Error Type",
  "detail": "Detailed error message",
  "timestamp": "2024-01-01 12:00:00"
}
```

### Common Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `413 Request Entity Too Large`: File too large
- `415 Unsupported Media Type`: Unsupported file type
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Limit**: 100 requests per minute per IP address
- **Headers**: Rate limit information is included in response headers
  - `X-RateLimit-Limit`: Maximum requests per window
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Time when the rate limit resets

## Security Features

### Input Validation
- All user inputs are validated and sanitized
- File type validation for uploads
- File size limits enforced
- XSS prevention through input sanitization

### Authentication & Authorization
- JWT-based authentication
- Password hashing with bcrypt
- Token expiration and refresh mechanism
- User session management

### Security Headers
- Content Security Policy (CSP)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin

### CORS Configuration
- Configurable allowed origins
- Secure cross-origin requests
- Preflight request handling

## Configuration

The API can be configured through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `API_HOST` | Server host | 0.0.0.0 |
| `API_PORT` | Server port | 8000 |
| `API_DEBUG` | Debug mode | false |
| `API_SECRET_KEY` | JWT secret key | auto-generated |
| `API_ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | 30 |
| `API_RATE_LIMIT_REQUESTS` | Rate limit requests | 100 |
| `API_RATE_LIMIT_WINDOW` | Rate limit window (seconds) | 60 |
| `API_MAX_FILE_SIZE` | Max file size (bytes) | 52428800 |
| `API_UPLOAD_DIRECTORY` | Upload directory | uploads |

## Examples

### Python Client Example

```python
import requests
import json

# Base URL
base_url = "http://localhost:8000"

# Register user
register_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123",
    "full_name": "Test User"
}

response = requests.post(f"{base_url}/api/v1/auth/register", json=register_data)
print("Registration:", response.json())

# Login
login_data = {
    "username": "testuser",
    "password": "SecurePass123"
}

response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data)
tokens = response.json()
access_token = tokens["access_token"]

# Set authorization header
headers = {"Authorization": f"Bearer {access_token}"}

# List models
response = requests.get(f"{base_url}/api/v1/models", headers=headers)
models = response.json()
print("Available models:", models)

# Face swap
with open("source.jpg", "rb") as source, open("target.jpg", "rb") as target:
    files = {
        "source_image": source,
        "target_image": target
    }
    data = {
        "model_name": "Albica_Johns",
        "quality": "high",
        "preserve_expression": True
    }
    
    response = requests.post(
        f"{base_url}/api/v1/faceswap",
        files=files,
        data=data,
        headers=headers
    )
    
    result = response.json()
    print("Face swap result:", result)
```

### cURL Examples

#### Register User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123",
    "full_name": "Test User"
  }'
```

#### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123"
  }'
```

#### Face Swap (with token)
```bash
curl -X POST "http://localhost:8000/api/v1/faceswap" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "source_image=@source.jpg" \
  -F "target_image=@target.jpg" \
  -F "model_name=Albica_Johns" \
  -F "quality=high"
```

## Testing

### Running the API

1. Install dependencies:
```bash
pip install fastapi uvicorn python-multipart pyjwt bcrypt
```

2. Start the server:
```bash
python -m api.main
```

3. Access documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Testing Endpoints

Use the interactive documentation at `/docs` to test endpoints directly in the browser, or use tools like Postman, cURL, or the Python examples above.

## Support

For API support and questions:
- Check the interactive documentation at `/docs`
- Review the error responses for troubleshooting
- Ensure all required dependencies are installed
- Verify configuration settings 