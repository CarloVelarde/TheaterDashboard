from typing import List

from fastapi import APIRouter, HTTPException

from app.db import get_connection
from app.models import ShowtimeRead

router = APIRouter(
    prefix="/showtimes",
    tags=["showtimes"],
)


@router.get(
    "",
    response_model=List[ShowtimeRead],
    summary="List all showtimes",
    description=(
        "Returns all showtimes in the system. "
        "Useful for populating dropdowns when selecting a showtime "
        "for ticket purchase or checking availability."
    ),
)
def list_showtimes():
    """
    General endpoint:

    - Output: list of all showtimes with IDs, movie IDs, auditorium IDs,
      and start/end times.

    Implementation notes:
    - Simple SELECT from Showtimes table.
    """
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                ShowtimeID AS showtime_id,
                MovieID    AS movie_id,
                TheaterID  AS theater_id,
                StartTime  AS start_time,
                EndTime    AS end_time
            FROM Showtimes
            ORDER BY StartTime;
        """
        cursor.execute(query)
        rows = cursor.fetchall()  # list[dict]

        return rows

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching showtimes: {e}",
        )
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
