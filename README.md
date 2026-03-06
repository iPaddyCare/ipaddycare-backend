# iPaddyCare - AI Powered Paddy Field Monitoring System

A FastAPI-based backend application for monitoring and analyzing paddy fields using AI and machine learning.

## 📋 Prerequisites

- **Python 3.10**
- **pip** (Python package installer)
- **Git** (optional, for cloning the repository)

## 🚀 Getting Started

### Step 1: Clone the Repository (if applicable)

If you have the project in a Git repository, clone it:

```bash
git clone <repository-url>
cd backend
```

### Step 2: Create a Virtual Environment

Create a virtual environment to isolate project dependencies:

**On Windows (PowerShell):**
```powershell
python -m venv venv
```

**On Windows (Command Prompt):**
```cmd
python -m venv venv
```

**On Linux/Mac:**
```bash
python3 -m venv venv
```

**Note:** If you have multiple Python versions installed, make sure to use Python 3.10:
- Windows: `py -3.10 -m venv venv`
- Linux/Mac: `python3.10 -m venv venv`

### Step 3: Activate the Virtual Environment

**On Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

If you encounter an execution policy error in PowerShell, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**On Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**On Linux/Mac:**
```bash
source venv/bin/activate
```

After activation, you should see `(venv)` at the beginning of your command prompt.

### Step 4: Install Dependencies

Install all required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Pydantic (data validation)
- Python-dotenv (environment variables)
- And other dependencies

### Step 5: Run the Application

Start the development server using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The `--reload` flag enables auto-reload on code changes (useful for development).

The application will start on `http://localhost:8000` by default.

### Step 6: Access the Application

Once the server is running, you can access:

- **API Root**: http://localhost:8000/
- **Interactive API Documentation (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Documentation (ReDoc)**: http://localhost:8000/redoc
- **Health Check Endpoint**: http://localhost:8000/api/v1/health
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── router.py          # Main API router
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── health.py      # Health check endpoint
│   ├── core/
│   │   ├── config.py          # Configuration settings
│   │   ├── dependencies.py    # Dependency injection
│   │   └── logging.py         # Logging configuration
│   ├── ml/
│   │   ├── base.py            # Base ML classes
│   │   ├── loaders.py         # Model loaders
│   │   ├── registry.py        # Model registry
│   │   └── models/            # ML models directory
│   ├── schemas/
│   │   ├── request.py         # Request schemas
│   │   └── response.py        # Response schemas
│   ├── services/              # Business logic services
│   ├── utils/
│   │   └── exceptions.py      # Custom exceptions
│   └── main.py               # FastAPI application entry point
├── venv/                     # Virtual environment (not in git)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🔌 API Endpoints

### Root Endpoint
- **GET** `/` - Welcome message

### Health Check
- **GET** `/api/v1/health` - Returns `{"status": "ok"}`

## 🛠️ Development

### Running in Production Mode

For production, run without the `--reload` flag:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Custom Port

To run on a different port:

```bash
uvicorn app.main:app --reload --port 8080
```

### Environment Variables

If you need to configure environment variables, create a `.env` file in the root directory:

```env
# Example .env file
# Add your environment variables here
```

The application uses `python-dotenv` to load environment variables from a `.env` file.

## 🧪 Testing the API

You can test the API endpoints using:

1. **Swagger UI**: Visit http://localhost:8000/docs for an interactive API explorer
2. **curl**:
   ```bash
   curl http://localhost:8000/
   curl http://localhost:8000/api/v1/health
   ```
3. **Python requests**:
   ```python
   import requests
   response = requests.get("http://localhost:8000/api/v1/health")
   print(response.json())
   ```

## 🚪 Deactivating the Virtual Environment

When you're done working on the project, deactivate the virtual environment:

```bash
deactivate
```

## 📝 Notes

- The virtual environment (`venv/`) should not be committed to version control
- Make sure to activate the virtual environment before running the application
- The application uses FastAPI's automatic API documentation feature
- All API routes are prefixed with `/api/v1`

## 🐛 Troubleshooting

### PowerShell Execution Policy Error

If you get an execution policy error when activating the virtual environment in PowerShell:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port Already in Use

If port 8000 is already in use, specify a different port:

```bash
uvicorn app.main:app --reload --port 8001
```

### Module Not Found Errors

Make sure you've:
1. Activated the virtual environment
2. Installed all dependencies: `pip install -r requirements.txt`
3. Are running commands from the project root directory

### Python Version Issues

To verify your Python version:
```bash
python --version
```

Make sure you're using Python 3.10. If you need to install Python 3.10 or switch versions:
- **Windows**: Use `py -3.10` to specify Python 3.10
- **Linux/Mac**: Use `python3.10` or install Python 3.10 via your package manager

## 📧 Contact

- **Name**: iPaddyCare
- **Website**: https://ipaddycare.com
- **Email**: contact@ipaddycare.com

## 📄 License

[Add your license information here]

