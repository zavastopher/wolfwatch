# `/api` - WolfWatch's REST API
`cjcuddy` - Cade Cuddy<br/>
`czavala2` - Chris Zavala

### 📁 `models`
_Data models used by the application._
  - `custom_sql_types.py`: Hacky module for converting the MySQL type LONGTEXT to a type usable with sqlite (for our unit tests)
  - `models.py`: Central place where all the database table models are defined for use in SQLAlchemy ORM.

### 📁 `routes`
_The application's main route handlers live here. Each file corresponds to a specific feature or resource._
  - `assignments.py`: Handles CRUD operations related to assignments.
  - `auth.py`: Manages authentication routes and user authorization.
  - `email.py`: Routes related to password resetting (and the emails that are sent in that process)
  - `instructor.py`: Defines the routes related to instructor data and actions.
  - `results.py`: Manages routes related to scanning results.

### 📁 `test`
_Contains unit tests for the application. Any new features or changes should have corresponding tests added here._

#### 🧪 Running Tests & Getting Coverage Numbers
1. Install the required python libraries: 
`pip install -r requirements.txt`
2. **Change into the test directory:** `cd test/`
3. Run the tests: `coverage run -m pytest *`
4. Get coverage report with: `coverage report -m --include="server.py,../routes/*.py"`

### 🔧 Utility & Configuration Files
- `config.py`: Central configuration file for the Flask app. Contains settings for different environments (development, production, etc.).
- `Dockerfile` & `Dockerfile.dev`: These files are used to containerize the application for deployment and development respectively.
- `extensions.py`: Initializes and configures extensions used throughout the app (e.g., database, logger).
- `requirements.txt`: Lists all the Python package dependencies needed for the application.
- `server.py`: The entry point for the Flask application. Initializes and runs the app.

### 📄 Others
- `log`: Directory that may contain log files for the application, helping in debugging and tracking issues. Generated upon first server startup.

---

For developers new to the system, it's advisable to first familiarize yourself with the files inside the `models` and `routes` directories, as they form the core business logic of the application. 

If you're looking to deploy or adjust configurations, the `Dockerfile`, `config.py`, and `extensions.py` would be the relevant files. **Always ensure to run/add/update tests in the `test` directory when introducing changes.**