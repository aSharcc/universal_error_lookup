import sqlite3

connection = sqlite3.connect("error_lookup.db")  # Connect to the SQLite database (or create it if it doesn"t exist)
try:
    with open ("schema.sql") as file:  # Open the schema.sql file
        connection.executescript(file.read())  # Execute the SQL commands in the schema.sql file
except FileNotFoundError:
    print("schema.sql file not found. Please ensure the file exists in the same directory as init_db.py.")  # Print an error message if the schema.sql file is not found
except sqlite3.Error as e:
    print(f"An error occurred while initializing the database: {e}")  # Print an error message if there was an issue

print("Database initialized successfully.")  # Print a success message