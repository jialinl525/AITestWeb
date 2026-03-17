# Quick Start Guide

## Step 1: Start the Backend

1.Open a terminal and go to the backend directory:
cd backend

2.Install Python dependencies (if not installed yet):
pip install -r requirements.txt

3.Initialize the database:
python init_db.py

4.(Optional) Generate sample/test data:
python seed_data.py

5.Start the backend service:
# Windows
python -m uvicorn main:app --reload --port 8000

# Or use the startup script
start.bat
The backend will run at http://localhost:8000

## Step 2: Start the Frontend
Open a new terminal window and go to the frontend directory:

cd frontend
Install Node.js dependencies:

npm install
Start the frontend development server:

npm run dev
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
- View the leaderboard: select metrics (accuracy, precision, etc.) to see model ranking
- View the scatter plot: select X-axis and Y-axis metrics to compare model performance
## FAQ / Troubleshooting
### Backend Fails to Start
- Make sure Python version >= 3.8
- Check that all dependencies are installed: pip install -r requirements.txt
- Make sure port 8000 is not in use
### Frontend Fails to Start
- Make sure Node.js version >= 16
- Delete the node_modules folder and run npm install again
- Make sure port 5173 is not in use
### Database Errors
- Run python backend/init_db.py to re-initialize the database
- If using SQLite, make sure you have write permission
### CORS Errors
- Make sure the backend CORS configuration includes the frontend address (default is already configured as http://localhost:5173)
- Check whether the backend service is running properly
## API Docs
After starting the backend, you can access the API docs at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc