from datetime import date
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Path

from app.db import get_connection
from app.models import (
    MovieShowtime,
    ShowtimeAvailability,
    ConcessionCategoryRevenue,
    MovieLifetimeSales,
    UpcomingShowtime,
    DailyTicketSales,
    MovieProfit,
)

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)


@router.get(
    "/movie-showtimes",
    response_model=List[MovieShowtime],
    summary="Query 1: Showtimes for a movie on a given date",
    description=(
        "Given a movie title and a date, returns all showtimes for that movie on that date. "
        "This query demonstrates join usage between Movies and Showtimes."
    ),
)
def get_movie_showtimes(
    title: str = Query(..., description="Exact movie title, e.g., 'Minecraft'"),
    show_date: date = Query(
        ..., alias="date", description="Date (YYYY-MM-DD) for which to find showtimes"
    ),
):
    """
    Assignment Query 1:

    - Input: movie title and specific date.
    - Output: list of showtimes (theater, start time, end time) for that movie on that date.
    """
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                m.Title   AS title,
                s.ShowtimeID AS showtime_id,
                s.TheaterID  AS theater_id,
                s.StartTime  AS start_time,
                s.EndTime    AS end_time
            FROM Showtimes s
            JOIN Movies m ON s.MovieID = m.MovieID
            WHERE m.Title = %s
              AND DATE(s.StartTime) = %s
            ORDER BY s.StartTime
        """
        cursor.execute(query, (title, show_date))
        rows = cursor.fetchall()

        return [
            MovieShowtime(
                title=row["title"],
                showtime_id=row["showtime_id"],
                theater_id=row["theater_id"],
                start_time=row["start_time"],
                end_time=row["end_time"],
            )
            for row in rows
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while fetching movie showtimes: {e}",
        )
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


@router.get(
    "/showtime-availability",
    response_model=ShowtimeAvailability,
    summary="Query 2: Remaining seats for a showtime",
    description=(
        "Given a showtime ID, returns the auditorium capacity, tickets sold, "
        "and seats remaining. Demonstrates join and aggregation."
    ),
)
def get_showtime_availability(
    showtime_id: int = Query(..., description="ID of the showtime to check"),
):
    """
    Assignment Query 2:

    - Input: ShowtimeID.
    - Output: capacity, tickets sold, seats remaining.
    """
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                s.ShowtimeID                      AS showtime_id,
                a.SeatCapacity                    AS seat_capacity,
                COUNT(t.TicketSaleID)             AS tickets_sold,
                (a.SeatCapacity - COUNT(t.TicketSaleID)) AS seats_remaining
            FROM Showtimes s
            JOIN Auditoriums a ON s.TheaterID = a.TheaterID
            LEFT JOIN TicketSales t ON s.ShowtimeID = t.ShowtimeID
            WHERE s.ShowtimeID = %s
            GROUP BY s.ShowtimeID, a.SeatCapacity
        """
        cursor.execute(query, (showtime_id,))
        row = cursor.fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Showtime with ID {showtime_id} not found.",
            )

        return ShowtimeAvailability(
            showtime_id=row["showtime_id"],
            seat_capacity=row["seat_capacity"],
            tickets_sold=row["tickets_sold"],
            seats_remaining=row["seats_remaining"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while fetching showtime availability: {e}",
        )
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


@router.get(
    "/concessions/top-categories",
    response_model=List[ConcessionCategoryRevenue],
    summary="Query 3: Total revenue per concession category",
    description=(
        "Displays the total revenue for each concession category (e.g., Popcorn, Beverage), "
        "optionally limited to the top N. Demonstrates join and aggregation."
    ),
)
def get_concession_category_revenue(
    limit: Optional[int] = Query(
        None,
        description="Optional limit (e.g., top 3). If omitted, returns all categories.",
    )
):
    """
    Assignment Query 3:

    - Input: optional limit on number of categories.
    - Output: concession categories with their total revenue.
    """
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        base_query = """
            SELECT
                c.Category  AS category,
                SUM(c.ConcessionPrice) AS total_revenue
            FROM ConcessionSales cs
            JOIN Concessions c ON cs.ConcessionID = c.ConcessionID
            GROUP BY c.Category
            ORDER BY total_revenue DESC
        """

        if limit is not None:
            query = base_query + " LIMIT %s"
            params = (limit,)
        else:
            query = base_query
            params = ()

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [
            ConcessionCategoryRevenue(
                category=row["category"],
                total_revenue=float(row["total_revenue"]),
            )
            for row in rows
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while fetching concession revenue: {e}",
        )
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


@router.get(
    "/movie-lifetime-sales",
    response_model=MovieLifetimeSales,
    summary="Query 4: Lifetime ticket sales for a movie",
    description=(
        "Given a MovieID, returns the lifetime number of ticket sales for that movie. "
        "Demonstrates usage of a subquery along with joins."
    ),
)
def get_movie_lifetime_sales(
    movie_id: int = Query(
        ..., description="MovieID to look up lifetime ticket sales for"
    ),
):
    """
    Assignment Query 4:

    - Input: MovieID.
    - Output: movie title and total number of tickets ever sold for that movie.
    """
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Using a subquery for the COUNT
        query = """
            SELECT
                m.MovieID AS movie_id,
                m.Title   AS title,
                (
                    SELECT COUNT(*)
                    FROM TicketSales ts
                    JOIN Showtimes s ON ts.ShowtimeID = s.ShowtimeID
                    WHERE s.MovieID = m.MovieID
                ) AS lifetime_ticket_sales
            FROM Movies m
            WHERE m.MovieID = %s
        """
        cursor.execute(query, (movie_id,))
        row = cursor.fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Movie with ID {movie_id} not found.",
            )

        return MovieLifetimeSales(
            movie_id=row["movie_id"],
            title=row["title"],
            lifetime_ticket_sales=row["lifetime_ticket_sales"] or 0,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while fetching movie lifetime sales: {e}",
        )
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


