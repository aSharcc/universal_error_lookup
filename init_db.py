import sqlite3

connection = sqlite3.connect("error_lookup.db")  # Connect to the SQLite database (or create it if it doesn"t exist)

with open ("schema.sql") as file:  # Open the schema.sql file
    connection.executescript(file.read())  # Execute the SQL commands in the schema.sql file

connection.commit()  # Commit the changes to the database
connection.close()  # Close the database connection

print("Database initialized successfully.")  # Print a success message