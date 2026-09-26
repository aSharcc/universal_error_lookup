import sqlite3

try:
    with sqlite3.connect("error_lookup.db") as connection:
        with open("schema.sql") as file:
            connection.executescript(file.read())
            print("Database initialized successfully.")
except FileNotFoundError:
    print("schema.sql file not found. Please ensure the file exists in the same directory as init_db.py.")
except sqlite3.Error as e:
    print(f"An error occurred while initializing the database: {e}")