# Test Management System
A front-end/back-end separated test management project based on Vue 3 + FastAPI. It is used to display test progress, track test bugs, and present test KPI performance.
Features
1. Test Progress Management
• View the test progress list
• Create and edit test tasks
• Display test progress percentage in real time
• View test case statistics (pass/fail)
2. Bug Tracking
• Bug list display and filtering
• Bug statistics (total count, status distribution, severity distribution)
• Create, edit, delete bugs
• View bugs by test task
3. KPI Performance Dashboard
• Leaderboard chart: shows performance ranking across different models
• Scatter plot: compares multiple metrics across different models
• Supports multiple metric selections (accuracy, precision, recall, F1-score, etc.)
4. People & Permission Management
• User and permission group management
• Supports adding users to manager-group to obtain test editing permissions
• Links with “Test Owner” in test progress: view each person’s task count and time allocation
Tech Stack
Backend
• FastAPI - Modern, high-performance web framework
• SQLAlchemy - ORM framework
• SQLite - Database (can be switched to PostgreSQL)
Frontend
• Vue 3 - Progressive JavaScript framework
• Vite - Fast frontend build tool
• Element Plus - Vue 3 component library
• ECharts - Data visualization charting library
Project Structure

.
├── backend/              # Backend code
│   ├── routers/         # API routers
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   ├── database.py      # DB configuration
│   ├── main.py          # FastAPI entry
│   └── requirements.txt # Python dependencies
├── frontend/            # Frontend code
│   ├── src/
│   │   ├── api/         # API calls
│   │   ├── views/       # Page components
│   │   ├── router/      # Router config
│   │   └── App.vue      # Root component
│   ├── package.json     # Frontend dependencies
│   └── vite.config.js   # Vite config
└── README.md
Quick Start
Requirements
• Python 3.8+
• Node.js 16+
• npm or yarn
Start the Backend
1. Go to the backend directory:

cd backend
2. Create a virtual environment (recommended):

python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
3. Install dependencies:

pip install -r requirements.txt
4. Initialize the database:

python init_db.py
4.1 If you already have a database, run migration to add new fields:

python migrate_db.py
After adding the personnel management feature, it is recommended to run python migrate_db.py once to create the user/permission-group related tables and populate the estimated_hours field.
5. Start the service:

uvicorn main:app --reload --port 8000
The backend will start at http://localhost:8000
Start the Frontend
1. Go to the frontend directory:

cd frontend
2. Install dependencies:

npm install
3. Start the dev server:

npm run dev
The frontend will start at http://localhost:5173
API Documentation
After starting the backend service, you can visit:
• Swagger UI:  http://localhost:8000/docs
• ReDoc:  http://localhost:8000/redoc
Usage Guide
Test Progress Management
1. On the “Test Progress” page, you can view the progress of all test tasks
2. Click “New Test” to create a new test task
3. You can edit test status, progress, and test case statistics
4. Click “View Bugs” to see bugs related to that test
Bug Tracking
1. On the “Bug Tracking” page, you can view all bugs
2. Use filters to filter bugs by status and severity
3. Click “New Bug” to create a new bug record
4. You can edit bug info or delete bugs
KPI Performance
1. On the “KPI Performance” page, you can view two charts:
• Leaderboard: choose metrics and time range to view model performance ranking
• Scatter plot: choose X and Y axis metrics to compare model performance
People Management & Permission Groups
1. On the “People Management” page, you can add users, edit users, and assign permission groups.
2. The system includes a default manager-group. Users in this group can edit test progress and bugs.
3. When creating/editing tasks on the “Test Progress” page, the test owner can be selected directly from the user list.
4. The People Management page automatically summarizes each person’s related tasks and estimated hours usage (for multi-person tasks, hours are evenly split among members).
Default admin account:
• Username: manager
• Password: 123456
One-click: Add a User to manager-group
You can use the script: backend/add_user_to_manager_group.py
1. Add an existing user to manager-group only:

cd backend
python add_user_to_manager_group.py alice
2. If the user does not exist, auto-create and add to manager-group:

cd backend
python add_user_to_manager_group.py bob --create-if-missing --display-name "Bob" --password 123456
3. If the user exists but is disabled, add to the group and auto-activate:

cd backend
python add_user_to_manager_group.py charlie --activate
Manual KPI Data Import (Wide Table: One Row per Model)
KPI data is currently recommended to be imported via CSV in one shot. The new format is a wide table: each row describes only one model, avoiding repetition of source/model_size/description.
CSV One-shot Import (Recommended)
The project includes a built-in script: backend/import_kpi_csv.py, which can batch import from CSV into the database directly (no need to start the API service).
1. If the database is an old version, migrate fields first:

cd backend
venv\Scripts\python migrate_db.py
2. Prepare the CSV (UTF-8 encoded, header row required). Columns:
• model_category (required, ASR/TTS/Translation/VoicecallTranslation Solution)
• model_name (required)
• source (optional)
• model_size (optional)
• description (optional)
• power_consumption (required, numeric)
• latency (required, numeric)
• accuracy_en (required, numeric)
• accuracy_zh (required, numeric)
• accuracy_es (required, numeric)
• accuracy_overall (required, numeric)
• test_date (optional, ISO time, e.g. 2026-03-14T10:30:00)
3. CSV example:

model_category,model_name,source,model_size,description,power_consumption,latency,accuracy_en,accuracy_zh,accuracy_es,accuracy_overall,test_date
ASR,Model-A,Internal Benchmark Set A,1.2B,"A lightweight model optimized for general speech recognition, emphasizing real-time transcription and on-device deployment.",72.8,118.4,0.946,0.931,0.919,0.932,
Translation,Model-F,Global Translation Benchmark v2,1.9B,"A next-generation multilingual translation model, enhanced for long-sentence semantic preservation and cross-domain terminology consistency.",70.2,112.7,0.958,0.941,0.929,0.943,
4. Run one-shot import:

cd backend
venv\Scripts\python import_kpi_csv.py .\kpi_data_sample_5models.csv
5. If you need to clear old KPI data before importing:

cd backend
venv\Scripts\python import_kpi_csv.py .\kpi_data_sample_5models.csv --clear
Note: The current script is not compatible with the old long-table CSV format (metric_name/metric_value).
Quick Check: Verify Import Success

curl "http://localhost:8000/api/kpi/metrics?model_name=Model-A"
Development Notes
Add New API Endpoints
1. Create or modify router files under backend/routers/
2. Register routes in backend/main.py
3. Define data schemas in backend/schemas.py (if needed)
Add New Frontend Pages
1. Create Vue components under frontend/src/views/
2. Add routes in frontend/src/router/index.js
3. Add menu items in frontend/src/App.vue (if needed)
Database
SQLite is used by default. The DB file is backend/test_management.db.
If you want to use PostgreSQL:
1. Modify the database URL in backend/database.py
2. Install PostgreSQL and create a database
3. Update the DB driver in requirements.txt
License
MIT License