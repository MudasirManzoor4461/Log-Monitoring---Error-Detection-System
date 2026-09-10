# 🔍 Log Monitoring & Error Detection System

A professional log monitoring and error detection system built with **Python and FastAPI**. The system parses application logs, detects and classifies errors, stores logs in SQLite, generates alerts, and provides analytics through REST APIs.

The project also includes a modern web dashboard and Docker support for containerized deployment.

![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)
![Docker](https://img.shields.io/badge/docker-ready-blue?logo=docker)
![Tests](https://img.shields.io/badge/tests-147%20passed-brightgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## 📸 Project Screenshots

### 🖥️ Dashboard
<img width="579" height="450" alt="Dashboard" src="https://github.com/user-attachments/assets/8c9b9416-87c4-4b07-b9a9-ddcd75120d61" />

The web dashboard provides an overview of uploaded logs, errors, warnings, critical errors, error rate, and error categories.

### 📚 FastAPI Documentation
<img width="758" height="450" alt="api-docs" src="https://github.com/user-attachments/assets/081cd27a-91c0-4dd2-9ca6-ef1ed0d51a89" />

Interactive REST API documentation powered by FastAPI and Swagger UI.

### 🐳 Docker Deployment
<img width="942" height="360" alt="docker" src="https://github.com/user-attachments/assets/2f650474-edb9-44bd-99a0-dee095eb756e" />

The application running inside a Docker container.

---

## 🚀 Features

- Log file parsing
- Valid and invalid log line handling
- Error detection, classification, and grouping
- SQLite database storage with duplicate log protection
- Alert generation, persistence, and acknowledgement
- Log search, pagination, and time-range filtering
- Error trends and analytics
- Log upload API
- Web-based dashboard
- Docker and Docker Compose support
- Automated testing
- Input validation and safe file-path validation
- Database constraints and persistent storage

> **Note:** Live file monitoring is under development and not yet a production-complete feature.

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | FastAPI, Pydantic |
| Database | SQLite |
| Testing | Pytest, HTTPX |
| Deployment | Docker, Docker Compose |
| Frontend | HTML, CSS, JavaScript |

---

## 📁 Project Structure

```text
log-monitoring-system/
│
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── repositories.py
│   │   └── schema.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── log_schema.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analytics.py
│   │   ├── alert_service.py
│   │   ├── error_detector.py
│   │   ├── error_grouper.py
│   │   ├── live_monitor.py
│   │   ├── log_monitor.py
│   │   └── log_parser.py
│   │
│   ├── __init__.py
│   └── main.py
│
├── frontend/
│   └── index.html
│
├── sample_logs/
│   ├── app.log
│   └── test_invalid.log
│
├── screenshots/
│   ├── dashboard.png
│   ├── api-docs.png
│   └── docker.png
│
├── tests/
│   ├── conftest.py
│   ├── test_alert_service.py
│   ├── test_analytics.py
│   ├── test_error_detector.py
│   ├── test_error_grouper.py
│   ├── test_live_monitor.py
│   ├── test_log_monitor.py
│   ├── test_log_parser.py
│   ├── test_repositories.py
│   └── test_routes.py
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/mudasirmanzoor/log-monitoring-system.git
cd log-monitoring-system
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows (PowerShell):**
```powershell
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

| Resource | URL |
|---|---|
| API | http://127.0.0.1:8000 |
| Interactive Docs (Swagger) | http://127.0.0.1:8000/docs |
| OpenAPI Spec | http://127.0.0.1:8000/openapi.json |

---

## 📊 Web Dashboard

The project includes a web-based dashboard at `frontend/index.html`.

It allows users to upload log files and view:

- Total logs, errors, warnings, and critical errors
- Error rate and error categories
- Log details and analytics results

---

## 🔌 API Capabilities

### Logs
- Upload, retrieve, search, and delete logs
- Pagination
- Filter logs by time range

### Errors
- Detect, classify, and group errors
- Retrieve detected errors
- View top error categories and error trends

### Analytics
- Total logs / errors
- Warning and critical counts
- Logs by level, errors by category
- Most common error, overall error rate

### Alerts
- Generate, store, and retrieve alerts
- Acknowledge alerts

### Live Monitoring
Included in the codebase but still under development — not yet production-ready.

---

## 🗄️ Database

The application uses **SQLite** for persistent data storage.

**`logs` table** — timestamp, log level, message, error category

**`alerts` table** — log ID, alert level, error category, message, creation time, acknowledgement status

Database files are excluded from Git via `.gitignore`.

---

## 🧪 Testing

Run the full test suite with Pytest:

```bash
pytest
```

```text
147 passed
```

Coverage includes log parsing, error detection/classification/grouping, analytics, log monitoring, alert generation, database repositories, and API routes.

---

## 🐳 Docker

Build and run the application in a container:

```bash
# Build the image
docker compose build

# Start the container
docker compose up

# Stop the container
docker compose down
```

Once running, the API is available at `http://127.0.0.1:8000` (Swagger docs at `/docs`).

A Docker volume is used for persistent database storage.

---

## 🔐 Security & Reliability

- Input validation and safe file-path validation
- Directory traversal protection
- Database and foreign-key constraints
- Duplicate log protection
- Graceful error handling
- UTF-8 file handling
- Non-root Docker container
- Environment-based database configuration
- Sensitive environment files excluded from Git
- Persistent database volume

---

## 📌 Future Improvements

- Production-grade live log monitoring
- PostgreSQL support
- Background task processing
- Real-time WebSocket dashboard
- Email and Slack notifications
- Authentication and authorization
- Advanced log filtering
- Support for monitoring multiple log files
- Containerized frontend
- CI/CD pipeline
- Cloud deployment
- Advanced observability and metrics

---

## 👨‍💻 Author

**Mudasir Manzoor**
BS Computer Science Student

- GitHub: [github.com/mudasirmanzoor](https://github.com/MudasirManzoor4461)
- LinkedIn: [linkedin.com/in/mudasirmanzoor](https://linkedin.com/in/mudasirmanzoor/)

---

## 📄 License

This project is intended for educational, portfolio, and demonstration purposes. Feel free to use, modify, and learn from it.
