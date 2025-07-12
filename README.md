# Tech Challenge 02

This repository contains a FastAPI-based REST API with Swagger documentation.

## Prerequisites

- Python 3.9 or higher
- Poetry (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ML-Group-37/tech_challenge_02.git
cd tech_challenge_02
```

2. Install dependencies using Poetry:
```bash
poetry install
```

## Running the Application

1. Start the FastAPI server:
```bash
poetry run python -m tech_challenge_02.main
```

2. The API will be available at:
   - Main API: http://localhost:8000
   - Swagger UI (interactive API documentation): http://localhost:8000/docs
   - ReDoc (alternative API documentation): http://localhost:8000/redoc

## Available Endpoints

- `GET /api/test`: Test endpoint that returns a success message
  - Try it out in Swagger UI: http://localhost:8000/docs#/Main/test_endpoint_api_test_get

## Running Tests

Run the test suite using pytest:
```bash
poetry run pytest
```

For verbose test output:
```bash
poetry run pytest -v
```

## Development

The project uses Poetry for dependency management. Here are some common commands:

1. Add a new dependency:
```bash
poetry add <package-name>
```

2. Add a development dependency:
```bash
poetry add --group dev <package-name>
```

3. Update dependencies:
```bash
poetry update
```

4. Activate the virtual environment:
```bash
poetry shell
```

The server runs in development mode with hot reload enabled, so any changes you make to the code will automatically restart the server.

## Project Structure

```
tech_challenge_02/
├── src/
│   └── tech_challenge_02/    # Main package
│       ├── __init__.py       # Package initialization
│       ├── main.py           # FastAPI application
│       └── controllers/      # API endpoints
│           ├── __init__.py
│           └── main_controller.py
├── tests/                    # Test directory
│   └── test_main.py         # Tests for endpoints
├── pyproject.toml           # Poetry configuration
└── README.md                # This file
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 