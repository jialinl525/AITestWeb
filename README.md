# Test Management System

A front-end/back-end separated test management project based on Vue 3 + FastAPI. It is used to display test progress, track test bugs, and visualize test KPI performance.

## Features

1. **Test Progress Management**
   - View the test progress list
   - Create and edit test tasks
   - Display test progress percentage in real time
   - View test case statistics (pass/fail)

2. **Bug Tracking**
   - Bug list display and filtering
   - Bug statistics (total count, status distribution, severity distribution)
   - Create, edit, and delete bugs
   - View bugs by test task

3. **KPI Performance Dashboard**
   - Leaderboard chart: shows performance ranking of different models
   - Scatter plot: compares multiple metrics across models
   - Supports selecting multiple metrics (accuracy, precision, recall, F1 score, etc.)

4. **People & Permission Management**
   - User and permission group management
   - Supports adding users to `manager-group` to obtain test editing permissions
   - Linked with the “Test Owner” in test progress: view each person’s task count and time allocation

## Tech Stack

### Backend
- FastAPI - Modern, high-performance web framework
- SQLAlchemy - ORM framework
- SQLite - Database (can be switched to PostgreSQL)

### Frontend
- Vue 3 - Progressive JavaScript framework
- Vite - Fast frontend build tool
- Element Plus - Vue 3 component library
- ECharts - Data visualization charting library

## Project Structure

```bash
.
├── backend/              # Backend code
│   ├── routers/         # API routers
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   ├── database.py      # Database configuration
│   ├── main.py          # FastAPI app entry
│   └── requirements.txt # Python dependencies
├── frontend/            # Frontend code
│   ├── src/
│   │   ├── api/         # API calls
│   │   ├── views/       # Page components
│   │   ├── router/      # Router configuration
│   │   └── App.vue      # Root component
│   ├── package.json     # Frontend dependencies
│   └── vite.config.js   # Vite configuration
└── README.md
```

## Quick Start

### Requirements
- Python 3.8+
- Node.js 16+
- npm or yarn

### Start the Backend

1. Enter the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python init_db.py
```

4.1 If you already have an existing database, you need to run a migration to add new fields:
```bash
python migrate_db.py
```

> After adding the people management feature, it is recommended to run `python migrate_db.py` once to create user/permission-group related tables and populate the `estimated_hours` field.

5. Start the service:
```bash
uvicorn main:app --reload --port 8000
```

The backend service will start at http://localhost:8000

### Start the Frontend

1. Enter the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the dev server:
```bash
npm run dev
```

The frontend service will start at http://localhost:5173

## API Docs

After starting the backend service, you can view the API docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Usage

### Test Progress Management
1. On the “Test Progress” page, you can view the progress of all test tasks.
2. Click the “New Test” button to create a new test task.
3. You can edit test status, progress, and test case statistics.
4. Click “View Bugs” to see bugs related to the test.

### Bug Tracking
1. On the “Bug Tracking” page, you can view all bugs.
2. Use filters to filter bugs by status and severity.
3. Click the “New Bug” button to create a new bug record.
4. You can edit bug information or delete bugs.

### KPI Performance
1. On the “KPI Performance” page, you can view two charts:
   - **Leaderboard**: select metrics and a time range to view model performance ranking
   - **Scatter Plot**: select X-axis and Y-axis metrics to compare model performance

### People Management & Permission Grouping
1. On the “People Management” page, you can add users, edit users, and assign permission groups.
2. `manager-group` exists by default. Users added to this group can edit test progress and bugs.
3. When creating/editing tasks on the “Test Progress” page, the test owner can be selected directly from the people list.
4. The people management page automatically summarizes each person’s related tasks and estimated hours (for multi-owner tasks, hours are split evenly among owners).

Default admin account:
- Username: `manager`
- Password: `123456`

#### One-click: Add a User to manager-group

You can use the script: `backend/add_user_to_manager_group.py`

1. Add an existing user to manager-group only:
```bash
cd backend
python add_user_to_manager_group.py alice
```

2. If the user does not exist, create and add to manager-group automatically:
```bash
cd backend
python add_user_to_manager_group.py bob --create-if-missing --display-name "Bob" --password 123456
```

3. If the user exists but is disabled, add to group and enable automatically:
```bash
cd backend
python add_user_to_manager_group.py charlie --activate
```

### Manual KPI Data Import (Wide Table: One Model per Row)

KPI data is currently recommended to be imported via one-click CSV import. The new format is a wide table: each row describes one model, avoiding repeated `source/model_size/description`.

#### One-click CSV Import (Recommended)

The project includes a built-in script: `backend/import_kpi_csv.py`, which can import from CSV in batch into the database (does not depend on the API service being running).

1. If the database is an old version, migrate fields first:
```bash
cd backend
venv\Scripts\python migrate_db.py
```

2. Prepare the CSV (UTF-8, header row required). Columns:
- `model_category` (required, ASR/TTS/Translation/VoicecallTranslation Solution)
- `model_name` (required)
- `source` (optional)
- `model_size` (optional)
- `description` (optional)
- `power_consumption` (required, numeric)
- `latency` (required, numeric)
- `accuracy_en` (required, numeric)
- `accuracy_zh` (required, numeric)
- `accuracy_es` (required, numeric)
- `accuracy_overall` (required, numeric)
- `test_date` (optional, ISO datetime, e.g. `2026-03-14T10:30:00`)

3. CSV example:
```csv
model_category,model_name,source,model_size,description,power_consumption,latency,accuracy_en,accuracy_zh,accuracy_es,accuracy_overall,test_date
ASR,Model-A,Internal Benchmark Set A,1.2B,Lightweight model optimized for general speech recognition, emphasizing real-time transcription and on-device deployment capability.,72.8,118.4,0.946,0.931,0.919,0.932,
Translation,Model-F,Global Translation Benchmark v2,1.9B,Next-generation multilingual translation model with improved long-sentence semantic retention and cross-domain terminology consistency.,70.2,112.7,0.958,0.941,0.929,0.943,
```

4. Run one-click import:
```bash
cd backend
venv\Scripts\python import_kpi_csv.py .\\kpi_data_sample_5models.csv
```

5. To clear old KPI data before importing:
```bash
cd backend
venv\Scripts\python import_kpi_csv.py .\\kpi_data_sample_5models.csv --clear
```

> Note: This script is not compatible with the old long-table CSV format using `metric_name/metric_value`.

#### Quick Check: Verify Import Success

```bash
curl "http://localhost:8000/api/kpi/metrics?model_name=Model-A"
```

## Development Notes

### Add New API Endpoints
1. Create or modify router files in `backend/routers/`
2. Register routers in `backend/main.py`
3. Define data schemas in `backend/schemas.py` (if needed)

### Add New Frontend Pages
1. Create Vue components in `frontend/src/views/`
2. Add route config in `frontend/src/router/index.js`
3. Add menu items in `frontend/src/App.vue` (if needed)

## Database

SQLite is used by default; the database file is `backend/test_management.db`.

To use PostgreSQL:
1. Update the database URL in `backend/database.py`
2. Install PostgreSQL and create a database
3. Update the database driver in `requirements.txt`

## License

MIT License
