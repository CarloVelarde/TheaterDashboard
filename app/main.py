from fastapi import FastAPI, HTTPException
from app.db import get_connection

app = FastAPI(title="Movie Theater Dashboard")


@app.get("/health")
def health_check():
    """
    Simple health endpoint to check that FastAPI is running and DB connection works
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return {"status": "ok", "db": row[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
