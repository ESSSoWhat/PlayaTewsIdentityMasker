# PlayaTewsIdentityMasker API Documentation

## Overview

The PlayaTewsIdentityMasker API is a secure RESTful API that provides real-time face swapping and identity masking capabilities. Built with FastAPI, it follows RESTful principles and implements comprehensive security measures.

### Features

- 🔐 **Secure Authentication**: JWT-based authentication with bcrypt password hashing
- 🎭 **Face Swapping**: Real-time face swap operations using DFM models
- 📁 **File Management**: Secure file upload and validation
- 🚀 **High Performance**: Rate limiting, caching, and optimized processing
- 🛡️ **Security**: Input validation, XSS prevention, CSRF protection
- 📊 **Monitoring**: Comprehensive logging and request tracking
- 📚 **Documentation**: Auto-generated OpenAPI/Swagger documentation

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r api/requirements.txt

# Set environment variables (optional)
export API_SECRET_KEY="your-secure-secret-key"
export API_HOST="0.0.0.0"
export API_PORT="8000"

# Run the API
python -m api.main
```

### Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Authentication

### Registration

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
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

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

### Using Authentication

Include the access token in the Authorization header:

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## API Endpoints

### Health Check

#### GET /health
Basic health check endpoint.

```bash
curl -X GET "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-31T10:30:00.000Z",
  "version": "1.0.0",
  "uptime": 3600.5
}
```

#### GET /health/detailed
Detailed health check with component status.

```bash
curl -X GET "http://localhost:8000/health/detailed"
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-31T10:30:00.000Z",
  "version": "1.0.0",
  "components": {
    "api": "healthy",
    "security": "healthy",
    "file_system": "healthy",
    "dfm_models": "healthy (5 models)"
  }
}
```

### Authentication Endpoints

#### POST /api/v1/auth/register
Register a new user account.

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Validation Rules:**
- Username: 3-50 characters, alphanumeric and underscores only
- Email: Valid email format
- Password: Minimum 8 characters, must contain uppercase, lowercase, and number

#### POST /api/v1/auth/login
Authenticate user and receive access tokens.

**Request Body:**
```json
{
  "username": "testuser",
  "password": "SecurePass123!"
}
```

#### GET /api/v1/auth/me
Get current user information.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "created_at": "2025-01-31T10:00:00.000Z",
  "is_active": true
}
```

### Model Management

#### GET /api/v1/models
List all available DFM models.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "name": "Liu_Lice",
    "size": 718525559,
    "path": "dfm_models/Liu_Lice.dfm",
    "created_at": "2025-01-31T09:00:00.000Z",
    "is_valid": true
  },
  {
    "name": "Albica_Johns",
    "size": 718525559,
    "path": "dfm_models/Albica_Johns.dfm",
    "created_at": "2025-01-31T09:00:00.000Z",
    "is_valid": true
  }
]
```

#### GET /api/v1/models/{model_name}
Get information about a specific model.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "name": "Liu_Lice",
  "size": 718525559,
  "path": "dfm_models/Liu_Lice.dfm",
  "created_at": "2025-01-31T09:00:00.000Z",
  "is_valid": true
}
```

### Face Swap Operations

