import sqlite3 # import the sqlite3 module for database operations
from flask import Flask, request, render_template, redirect, session, flash, url_for # import Flask and other necessary modules
import requests # import the requests module for making HTTP requests
import os # import the os module for interacting with the operating system
from google import genai # import the genai module from the google package for AI functionality

app = Flask(__name__) # create a Flask application instance
app.secret_key = os.urandom(24)

DATABASE = "error_lookup.db"

def init_db():
    if not os.path.exists("schema.sql"):
        print("Schema.sql not found !!")
        return
    with sqlite3.connect(DATABASE) as connection:
        with open("schema.sql") as file:
            connection.executescript(file.read())

def get_db():
    connection = sqlite3.connect(DATABASE) # connect to the SQLite database
    connection.row_factory = sqlite3.Row # set the row factory to return rows as dictionaries
    return connection # return the database connection

def get_http_error(error_code):
    if error_code.isdigit() and len(error_code) == 3: # check if the error code is a 3-digit number
        try:
            url = f"https://httpstatuses.io/{error_code}.json" # define the URL for the HTTP statuses API
            response = requests.get(url, timeout=5) # make a GET request to the URL with a timeout
            if response.status_code == 200: # check if the response status code is 200 (OK)
                data = response.json() # parse the JSON response
                summary = f"{data.get('title')}: {data.get('description')}" # create a summary from the title and description
                return ("HTTP Statuses API", summary) # return the parsed JSON data
        except requests.RequestException:
            return None
    else:
        return None # return None if the request was not successful

def get_system_error(error_code):
    if error_code.isdigit():
        try:
            message = os.strerror(int(error_code)) # get the system error message for the given error code
            if message and "Unknown error" not in message: # check if the message is valid and not unknown
                return ("OS System Error", f"System error {error_code}: {message}") # return the system error message
        except ValueError:
            return None # return None if the error code is not valid
    else: 
        return None # return None if the error code is not a digit

def get_error_from_ai(error_code, context):
    try:
        client = genai.Client() # create a client instance for the Google GenAI API

        contents=(
            f"Explain technical error code '{error_code}' in 2-3 concise sentences. "
            f"State what causes it and how to fix it. "
            f"Context: {context if context else 'No additional context provided.'}"
        )

        response = client.models.generate_content( 
            model="models/gemini-3.5-flash-lite", 
            contents=contents
        )
        return ("AI Generated", response.text.strip()) # return the AI-generated explanation of the error code
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return ("Manual Search Needed", f"Could not retrieve information for error code {error_code}. Please search using links below.") # return a message indicating that manual search is needed

def get_error_info(error_code, context):
    http_result = get_http_error(error_code)
    if http_result:
        return http_result
    system_result = get_system_error(error_code)
    if system_result:
        return system_result
    return get_error_from_ai(error_code, context) # call the AI function to get error information if not found in HTTP or system errors

@app.route("/", methods=["GET", "POST"]) # define the route for the home page
def index():
    error_code = request.form.get("error_code", "").strip() or request.args.get("error_code", "").strip() # get the error code from the form data
    context = (request.form.get("context") or request.args.get("context") or "").strip()
    page = request.args.get("page", 1, type=int) or request.form.get("page", 1, type=int)

    print(page)

    if error_code: # check if the error code is empty
        connection = get_db() # get a database connection
        try:
            cached_result = connection.execute(
                "SELECT source_api, result_summary, context FROM searches WHERE error_code = ? AND context = ?",
                (error_code, context)
            ).fetchone() # check if the error code is already in the database

            if cached_result: # if the error code is found in the database
                result_data = {
                    "error_code": error_code,
                    "source_api": cached_result["source_api"],
                    "result_summary": cached_result["result_summary"],
                    "context": cached_result["context"]
                }
            else: # if the error code is not found in the database
                source_api, summary = get_error_info(error_code, context) # call the error information lookup function
                result_data = {
                    "error_code": error_code,
                    "source_api": source_api,
                    "result_summary": summary,
                    "context": context
                }
                if source_api != "Manual Search Needed": # if the source API is not "Manual Search Needed"
                    connection.execute(
                        "INSERT OR IGNORE INTO searches (error_code, source_api, result_summary, context) VALUES (?, ?, ?, ?)",
                        (error_code, source_api, summary, context)
                    ) # insert the new error code and summary into the database
                    connection.commit() # commit the changes to the database

            offset = (page-1) * 10

            user_solutions = connection.execute(
                "SELECT id, solution, author, votes FROM solutions WHERE error_code = ? ORDER BY votes DESC LIMIT 10 OFFSET ?",
                (error_code, offset)
            ).fetchall() # fetch all solutions for the given error code

            total_count = connection.execute(
                "SELECT COUNT(*) FROM solutions WHERE error_code = ?",
                (error_code,)
            ).fetchone()[0]
        finally:
            connection.close() # close the database connection

        voted_solutions = session.get("voted_solutions", []) 

        return render_template(
            "index.html",
            error_code=error_code, 
            result=result_data, context=context, 
            user_solutions=user_solutions,
            voted_solutions=voted_solutions,
            page=page,
            total_count=total_count
        ) # render the index.html template with the new result

    return render_template("index.html")
        
    

@app.route("/add_solution", methods=["POST"]) # define the route for the searches page
def add_solution():
    error_code = request.form.get("error_code", "").strip() # get the error code from the form data
    author = request.form.get("author", "").strip() # get the author from the form data
    solution = request.form.get("solution", "").strip() # get the solution from the form
    context = (request.form.get("context") or "").strip()

    if not error_code or not author or not solution: # check if any of the required fields are empty
        flash("Please fill all required fields.")
        return redirect(url_for("index", error_code=error_code, context=context))

    connection = get_db() # get a database connection
    try:
        connection.execute(
            "INSERT INTO solutions (error_code, solution, author, context, votes) VALUES (?, ?, ?, ?, 0)",
            (error_code, solution, author, context)
        ) # insert the new solution into the database
        connection.commit() # commit the changes to the database
    finally:
        connection.close() # close the database connection
    return redirect(url_for("index", error_code=error_code, context=context))

@app.route("/vote", methods=["POST"]) # define the route for the searches page
def vote():
    solution_id = request.form.get("solution_id") # get the solution ID from the query parameters
    vote_type = request.form.get("vote_type") # get the vote type from the query parameters (upvote or downvote)
    error_code = request.form.get("error_code")
    context = request.form.get("context", "").strip()
    page = request.form.get("page", 1, type=int)

    if "voted_solutions" not in session:
        session["voted_solutions"] = []

    if solution_id: # check if the solution ID is provided
        solution_id_int = int(solution_id)

        if solution_id_int not in session["voted_solutions"]:
            connection = get_db() # get a database connection
            try:
                if vote_type == "upvote": # check if the vote type is upvote
                    connection.execute(
                        "UPDATE solutions SET votes = votes + 1 WHERE id = ?",
                        (solution_id,)
                    ) # increment the vote count for the specified solution ID
                    connection.commit() # commit the changes to the database
                elif vote_type == "downvote": # check if the vote type is downvote
                    connection.execute(
                        "UPDATE solutions SET votes = votes - 1 WHERE id = ?",
                        (solution_id,)
                    ) # decrement the vote count for the specified solution ID
                    connection.commit() # commit the changes to the database
                session["voted_solutions"].append(solution_id_int)
                session.modified = True
            finally:
                connection.close() # close the database connection

            return redirect(url_for("index", error_code=error_code, context=context, page=page))
        
    return redirect("/")
    
if __name__ == "__main__": # check if the script is run directly
    init_db()
    app.run(debug=True) # run the Flask application in debug mode