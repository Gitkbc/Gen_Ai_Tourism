# Travel AI Backend 🧠

The core orchestration engine for the Travel AI system. This FastAPI service manages the multi-agent workflow, LLM interactions, and response caching.

## 🛠️ Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)
- An API Key for **OpenRouter** (or OpenAI if configured)

## 🚀 Installation & Setup

1. **Navigate to the backend directory:**
   ```bash
   cd travel_ai
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

Create a `.env` file in the `travel_ai` directory:

```bash
touch .env
```

Add the following variables:

```env
# Required for LLM generation
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here

# Optional: Debug mode
DEBUG=true
```

## 🏃‍♂️ Running the Server

Start the FastAPI development server:

```bash
uvicorn travel_ai.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at: `http://127.0.0.1:8000`
API Documentation (Swagger): `http://127.0.0.1:8000/docs`