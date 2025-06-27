import os
import sys
import json
import csv
import time
import math
import random
import string
import datetime
import re
from collections import defaultdict, Counter, namedtuple
from typing import List, Dict, Any, Tuple


# ------------------- File & Directory Utilities -------------------

def list_files_in_directory(directory: str) -> List[str]:
    try:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    except Exception as e:
        print(f"Error listing files in {directory}: {e}")
        return []


def create_directory(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def write_json(filepath: str, data: Dict):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)


def read_json(filepath: str) -> Dict:
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to read JSON: {e}")
        return {}


# ------------------- String Utilities -------------------

def random_string(length: int = 10) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def is_valid_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


# ------------------- Math Utilities -------------------

def compute_mean(numbers: List[float]) -> float:
    return sum(numbers) / len(numbers) if numbers else 0.0


def compute_std_dev(numbers: List[float]) -> float:
    mean = compute_mean(numbers)
    return math.sqrt(sum((x - mean) ** 2 for x in numbers) / len(numbers)) if numbers else 0.0


# ------------------- CSV Utilities -------------------

def write_csv(filepath: str, data: List[Dict[str, Any]], headers: List[str]):
    try:
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        print(f"Failed to write CSV: {e}")


def read_csv(filepath: str) -> List[Dict[str, str]]:
    try:
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        print(f"Failed to read CSV: {e}")
        return []


# ------------------- Data Models -------------------

Person = namedtuple("Person", ["name", "email", "age"])

class User:
    def __init__(self, name: str, email: str, age: int):
        self.name = name
        self.email = email
        self.age = age
        self.created_at = datetime.datetime.now()
        self.logs = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "email": self.email,
            "age": self.age,
            "created_at": self.created_at.isoformat()
        }

    def log(self, message: str):
        timestamp = datetime.datetime.now().isoformat()
        self.logs.append(f"{timestamp} - {message}")

    def __str__(self):
        return f"User(name={self.name}, email={self.email}, age={self.age})"


# ------------------- Simulated App -------------------

class GenericApp:
    def __init__(self):
        self.users: Dict[str, User] = {}

    def add_user(self, name: str, email: str, age: int):
        if email in self.users:
            print(f"User with email {email} already exists.")
            return
        if not is_valid_email(email):
            print("Invalid email address.")
            return
        user = User(name, email, age)
        self.users[email] = user
        user.log("User added.")
        print(f"Added: {user}")

    def remove_user(self, email: str):
        if email in self.users:
            del self.users[email]
            print(f"Removed user with email {email}.")
        else:
            print("User not found.")

    def list_users(self):
        for user in self.users.values():
            print(user)

    def export_users(self, filepath: str):
        data = [user.to_dict() for user in self.users.values()]
        headers = list(data[0].keys()) if data else []
        write_csv(filepath, data, headers)
        print(f"Exported users to {filepath}")


# ------------------- Miscellaneous Utilities -------------------

def wait_with_dots(seconds: int):
    for i in range(seconds):
        print('.', end='', flush=True)
        time.sleep(1)
    print()


def show_datetime_info():
    now = datetime.datetime.now()
    print("Current time:", now)
    print("ISO format:", now.isoformat())
    print("Weekday:", now.strftime("%A"))
    print("Day of year:", now.timetuple().tm_yday)


def generate_dummy_users(app: GenericApp, count: int):
    for _ in range(count):
        name = random_string(7)
        email = f"{name.lower()}@example.com"
        age = random.randint(18, 65)
        app.add_user(name, email, age)


# ------------------- Main Logic -------------------

def main():
    print("Welcome to the Generic Python App!")
    app = GenericApp()

    generate_dummy_users(app, 5)
    print("\nListing Users:")
    app.list_users()

    print("\nWaiting a bit...")
    wait_with_dots(3)

    print("\nDateTime Info:")
    show_datetime_info()

    print("\nExporting to users.csv")
    app.export_users("users.csv")

    print("\nReading users.csv")
    users_csv = read_csv("users.csv")
    for row in users_csv:
        print(row)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

import threading
import queue
import uuid
import hashlib
import logging
import shutil
import tempfile

from functools import lru_cache, wraps
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------- Caching Utilities -------------------

@lru_cache(maxsize=128)
def expensive_computation(x):
    logger.info(f"Computing expensive_computation({x})")
    time.sleep(2)
    return x ** 2 + x

# ------------------- Decorators -------------------

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper

# ------------------- File Backup Utilities -------------------

def backup_file(src_path):
    try:
        backup_path = src_path + ".bak"
        shutil.copy(src_path, backup_path)
        logger.info(f"Backed up {src_path} to {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return None

# ------------------- UUID & Hash Utilities -------------------

def generate_uuid() -> str:
    return str(uuid.uuid4())

def hash_string(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

# ------------------- Queue and Threads -------------------

class Worker(threading.Thread):
    def __init__(self, q):
        super().__init__()
        self.q = q
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args = self.q.get()
            try:
                logger.info(f"Running: {func.__name__} with args: {args}")
                func(*args)
            except Exception as e:
                logger.error(f"Error in worker thread: {e}")
            self.q.task_done()

# ------------------- Minimal Web Server -------------------

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<html><body><h1>Hello from Python Server!</h1></body></html>")


def start_web_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHandler)
    logger.info(f"Starting server on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server.")
        httpd.server_close()

# ------------------- Temporary File Utilities -------------------

def write_temp_file(content: str) -> str:
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt')
    temp_file.write(content)
    temp_file.close()
    logger.info(f"Temp file written to: {temp_file.name}")
    return temp_file.name

# ------------------- Execute When Run Directly -------------------

if __name__ == '__main__':
    print("Generated UUID:", generate_uuid())
    print("Hash of 'example':", hash_string("example"))

    print("Performing expensive computation with cache:")
    print(expensive_computation(10))
    print(expensive_computation(10))  # Cached

    # Setup and run a worker thread
    q = queue.Queue()
    worker = Worker(q)

    def dummy_task(x):
        print(f"Dummy task executed with {x}")

    q.put((dummy_task, (42,)))
    q.join()

    # Start web server in a thread
    threading.Thread(target=start_web_server, daemon=True).start()

    # Wait a moment for server to start
    time.sleep(2)

    # Write temp file
    write_temp_file("This is a temporary test.")

    # Back up an example file
    test_file = write_temp_file("backup test content")
    backup_file(test_file)

    print("All tasks completed. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Goodbye!")
