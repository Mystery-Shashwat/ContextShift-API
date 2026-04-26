# ContextShift API

ContextShift is a FastAPI backend service designed to save unstructured work context, process it through an LLM (Groq) to generate structured summaries, and allow users to resume their work efficiently.

## Prerequisites

- Python 3.11+
- Groq API Key

## Setup

1. **Clone the repository** (if applicable) and navigate to the project directory:
   ```bash
   cd contextshift
   ```

2. **Create a virtual environment and install dependencies**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables**:
   Copy `.env.example` to `.env` and configure your Groq API key:
   ```bash
   cp .env.example .env
   ```
   Add your API key inside `.env`.

## Running the Server

Start the FastAPI application using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The server will be available at `http://127.0.0.1:8000`.

## Running Tests

Run the test suite using pytest:

```bash
pytest tests/
```

The tests use a mock LLM service, so the Groq API will not be called during testing.

## API Endpoints

### 1. Save Context
- **Endpoint**: `POST /save`
- **Body**:
  ```json
  {
    "user_id": "user123",
    "raw_context": "I was working on the login page but it is throwing a 500 error when I submit the form."
  }
  ```
- **Response**:
  ```json
  {
    "id": "context_id",
    "problem": "...",
    "current_progress": "...",
    "next_step": "...",
    "open_questions": ["..."],
    "notes": "..."
  }
  ```

### 2. Resume Context
- **Endpoint**: `GET /resume/{context_id}`
- **Response**: Returns the structured context for the given context ID.

### 3. Get User Contexts
- **Endpoint**: `GET /contexts/{user_id}`
- **Response**: Returns a list of contexts associated with the given user ID.

## Docker Deployment

Build and run the Docker container:

```bash
docker build -t contextshift .
docker run -p 8000:8000 --env-file .env contextshift
```
