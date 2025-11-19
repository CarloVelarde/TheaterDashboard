from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from app.db import get_connection
from app.routers import movies, tickets, reports

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


# Include routers
app.include_router(movies.router, prefix="/api")
app.include_router(tickets.router, prefix="/api")
app.include_router(reports.router, prefix="/api")

# Serve static frontend (needs to be implemented)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
