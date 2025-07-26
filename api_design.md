# Circuit Recognition API Architecture Design

## 1. Overview

This document outlines the design of a unified API that exposes both ASC to JSON parsing functionality and circuit recognition/detection functionality with API key authentication. The API will be built using FastAPI for its performance, automatic documentation generation, and type validation capabilities.

## 2. API Architecture

### 2.1 Technology Stack
- **Framework**: FastAPI (Python)
- **Authentication**: API Key-based authentication
- **Serialization**: Pydantic models for request/response validation
- **File Handling**: Python standard libraries with temporary file storage
- **Deployment**: Docker containerization with Gunicorn/uvicorn

### 2.2 Core Components
1. **Authentication Layer**: API key validation middleware
2. **ASC Parsing Service**: Wrapper around existing ASCParser functionality
3. **Circuit Recognition Service**: Wrapper around YOLOv5-based circuit recognition
4. **File Management**: Temporary file handling for uploaded images
5. **Error Handling**: Comprehensive error responses and logging

## 3. API Endpoints

### 3.1 Authentication
All endpoints require a valid API key in the `X-API-Key` header.

### 3.2 ASC Parsing Endpoints

#### Convert ASC to JSON
- **Endpoint**: `POST /api/v1/asc-to-json`
- **Description**: Convert an LTspice ASC file to JSON format
- **Request**:
  - Form data with file upload
  - `file`: ASC file to convert
- **Response**:
  - `200 OK`: JSON representation of the circuit
  - `400 Bad Request`: Invalid file format
  - `401 Unauthorized`: Invalid API key
  - `500 Internal Server Error`: Processing error

#### Parse ASC File
- **Endpoint**: `POST /api/v1/parse-asc`
- **Description**: Parse an ASC file and return structured data
- **Request**:
  - Form data with file upload
  - `file`: ASC file to parse
- **Response**:
  - `200 OK`: Structured circuit data
  - `400 Bad Request`: Invalid file format
  - `401 Unauthorized`: Invalid API key
  - `500 Internal Server Error`: Processing error

### 3.3 Circuit Recognition Endpoints

#### Recognize Circuit from Image
- **Endpoint**: `POST /api/v1/recognize-circuit`
- **Description**: Process an image of a hand-drawn circuit and generate an ASC file
- **Request**:
  - Form data with file upload
  - `file`: Image file of the circuit (JPG, PNG)
  - `output_format`: Optional, "asc" or "json" (default: "asc")
- **Response**:
  - `200 OK`: Generated circuit file (ASC or JSON)
  - `400 Bad Request`: Invalid file format
  - `401 Unauthorized`: Invalid API key
  - `500 Internal Server Error`: Processing error

#### Recognize and Parse Circuit
- **Endpoint**: `POST /api/v1/recognize-and-parse`
- **Description**: Process an image and return structured circuit data
- **Request**:
  - Form data with file upload
  - `file`: Image file of the circuit (JPG, PNG)
- **Response**:
  - `200 OK`: Structured circuit data
  - `400 Bad Request`: Invalid file format
  - `401 Unauthorized`: Invalid API key
  - `500 Internal Server Error`: Processing error

### 3.4 Health Check Endpoint

#### API Health Check
- **Endpoint**: `GET /api/v1/health`
- **Description**: Check if the API is running
- **Request**: None
- **Response**:
  - `200 OK`: {"status": "healthy"}

## 4. Data Models

### 4.1 Circuit Data Model
```json
{
  "version": "4",
  "sheet": {
    "number": 1,
    "width": 880,
    "height": 680
  },
  "components": [
    {
      "id": "comp_1",
      "type": "res",
      "x": 128,
      "y": 96,
      "rotation": "R90",
      "attributes": {
        "name": "R1"
      }
    }
  ],
  "wires": [
    {
      "x1": 48,
      "y1": 256,
      "x2": 320,
      "y2": 256
    }
  ],
  "flags": []
}
```

### 4.2 Component Model
- `id`: Unique identifier for the component
- `type`: Component type (res, voltage, cap, etc.)
- `x`: X coordinate
- `y`: Y coordinate
- `rotation`: Rotation value (R0, R90, R180, R270)
- `attributes`: Dictionary of component attributes

### 4.3 Wire Model
- `x1`: Starting X coordinate
- `y1`: Starting Y coordinate
- `x2`: Ending X coordinate
- `y2`: Ending Y coordinate

## 5. Authentication System

### 5.1 API Key Management
- API keys will be stored in a secure database or environment variables
- Keys will have associated metadata (user, permissions, creation date)
- Keys can be revoked or disabled

### 5.2 Authentication Flow
1. Client includes `X-API-Key` header in all requests
2. Middleware validates the API key against the key store
3. If valid, request proceeds to the endpoint handler
4. If invalid, returns `401 Unauthorized`

