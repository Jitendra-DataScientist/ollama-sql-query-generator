# SQL Generator API

A FastAPI-based service that generates SQL queries from natural language questions using the Ollama chat interface with the Gemma3 model.

## Features

- Convert natural language questions to SQL queries
- Uses Ollama's Gemma3 model for intelligent query generation
- Clean SQL output without code fences or extra formatting
- RESTful API with automatic documentation
- Input validation using Pydantic models

## Requirements

- Python 3.7+
- FastAPI
- Pydantic
- Ollama Python client
- Uvicorn (for development server)
- Ollama installed locally with Gemma3 model

## Installation

1. Install the required packages:
```bash
pip install fastapi pydantic ollama uvicorn
```

2. Make sure Ollama is installed and running on your system:
```bash
# Install Ollama (follow instructions at https://ollama.ai)
# Pull the Gemma3 model
ollama pull gemma3
```

## Usage

### Starting the Server

Run the application:
```bash
python app.py
```

The server will start on `http://localhost:8000` with auto-reload enabled for development.

### API Documentation

Once running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

### Making Requests

#### Endpoint: `POST /generate-sql`

**Request Body:**
```json
{
  "schema": "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100)); CREATE TABLE orders (id INT PRIMARY KEY, user_id INT, amount DECIMAL(10,2), created_at TIMESTAMP);",
  "question": "Find all users who have placed orders over $100"
}
```

**Response:**
```json
{
  "sql_query": "SELECT DISTINCT u.* FROM users u JOIN orders o ON u.id = o.user_id WHERE o.amount > 100"
}
```

### Example with cURL

```bash
curl -X POST "http://localhost:8000/generate-sql" \
  -H "Content-Type: application/json" \
  -d '{
    "schema": "CREATE TABLE products (id INT, name VARCHAR(100), price DECIMAL(10,2))",
    "question": "Get all products under $50"
  }'
```

## How It Works

1. **Input Processing**: The API accepts a database schema and a natural language question
2. **Prompt Generation**: Creates a structured prompt for the Gemma3 model
3. **AI Processing**: Uses Ollama to generate SQL based on the schema and question
4. **Output Cleaning**: Removes code fences and extra formatting from the generated SQL
5. **Response Formatting**: Returns clean, flattened SQL ready for execution

## Code Structure

- `QueryRequest`: Pydantic model for request validation
- `clean_sql()`: Removes markdown code fences from generated SQL
- `flatten_sql_safe()`: Converts multi-line SQL to single line format
- `/generate-sql`: Main endpoint that processes requests and returns SQL

## Error Handling

The API includes proper error handling:
- Returns HTTP 500 for Ollama communication errors
- Validates input using Pydantic models
- Provides detailed error messages

## Development

The application runs with auto-reload enabled by default, making it easy to develop and test changes.

## Notes

- Ensure Ollama is running before starting the API
- The Gemma3 model must be available in your Ollama installation
- Generated SQL should be validated before executing on production databases
- Consider adding authentication and rate limiting for production use