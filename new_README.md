# PrivacyGuard Dashboard

PrivacyGuard is a web-based dashboard for managing network privacy and routing. It provides an intuitive interface for controlling network interfaces, toggling privacy services (VPN, proxy, Tor), automating privacy-related tasks, and viewing analytics reports.

## Features

- Discover and manage network interfaces
- Set preferred network routes and view current routing status
- Enable or disable network interfaces on-the-fly
- Toggle privacy services: VPN, Proxy, Tor
- Schedule automated privacy checks and actions
- View recent logs and generate aggregated reports
- Simple, responsive frontend using static HTML and JavaScript

## Repository Structure

```
.
├── backend/                  Flask backend application and API routes
├── frontend/                 Static frontend files (HTML, JS)
├── CHANGELOG.md             Release notes and changelog
├── install_directions.md    Detailed installation and usage guide
├── setup.sh                 Convenience script for setup and launch
├── .gitignore
└── README.md                This file
```

## Prerequisites

- Python 3.8 or higher
- `pip` package manager
- (Optional) Virtual environment tool (`venv` or `virtualenv`)
- Root/Administrator privileges (required for network interface management)
- Modern web browser

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/privacyguard-dashboard.git
   cd privacyguard-dashboard
   ```
2. (Optional) Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install backend dependencies:
   ```bash
   cd backend
   pip install --upgrade pip
   pip install -r requirements.txt
   cd ..
   ```
4. (Optional) Review and adjust settings in `backend/config.json` as needed.

## Running the Backend

By default, the backend API server listens on port 8001.

```bash
cd backend
python3 app.py
```

Alternatively, you can use Flask's CLI:

```bash
FLASK_APP=app.py FLASK_ENV=development flask run --host=0.0.0.0 --port=8001
```

## Running the Frontend

Serve the static frontend files over HTTP to allow CORS requests to the backend API.

```bash
cd frontend
python3 -m http.server 8000
```

Then open your web browser and navigate to:

- Dashboard UI: http://localhost:8000
- Reports page: http://localhost:8000/reports.html

## API Endpoints

| Endpoint               | Method | Description                                |
| ---------------------- | ------ | ------------------------------------------ |
| `/api/interfaces`      | GET    | List available network interfaces          |
| `/api/routing`         | GET    | Get current routing and preferred interface |
| `/api/routing/preferred` | POST | Set preferred routing interface            |
| `/api/interface/<name>/status` | GET | Get status of a specific interface       |
| `/api/interface/<name>/toggle` | POST | Enable/disable a network interface       |
| `/api/config`          | GET    | Retrieve current configuration             |
| `/api/config`          | POST   | Update configuration and save to file      |
| `/api/automation/status` | GET  | Get current automation status              |
| `/api/logs`            | GET    | Fetch recent log entries                   |
| `/api/reports`         | GET    | Generate aggregated report data            |

## Logs and Reports

- Backend logs are stored in `backend/privacyguard.log`.
- Use the `/api/logs` and `/api/reports` endpoints to fetch recent logs and aggregated reports programmatically.

## Further Documentation

For detailed installation instructions, advanced configuration, and deployment options, see [install_directions.md](install_directions.md). For a full list of changes, see [CHANGELOG.md](CHANGELOG.md).

