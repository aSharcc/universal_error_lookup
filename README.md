# UNIVERSAL ERROR CODE LOOKUP

[Video Demo](https://youtu.be/GXGimSqpsr4)

#### Description:

This is a webapp, designed to help software engineers, system admins, students, even gamers to easily and quickly understand and solve error codes.

**To accomplish this I implemented:**
- **Database lookup:** Checks the local database for stored problems and solutions.
- **Public API lookup:** If not found yet, queries APIs such as `httpstatuses.io/` to attempt to retrieve information and solutions.
- **OS system-level error code lookup:** If not found yet,  attempts to retrieve data from Python's native `os.sterror`.
- **AI-Generated Solutiuons:** If no solution can be found, the application querries Google Gemini model `models/gemini-3.8-flash` to generate a concise description and cause.
- **Solution Caching:** When a new solution is retrieved, it is cached into the database to reduce API usage and increase efficiency.
- **Targeted Deep Links:** Users are provided with buttons to send them to pre-filtered search queries on Google, Reddit, and Stack Overflow.
- **User Submitted Solutions:** Users are also able to view and upload solutions made by others and vote on these. The results are dynamically ordered by votes and have integrated pagination.

## File Structure and contents

### `app.py`
This is the primary application written in Flask. It handles routes, databases, API lookup and voting.
- **`init_db()`:** Checks if the database exists, if not, a new one is created following a script from `schema.sql`.
- **`get_db()`:** Manages SQLite database connection, creating dictionaries for easy access to information.
- **`get_http_error(error_code)`:** First, evaluates whether error code could be a HTTP error, if so, queries HTTP statuses API over HTTPS using `requests`
- **`get_system_error(error_code)`:** Looks up the error code, if it is a digit, to the OS's standard errors via `os.sterror`.
- **`get_error_from_ai(error_code, context)`:** Connects to Google GenAI, providing the user submitted error code and context.
- **`get_error_info`:** Orchestrates the retrieval of error codes from the 3 aforementioned methods.
- **`index()` (`"/"` Route):**  Handles both GET and POST methods for error searches, depending on request source. Checks the local database for cached results, inserts new results, calculates and provides pagination and renders the `index.html` page.
- **`add_solution()` (`/add_solution` Route):** Processes user submitted solutions, verifies them and inserts them into the `solutions` database.
- **`vote()` (`/vote` route):** Manges community votes on solutions. To prevent duplicate votes, uses sessions to track voted solutions.

### `init_db.py`
A script that initialises the database using the script from `schema.sql`.

### `templates/index.html`
The Jinja2 template for the frontend webpage. It is built on PICO CSS for a clean design.
- Input for error code and optional context. 
- Conditional logic, if a part has no information, does not render to keep page clean.
- Paginated user submitted solutions. Uses GET to pass querry back to `"/"` to retrieve next page of inforamtion.

### `requirments.txt`
Specifies all python package dependancies.

## How to run

1. Clone repo and enter the directiory
2. **Install Dependancies:** `pip install -r requirments.txt`
3. **Setup environmental variables:** `export GEMINI_API_KEY="your-api-key-here"` ([Get Gemini API key](https://aistudio.google.com/api-keys))
4. **Initialise Database:** `py init_db.py`
5. **Launch application:** `py app.py`
6. **Navigate to webapp:** `http://127.0.0.1:5000`