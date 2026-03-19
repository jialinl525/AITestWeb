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

### KPI Schema-Driven Import and Extension

KPI category/metric definitions are now centralized in one place:
- `backend/kpi_schema.py`

The following components all read from this schema:
- `backend/routers/kpi.py`
- `backend/import_kpi_csv.py`
- `frontend/src/views/KPI.vue` (via API `GET /api/kpi/schema`)

This means: when adding a new KPI model type or metric, you only need to modify `backend/kpi_schema.py`.

#### Generate CSV Templates from Schema

Use template generator to avoid manual header mistakes:

```bash
cd backend
venv\Scripts\python generate_kpi_csv_templates.py --all --output-dir .\kpi_templates --include-example
```

Or generate for specific categories only:

```bash
cd backend
venv\Scripts\python generate_kpi_csv_templates.py --category ASR --category "LPI Recording" --output-dir .\kpi_templates
```

#### Import KPI Data by Category (Strict Mode)

Each CSV should contain one category only, and must include that category's metric columns from schema.

```bash
cd backend
venv\Scripts\python import_kpi_csv.py .\kpi_templates\kpi_asr.csv --category ASR --clear
venv\Scripts\python import_kpi_csv.py .\kpi_templates\kpi_translation.csv --category Translation
```

> `--clear` should be used only on the first import when rebuilding KPI data.

#### Add New KPI Category / Metric (One-Place Change)

1. Edit `backend/kpi_schema.py`:
- Add a new item in `categories` with `key`, `label`, `description`
- Add metrics with `key`, `label`, `unit`, `direction`, `chart_roles`

2. (Optional) Add aliases:
- `category_aliases`
- `metric_aliases`
- `metric_filter_aliases`

3. Restart backend service.

4. Regenerate templates:

```bash
cd backend
venv\Scripts\python generate_kpi_csv_templates.py --all --output-dir .\kpi_templates --include-example
```

5. Fill CSV data and import with `import_kpi_csv.py`.

#### Quick Check: Verify Schema and Data

```bash
curl "http://localhost:8000/api/kpi/schema"
curl "http://localhost:8000/api/kpi/models/latest"
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