### 5.3 Key Generation
- Keys will be generated using a cryptographically secure random generator
- Keys will be stored hashed in the database
- Admin endpoints will be provided for key management (internal use only)

## 6. Project Structure

```
circuit_api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── asc_parsing.py
│   │   │   │   ├── circuit_recognition.py
│   │   │   │   └── health.py
│   │   │   ├── schemas/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── circuit.py
│   │   │   │   └── auth.py
│   │   │   └── dependencies.py  # Authentication dependency
│   │   └── deps.py             # Global dependencies
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration settings
│   │   ├── security.py         # Authentication and security
│   │   └── logging.py          # Logging configuration
│   ├── services/
│   │   ├── __init__.py
│   │   ├── asc_parser.py       # ASC parsing service
│   │   └── circuit_recognizer.py # Circuit recognition service
│   ├── models/
│   │   ├── __init__.py
│   │   └── api_key.py          # API key model
│   └── utils/
│       ├── __init__.py
│       └── file_handler.py     # File handling utilities
├── tests/
│   ├── __init__.py
│   ├── test_asc_parsing.py
│   ├── test_circuit_recognition.py
│   └── test_auth.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
└── .env.example
```

## 7. Dependencies

### 7.1 Core Dependencies
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `python-multipart`: File upload handling
- `pydantic`: Data validation
- `torch`: PyTorch for YOLOv5
- `opencv-python`: Image processing
- `pandas`: Data processing
- `numpy`: Numerical computing
- `Pillow`: Image handling

### 7.2 Development Dependencies
- `pytest`: Testing framework
- `httpx`: HTTP client for testing
- `black`: Code formatting
- `flake8`: Code linting

## 8. Error Handling

### 8.1 Error Response Format
```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2023-01-01T00:00:00Z"
}
```

### 8.2 Common Error Codes
- `INVALID_API_KEY`: API key is missing or invalid
- `INVALID_FILE_FORMAT`: Uploaded file format is not supported
- `FILE_TOO_LARGE`: Uploaded file exceeds size limit
- `PROCESSING_ERROR`: Error occurred during file processing
- `INTERNAL_ERROR`: Unexpected server error

### 8.3 Validation
- File type validation for uploads
- File size limits
- Request parameter validation
- API key validation

## 9. Security Considerations

### 9.1 API Key Security
- Keys stored hashed in database
- Keys transmitted only over HTTPS
- Key rotation policy
- Rate limiting per API key

### 9.2 File Upload Security
- File type validation
- File size limits
- Sanitization of filenames
- Temporary file cleanup
- Virus scanning (optional)

### 9.3 Rate Limiting
- Per-API key rate limiting
- Global rate limiting
- Burst rate limiting

### 9.4 Input Validation
- Strict validation of all inputs
- Sanitization of file contents
- Protection against injection attacks

## 10. Deployment Considerations

### 10.1 Containerization
- Docker image with all dependencies
- Multi-stage build for smaller image size
- Environment-based configuration

### 10.2 Scaling
- Horizontal scaling with load balancer
- Asynchronous processing for heavy tasks
- Caching of frequently accessed data

### 10.3 Monitoring
- Health check endpoints
- Logging to centralized system
- Performance metrics collection
- Error tracking integration

### 10.4 Environment Configuration
- Environment variables for configuration
- Different settings for development/production
- Secure storage of secrets

### 10.5 Backup and Recovery
- Regular backups of API key database
- Recovery procedures for failed deployments
- Rollback capabilities

## 11. Performance Optimization

### 11.1 Model Loading
- Pre-load YOLOv5 model at startup
- Model caching for multiple requests
- GPU acceleration when available

### 11.2 File Handling
- Temporary file cleanup
- Efficient image processing
- Streaming for large file uploads

### 11.3 Caching
- Cache frequently requested data
- Cache parsed ASC files
- Cache recognition results for identical images

## 12. Testing Strategy

### 12.1 Unit Tests
- Test individual components
- Mock external dependencies
- Test error conditions

### 12.2 Integration Tests
- Test API endpoints
- Test file upload and processing
- Test authentication flow

### 12.3 Performance Tests
- Load testing with multiple concurrent users
- Stress testing with large files
- Response time monitoring

## 13. API Documentation

### 13.1 Automatic Documentation
- Swagger UI at `/docs`
- ReDoc at `/redoc`
- OpenAPI schema at `/openapi.json`

### 13.2 Examples
- Example requests for each endpoint
- Example responses for success and error cases
- Code samples in multiple languages

## 14. Future Enhancements

### 14.1 Additional Endpoints
- Batch processing of multiple files
- Circuit simulation integration
- Circuit visualization endpoint

### 14.2 Advanced Features
- Async processing for long-running tasks
- Webhook notifications for completed tasks
- User account management