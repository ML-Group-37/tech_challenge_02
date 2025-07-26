# Tech Challenge 02

This repository contains a FastAPI-based REST API with Swagger documentation.

## Prerequisites

- Python 3.9 or higher
- Poetry (Python package manager)

## AWS Credentials & S3 Configuration

To enable Parquet uploads to S3, set the following environment variables before running the application:

```
# Required for S3 upload:
export AWS_ACCESS_KEY_ID=your-access-key-id
export AWS_SECRET_ACCESS_KEY=your-secret-access-key
# (Optional, for temporary credentials)
export AWS_SESSION_TOKEN=your-session-token

# S3 bucket and prefix:
export S3_BUCKET=your-bucket-name
export S3_PREFIX=parquet_data  # (optional, defaults to 'parquet_data')
```

- You can also configure AWS credentials using the AWS CLI (`aws configure`) or IAM roles if running on AWS infrastructure.
- The application will use these credentials to upload Parquet files to S3 with daily partitioning.

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
poetry run python src/tech_challenge_02/main.py
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