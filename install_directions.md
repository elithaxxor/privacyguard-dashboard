# PrivacyGuard Installation Guide

This guide provides detailed steps for installing and running PrivacyGuard, the network privacy dashboard.

## Prerequisites
- Python 3.8 or higher
- A modern web browser
- Root/Administrator privileges (required for network interface management)
- (Optional) Virtual environment tool (e.g., `venv` or `virtualenv`)

## Clone the Repository
```bash
git clone https://github.com/yourusername/privacyguard-dashboard.git
cd privacyguard-dashboard
```

## Backend Setup
1. Navigate to the backend folder:
   ```bash
   cd backend
   ```
2. (Optional) Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\\Scripts\\activate
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure `config.json` as needed (default settings are provided).

## Frontend Setup
1. Return to the project root if needed:
   ```bash
   cd ../frontend
   ```
2. Serve the static files using a simple HTTP server:
   ```bash
   python3 -m http.server 8000
   ```

## Running PrivacyGuard
1. In one terminal, start the backend server:
   ```bash
   cd backend
   python3 app.py
   ```
2. In another terminal, start the frontend server (if not already running):
   ```bash
   cd frontend
   python3 -m http.server 8000
   ```
3. Open your browser and navigate to:
   - Dashboard: http://localhost:8000
   - Reports:   http://localhost:8000/reports.html

## Docker (Optional)
You can also containerize the application using Docker:
```bash
# Build images
docker build -t privacyguard-backend backend
# Run backend
docker run -d --name pg-backend -p 8001:8001 privacyguard-backend
# Serve frontend via nginx or any static server on port 8000
```

## Post-Installation
- Use the Settings modal in the UI to adjust automation, VPN, proxy, and Tor settings.
- Drag-and-drop dashboard sections to customize your layout; the order is saved automatically.
- Access advanced reports and analytics on the Reports page.

# Enjoy using PrivacyGuard!