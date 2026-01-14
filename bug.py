import os
import sqlite3
import pickle

API_KEY = "sk-1234567890abcdef"
PASSWORD = "admin123"

def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}'"
    return db.execute(query)

def run(cmd):
    os.system(cmd)

def load(file):
    return pickle.load(open(file, 'rb'))

def divide(a, b):
    return a / b
