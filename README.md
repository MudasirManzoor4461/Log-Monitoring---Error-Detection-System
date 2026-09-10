# 🔍 Log Monitoring & Error Detection System

A professional log monitoring and error detection system built with **Python and FastAPI**. The system parses application logs, detects and classifies errors, stores logs in SQLite, generates alerts, and provides analytics through REST APIs.

The project also includes a modern web dashboard and Docker support for containerized deployment.

---

## 📸 Project Screenshots
### 🖥️ Dashboard
![alt text](Dashboard.png)

The web dashboard provides an overview of uploaded logs, errors, warnings, critical errors, error rate, and error categories.

### 📚 FastAPI Documentation
![alt text](api-docs.png)

Interactive REST API documentation powered by FastAPI and Swagger UI.

### 🐳 Docker Deployment
![alt text](docker.png)
The application running inside a Docker container.

---

## 🚀 Features

* Log file parsing
* Valid and invalid log line handling
* Error detection
* Error classification
* Error grouping
* SQLite database storage
* Duplicate log protection
* Alert generation
* Alert persistence
* Alert acknowledgement
* Log search
* Pagination
* Time-range log filtering
* Error trends
* Error analytics
* Log upload API
* Web-based dashboard
* Docker support
* Docker Compose support
* Automated testing
* Input validation
* Error handling
* Safe file-path validation
* Database constraints
* Persistent database storage

> **Note:** Live file monitoring is currently under development and is not considered a completed production feature.

---

## 🛠️ Tech Stack

* **Python 3.12**
* **FastAPI**
* **Pydantic**
* **SQLite**
* **Pytest**
* **HTTPX**
* **Docker**
* **Docker Compose**
* **HTML**
* **CSS**
* **JavaScript**

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

**Windows PowerShell:**

```powershell
venv\Scripts\activate
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

The API will be available at:

```text
http://127.0.0.1:8000
```

### Interactive API Documentation

```text
http://127.0.0.1:8000/docs
```

### OpenAPI Specification

```text
http://127.0.0.1:8000/openapi.json
```

---

## 📊 Web Dashboard

The project includes a web-based dashboard located at:

```text
frontend/index.html
```

The dashboard allows users to upload log files and view important monitoring information, including:

* Total logs
* Total errors
* Warnings
* Critical errors
* Error rate
* Error categories
* Log information
* Analytics results

---

## 🔌 API Capabilities

### Logs

* Upload logs
* Retrieve logs
* Search logs
* Delete logs
* Pagination
* Filter logs by time range

### Errors

* Detect errors
* Classify errors
* Group errors
* Retrieve detected errors
* View top error categories
* View error trends

### Analytics

* Total logs
* Total errors
* Warning count
* Critical count
* Logs by level
* Errors by category
* Most common error
* Error rate

### Alerts

* Generate alerts
* Store alerts
* Retrieve alerts
* Acknowledge alerts

### Live Monitoring

Live monitoring components are included in the project but are currently under development and are not considered production-complete.

---

## 🗄️ Database

The application uses **SQLite** for persistent data storage.

### `logs`

Stores application log records including:

* Timestamp
* Log level
* Message
* Error category

### `alerts`

Stores generated alerts including:

* Log ID
* Alert level
* Error category
* Message
* Creation time
* Acknowledgement status

Database files are excluded from Git using `.gitignore`.

---

## 🧪 Testing

The project includes automated tests using **Pytest**.

Run the complete test suite:

```bash
pytest
```

### Test Result

```text
147 passed
```

The test suite covers major components including:

* Log parsing
* Error detection
* Error classification
* Error grouping
* Analytics
* Log monitoring
* Alert generation
* Database repositories
* API routes

---

## 🐳 Docker

The application supports containerized deployment using **Docker** and **Docker Compose**.

### Build the Docker Image

```bash
docker compose build
```

### Start the Container

```bash
docker compose up
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

### Stop the Container

```bash
docker compose down
```

The project uses a Docker volume for persistent database storage.

---

## 🔐 Security & Reliability

The project follows several production-minded practices:

* Input validation
* Safe file-path validation
* Directory traversal protection
* Database constraints
* Duplicate log protection
* Foreign-key constraints
* Graceful error handling
* UTF-8 file handling
* Non-root Docker container
* Environment-based database configuration
* Sensitive environment files excluded from Git
* Persistent database volume
* Validation of API inputs

---

## 📌 Future Improvements

Planned improvements include:

* Production-grade live log monitoring
* PostgreSQL support
* Background task processing
* Real-time WebSocket dashboard
* Email and Slack notifications
* Authentication and authorization
* Advanced log filtering
* Monitoring multiple log files
* Containerized frontend
* CI/CD pipeline
* Cloud deployment
* Advanced observability and metrics

---

## 👨‍💻 Author

### Mudasir Manzoor

**BS Computer Science Student**

**GitHub:** `github.com/mudasirmanzoor`

**LinkedIn:** `linkedin.com/in/mudasirmanzoor/`

---

## 📄 License

This project is intended for educational, portfolio, and demonstration purposes.
