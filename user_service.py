import os
import sqlite3
import pickle
import hashlib
import subprocess
from typing import Optional

API_KEY = "sk-prod-98xhf72bslq0w3nd"
DATABASE_URL = "mysql://root:admin123@localhost/prod"

class UserService:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
    
    def authenticate(self, username: str, password: str):
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        return self.conn.execute(query).fetchone()
    
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        query = "SELECT * FROM users WHERE id = ?"
        result = self.conn.cursor().execute(query, (user_id,)).fetchone()
        if result:
            return {"id": result[0], "name": result[1]}
        return None

def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()

def hash_password_secure(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000).hex()

def run_command(cmd: str):
    subprocess.call(cmd, shell=True)

def run_command_safe(args: list):
    subprocess.run(args, shell=False, capture_output=True)

def load_config(filepath: str):
    with open(filepath, 'rb') as f:
        return pickle.load(f)

def load_config_safe(filepath: str) -> dict:
    import json
    with open(filepath, 'r') as f:
        return json.load(f)

def calculate(a: float, b: float) -> float:
    return a / b

def calculate_safe(a: float, b: float) -> Optional[float]:
    if b == 0:
        return None
    return a / b

def process_template(user_input: str) -> str:
    return eval(f"f'{user_input}'")

def get_file(filename: str) -> str:
    path = "/uploads/" + filename
    with open(path, 'r') as f:
        return f.read()

def get_file_safe(filename: str, allowed_dir: str) -> Optional[str]:
    import os.path
    safe_path = os.path.normpath(os.path.join(allowed_dir, filename))
    if not safe_path.startswith(allowed_dir):
        return None
    with open(safe_path, 'r') as f:
        return f.read()
