import sqlite3 

# opens a new connection and enforce foreign keys

def get_connection(): 
    con = sqlite3.connect("lockitdown.db")
    con.execute("PRAGMA foreign_keys = ON")
    return con

