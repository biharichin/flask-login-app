import mysql.connector
from flask import g
import os

def get_db():
    """
    Opens a new database connection if there is none yet for the
    current application context.
    """
    if 'db' not in g:
        try:
            g.db = mysql.connector.connect(
                host=os.environ.get("DB_HOST"),
                user=os.environ.get("DB_USER"),
                password=os.environ.get("DB_PASSWORD"),
                database=os.environ.get("DB_NAME"),
                port=3306
            )
        except mysql.connector.Error as e:
            # If connection fails, you might want to handle it gracefully
            # For now, we let the exception propagate to be caught by Flask
            raise e
    return g.db

def close_db(e=None):
    """
    Closes the database connection if it exists. This function is
    registered to be called when the application context is torn down.
    """
    db = g.pop('db', None)

    if db is not None and db.is_connected():
        db.close()