#### POST /api/v1/faceswap
Perform face swap operation.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "source_image": "/uploads/source_image.jpg",
  "target_image": "/uploads/target_image.jpg",
  "model_name": "Liu_Lice",
  "quality": "high",
  "preserve_expression": true
}
```

**Response:**
```json
{
  "result_image": "/uploads/faceswap_result_1706700000.jpg",
  "processing_time": 2.5,
  "model_used": "Liu_Lice",
  "quality": "high"
}
```

### File Upload

#### POST /api/v1/upload
Upload a file for processing.

**Headers:** `Authorization: Bearer <token>`

**Form Data:**
- `file`: File to upload (max 10MB)

**Supported File Types:**
- Images: `.jpg`, `.jpeg`, `.png`
- Videos: `.mp4`, `.avi`, `.mov`

**Response:**
```json
{
  "filename": "1706700000_image.jpg",
  "original_name": "image.jpg",
  "size": 1024000,
  "hash": "a1b2c3d4e5f6...",
  "url": "/uploads/1706700000_image.jpg",
  "uploaded_at": "2025-01-31T10:30:00.000Z"
}
```

### Utilities

#### GET /api/v1/utils/validate-file
Validate a filename for upload.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `filename`: Filename to validate

**Response:**
```json
{
  "filename": "image.jpg",
  "is_valid": true,
  "allowed_types": [".jpg", ".jpeg", ".png", ".mp4", ".avi", ".mov"],
  "max_size": 10485760
}
```

## Error Handling

The API uses standard HTTP status codes and returns consistent error responses:

### Error Response Format

```json
{
  "error": "Error Type",
  "detail": "Detailed error message",
  "timestamp": "2025-01-31T10:30:00.000Z"
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
- `415 Unsupported Media Type`: Invalid content type
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Limit**: 100 requests per minute per IP address
- **Headers**: 
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset time

## Security Features

### Input Validation
- All user inputs are sanitized to prevent XSS attacks
- File uploads are validated for type and size
- Request data is validated using Pydantic models

### Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Content-Security-Policy`: Restricts resource loading
- `Strict-Transport-Security`: Enforces HTTPS

### Authentication
- JWT tokens with configurable expiration
- bcrypt password hashing
- Secure token validation

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_HOST` | `0.0.0.0` | Server host |
| `API_PORT` | `8000` | Server port |
| `API_SECRET_KEY` | `your-secret-key-change-in-production` | JWT secret key |
| `API_DEBUG` | `false` | Debug mode |
| `API_RATE_LIMIT_REQUESTS` | `100` | Rate limit requests |
| `API_RATE_LIMIT_WINDOW` | `60` | Rate limit window (seconds) |
| `API_MAX_FILE_SIZE` | `10485760` | Max file size (10MB) |
| `API_CACHE_TTL` | `300` | Cache TTL (seconds) |

### Configuration File

Create a `.env` file for local development:

```env
API_SECRET_KEY=your-secure-secret-key-here
API_DEBUG=true
API_HOST=127.0.0.1
API_PORT=8000
```

## Testing

### Using curl

```bash
# Health check
curl -X GET "http://localhost:8000/health"

# Register user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "SecurePass123!"}'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "SecurePass123!"}'

# List models (with token)
curl -X GET "http://localhost:8000/api/v1/models" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Using Python requests

```python
import requests

# Base URL
base_url = "http://localhost:8000"

# Register
response = requests.post(f"{base_url}/api/v1/auth/register", json={
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!"
})
tokens = response.json()

# Use access token
headers = {"Authorization": f"Bearer {tokens['access_token']}"}

# List models
response = requests.get(f"{base_url}/api/v1/models", headers=headers)
models = response.json()
print(models)
```

## Monitoring and Logging

### Log Files
- **API Log**: `api.log` - All API requests and responses
- **Error Log**: Errors are logged with stack traces
- **Security Log**: Authentication and authorization events

### Log Format
```json
{
  "timestamp": "2025-01-31T10:30:00.000Z",
  "method": "POST",
  "url": "/api/v1/auth/login",
  "client_ip": "127.0.0.1",
  "user_agent": "curl/7.68.0",
  "content_length": 89
}
```

### Performance Headers
- `X-Processing-Time`: Request processing time in seconds
- `X-Cache`: Cache status (HIT/MISS)

## Development

### Project Structure
```
api/
├── __init__.py          # Package initialization
├── main.py             # FastAPI application
├── config.py           # Configuration management
├── security.py         # Authentication and security
├── middleware.py       # Custom middleware
└── requirements.txt    # Dependencies
```

### Adding New Endpoints

1. Define Pydantic models for request/response
2. Add endpoint function with proper decorators
3. Implement authentication if required
4. Add input validation and error handling
5. Update documentation

### Testing New Features

```bash
# Run with auto-reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
python -m pytest tests/

# Check API documentation
open http://localhost:8000/docs
```

## Production Deployment

### Security Checklist
- [ ] Change default secret key
- [ ] Enable HTTPS
- [ ] Configure proper CORS origins
- [ ] Set up database for user storage
- [ ] Configure logging and monitoring
- [ ] Set up rate limiting
- [ ] Enable security headers

### Performance Optimization
- [ ] Use production ASGI server (Gunicorn + Uvicorn)
- [ ] Configure caching (Redis)
- [ ] Set up load balancing
- [ ] Monitor performance metrics
- [ ] Optimize database queries

### Example Production Setup

```bash
# Install production dependencies
pip install gunicorn uvicorn[standard] redis

# Run with Gunicorn
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review error logs
3. Test with curl or Postman
4. Check configuration settings

## License

This API is part of the PlayaTewsIdentityMasker project and follows the same licensing terms. 