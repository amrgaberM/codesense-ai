import os
import sqlite3
import pickle
import subprocess
import requests

# Hardcoded secrets
API_KEY = "sk-prod-98xhf72bslq0w3nd"
DB_PASSWORD = "admin@123!"
SECRET_TOKEN = "token_987654321"

# Vulnerable database query
def authenticate(username, password):
    query = f"SELECT * FROM users WHERE user='{username}' AND pass='{password}'"
    conn = sqlite3.connect("users.db")
    return conn.execute(query).fetchall()

# Remote code execution risk
def execute_task(user_command):
    os.system(user_command)  # Critical vulnerability

# Pickle deserialization vulnerability
def load_session(filepath):
    return pickle.load(open(filepath, 'rb'))

# Arithmetic bug
def calculate_ratio(a, b):
    return a / b  # Potential division by zero

# Eval vulnerability
def process_input(data):
    return eval(data)

# Command injection
def run_script(script_name):
    subprocess.call(f"bash {script_name}", shell=True)

# Hardcoded API call
def send_request(user_id):
    url = f"https://api.example.com/data?user={user_id}&key={API_KEY}"
    return requests.get(url).json()

# Missing input validation
def sum_list(items):
    return sum(items)  # No type checking, can crash if items contain non-numbers

# Logic error example
def check_access(role):
    if role = "admin":  # Syntax error (intentional)
        return True
    return False
