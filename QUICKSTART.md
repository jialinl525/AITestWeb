# Quick Start Guide

## Step 1: Start the Backend

1. Open a terminal and enter the backend directory:
```bash
cd backend
```

2. Install Python dependencies (if not installed yet):
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python init_db.py
```

4. (Optional) Generate test data:
```bash
python seed_data.py
```

5. Start the backend service:
```bash
# Windows
python -m uvicorn main:app --reload --port 8000
# Or use the startup script
start.bat
```

The backend will run at http://localhost:8000

## Step 2: Start the Frontend

1. Open a new terminal window and enter the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the frontend dev server:
```bash
npm run dev
```

The frontend will run at http://localhost:5173

## Step 3: Access the App

Open http://localhost:5173 in your browser.

## Feature Check

### Test Progress Page
- View the test progress list
- Click “New Test” to create a test task
- Edit test status and progress

### Bug Tracking Page
- View the bug list and statistics
- Use filters to filter by status and severity
- Create, edit, and delete bugs

### KPI Performance Page
- Leaderboard: select metrics (accuracy, precision, etc.) to view model ranking
- Scatter plot: select X-axis and Y-axis metrics to compare model performance

## FAQ

### Backend Fails to Start
- Ensure Python version >= 3.8
- Check dependencies are installed: `pip install -r requirements.txt`
- Ensure port 8000 is not in use

### Frontend Fails to Start
- Ensure Node.js version >= 16
- Delete the `node_modules` folder, then run `npm install` again
- Ensure port 5173 is not in use

### Database Errors
- Run `python backend/init_db.py` to re-initialize the database
- If using SQLite, ensure you have write permission

### CORS Errors
- Ensure the backend CORS config includes the frontend address (default: http://localhost:5173)
- Check whether the backend service is running properly

## API Docs

After starting the backend, you can view the API docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
