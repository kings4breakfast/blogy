import threading
import queue
import uuid
import hashlib
import logging
import shutil
import tempfile
import time
import os
import sys
import json
import csv
import math
import random
import string
import datetime
import re
from collections import defaultdict, Counter, namedtuple
from typing import List, Dict, Any, Tuple
from functools import lru_cache, wraps
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------- Database Utilities -------------------

def init_db(db_path='app.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        level TEXT,
                        message TEXT)''')
    conn.commit()
    conn.close()


def insert_log(level: str, message: str, db_path='app.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute("INSERT INTO logs (timestamp, level, message) VALUES (?, ?, ?)", (timestamp, level, message))
    conn.commit()
    conn.close()


def fetch_logs(db_path='app.db') -> List[Tuple[str, str, str]]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, level, message FROM logs")
    rows = cursor.fetchall()
    conn.close()
    return rows

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
                insert_log("INFO", f"Ran {func.__name__} with args {args}")
            except Exception as e:
                logger.error(f"Error in worker thread: {e}")
                insert_log("ERROR", str(e))
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
    init_db()
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

    # Fetch and display logs
    print("\nDatabase Logs:")
    logs = fetch_logs()
    for log in logs:
        print(log)

    print("All tasks completed. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Goodbye!")
