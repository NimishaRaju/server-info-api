# FastAPI Server Info API

A lightweight, high-performance REST API built with **FastAPI** to manage server configurations. This project leverages **Pydantic** for data validation, FastAPI's **Dependency Injection** system, and stores data locally in a JSON file.

---

## 📂 Project Structure

```text
├── app/    
│   ├── main.py            # Application entry point and API routes
│   ├── dependencies.py    # Reusable route dependencies (Auth, DB etc.)
│   ├── schemas.py         # Pydantic models for data validation/serialization
│   ├── services.py        # Core business logic and file I/O operations
│   ├── servers.json       # Local data store
│   └── test_main.py       # pytests
├── venv/                  # Virtual environment (ignored by git)
└── README.md              # Project documentation
```

---

## 🛠️ Architecture & Data Flow

The application follows a clean separation of concerns:
1. **`app/main.py`** receives the HTTP request and handles routing.
2. **`app/dependencies.py`** intercepts requests for pre-requisites (e.g., validating API keys).
3. **`app/services.py`** processes business logic and interacts with `servers.json`.
4. **`app/schemas.py`** ensures incoming and outgoing data strictly match expected structures.

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have **Python 3.10+** installed.

### 2. Installation & Setup
Run these commands from the root directory (outside the `app/` folder):

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Install required dependencies
pip install fastapi uvicorn pydantic pytest httpx
```

### 3. Running the Application
Start the local development server using Uvicorn. Using the command fastapi run main.py


The API will be available at **`http://127.0.0.1:8000`**.

---

## 🧪 Running Tests

The test suite uses `pytest` and FastAPI's `TestClient` to run integration tests against your endpoints. Run this from the root directory:

```bash
pytest test_main.py
```
