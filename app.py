import sqlite3 # import the sqlite3 module for database operations
from flask import Flask, request, render_template # import Flask and other necessary modules

app = Flask(__name__) # create a Flask application instance


def get_db():
    connection = sqlite3.connect("error_lookup.db") # connect to the SQLite database
    connection.row_factory = sqlite3.Row # set the row factory to return rows as dictionaries
    return connection # return the database connection

@app.route("/", methods=["GET", "POST"]) # define the route for the home page
def index():
    if request.method == "POST": # check if the request method is POST
        error_code = request.form["error_code"] # get the error code from the form data
        if not error_code: # check if the error code is empty
            return render_template("index.html", error="Please enter an error code.") # render the index.html template with an error message
        connection = get_db() # get the database connection
        cached_result = connection.execute("SELECT * FROM searches WHERE error_code = ?", (error_code,)).fetchone() # check if the error code is already in the database
        if cached_result: # if the error code is found in the database
            return render_template("index.html", error_code=error_code, result=cached_result) # render the index.html template with the cached result
        else: # if the error code is not found in the database
            summary = f"Summary for error code {error_code}" # create a summary for the error code
            connection.execute("INSERT INTO searches (error_code, source_api, result_summary) VALUES (?, ?, ?)", (error_code, "API", summary)) # insert the new error code and summary into the database
            connection.commit() # commit the changes to the database
        new_result = connection.execute("SELECT * FROM searches WHERE error_code = ?", (error_code,)).fetchone() # retrieve the newly inserted record
        connection.close() # close the database connection
        return render_template("index.html", error_code=error_code, result=new_result) # render the index.html template with the new result
    else:
        return render_template("index.html") # render the index.html template

if __name__ == "__main__": # check if the script is run directly
    app.run(debug=True) # run the Flask application in debug mode