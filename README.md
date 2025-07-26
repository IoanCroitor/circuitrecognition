# Circuit Recognition API

This API provides endpoints for converting LTspice ASC files to JSON format and processing images of hand-drawn circuits.

## Features

- Convert LTspice ASC files to JSON format
- Parse ASC files to structured data
- API key authentication for all endpoints
- Docker support for easy deployment

## Prerequisites

- Python 3.9+
- Required Python packages (see pyproject.toml)

## Installation

1. Clone the repository
2. Install the required packages:
   ```bash
   pip install -e .
   ```

## Usage

### Running the API locally

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Running with Docker

```bash
docker-compose up --build
```

## API Endpoints

### Authentication

All endpoints require an API key in the `X-API-Key` header.

Test API keys:
- `test-key-123` - Basic user access
- `admin-key-456` - Admin access

### ASC Parsing

#### Convert ASC to JSON

- **Endpoint**: `POST /api/v1/asc-to-json/convert`
- **Description**: Convert an LTspice ASC file to JSON format
- **Request**: Form data with file upload (`file`: ASC file to convert)
- **Response**: JSON representation of the circuit

#### Parse ASC File

- **Endpoint**: `POST /api/v1/asc-to-json/parse`
- **Description**: Parse an ASC file and return structured data
- **Request**: Form data with file upload (`file`: ASC file to parse)
- **Response**: Structured circuit data

### Health Check

#### API Health Check

- **Endpoint**: `GET /api/v1/health`
- **Description**: Check if the API is running
- **Response**: `{"status": "healthy"}`

## Project Structure

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
│   │   │   │   └── health.py
│   │   │   ├── schemas/
│   │   │   │   ├── __init__.py
│   │   │   │   └── circuit.py
│   │   │   └── dependencies.py  # Authentication dependency
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration settings
│   │   └── logging.py          # Logging configuration
│   ├── services/
│   │   ├── __init__.py
│   │   └── asc_parser.py       # ASC parsing service
│   ├── models/
│   │   ├── __init__.py
│   │   └── api_key.py          # API key model
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Development

### Running Tests

```bash
pytest
```

### API Documentation

Once the API is running, you can access the automatic documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT
