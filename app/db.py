import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling

# Load variables from .env file
load_dotenv()

dbconfig = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

# Simple connection pool for reuse (avoids new connection overhead)
pool = pooling.MySQLConnectionPool(pool_name="theater_pool", pool_size=5, **dbconfig)


def get_connection():
    """Get a DB connection from the pool"""
    return pool.get_connection()