@router.get(
    "/upcoming-showtimes",
    response_model=List[UpcomingShowtime],
    summary="Query 5: Upcoming showtimes (using view)",
    description=(
        "Returns upcoming showtimes with dynamic status (Scheduled, In Progress, Completed, "
        "Sold Out) using the UpcomingShowtimesView. Demonstrates use of a SQL view."
    ),
)
def get_upcoming_showtimes(
    days_ahead: Optional[int] = Query(
        None,
        description=(
            "Optional number of days ahead to restrict upcoming showtimes. "
            "If omitted, returns all future showtimes from now onward."
        ),
    )
):
    """
    Assignment Query 5:

    - Input: optional days_ahead filter.
    - Output: upcoming showtimes with movie title, auditorium, and dynamic status.
    """
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        base_query = """
            SELECT
                ShowtimeID    AS showtime_id,
                MovieID       AS movie_id,
                MovieTitle    AS movie_title,
                TheaterID     AS theater_id,
                StartTime     AS start_time,
                EndTime       AS end_time,
                IsSoldOut     AS is_sold_out,
                DynamicStatus AS dynamic_status
            FROM UpcomingShowtimesView
        """

        params = ()
        if days_ahead is not None:
            # View already filters out past showtimes- simply cap them by days_ahead
            base_query += " WHERE StartTime <= DATE_ADD(NOW(), INTERVAL %s DAY)"
            params = (days_ahead,)

        base_query += " ORDER BY StartTime"

        cursor.execute(base_query, params)
        rows = cursor.fetchall()

        return [
            UpcomingShowtime(
                showtime_id=row["showtime_id"],
                movie_id=row["movie_id"],
                movie_title=row["movie_title"],
                theater_id=row["theater_id"],
                start_time=row["start_time"],
                end_time=row["end_time"],
                is_sold_out=bool(row["is_sold_out"]),
                dynamic_status=row["dynamic_status"],
            )
            for row in rows
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while fetching upcoming showtimes: {e}",
        )
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


# ---------- Optional / function based reports ----------


@router.get(
    "/daily-ticket-sales",
    response_model=DailyTicketSales,
    summary="(Optional) Daily ticket sales using get_number_of_ticket_sales",
    description=(
        "Given a date, returns the total number of ticket sales for that date, "
        "using the get_number_of_ticket_sales(p_Date) function."
    ),
)
def get_daily_ticket_sales(
    target_date: date = Query(
        ..., alias="date", description="Date (YYYY-MM-DD) to count ticket sales for"
    ),
):
    """
    Optional report:

    - Input: date.
    - Output: number of ticket sales on that date.
    """
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT get_number_of_ticket_sales(%s) AS tickets_sold"
        cursor.execute(query, (target_date,))
        row = cursor.fetchone()

        tickets_sold = (
            row["tickets_sold"] if row and row["tickets_sold"] is not None else 0
        )

        return DailyTicketSales(
            report_date=target_date,
            tickets_sold=tickets_sold,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while fetching daily ticket sales: {e}",
        )
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


@router.get(
    "/movies/{movie_id}/profit",
    response_model=MovieProfit,
    summary="(Optional) Movie profit using get_movie_profits",
    description=(
        "Given a MovieID, returns the net profit for that movie using the "
        "get_movie_profits(p_MovieID) function (ticket revenue minus distributor fee)."
    ),
)
def get_movie_profit(
    movie_id: int = Path(..., description="MovieID to compute profit for"),
):
    """
    Optional report:

    - Input: MovieID.
    - Output: net profit for that movie and its title.
    """
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                m.Title                    AS title,
                get_movie_profits(%s)      AS net_profit
            FROM Movies m
            WHERE m.MovieID = %s
        """
        cursor.execute(query, (movie_id, movie_id))
        row = cursor.fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Movie with ID {movie_id} not found.",
            )

        return MovieProfit(
            movie_id=movie_id,
            title=row["title"],
            net_profit=float(row["net_profit"] or 0.0),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while fetching movie profit: {e}",
        )
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
