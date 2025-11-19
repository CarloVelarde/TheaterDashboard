from datetime import date
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Path
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
    show_date: date = Query(..., alias="date", description="Date (YYYY-MM-DD) for which to find showtimes"),
):
    """
    Assignment Query 1 (user/admin):

    - Input: movie title and specific date.
    - Output: list of showtimes (theater, start time, end time) for that movie on that date.

    Implementation notes:
    - JOIN Movies m ON Showtimes.MovieID = m.MovieID.
    - Filter by m.Title and DATE(Showtimes.StartTime) = :show_date.
    """
    # TODO: implement database logic (raw SQL)
    raise HTTPException(status_code=501, detail="Not implemented yet")


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
    Assignment Query 2 (user/admin/employee):

    - Input: ShowtimeID.
    - Output: capacity, tickets sold, seats remaining.

    Implementation notes:
    - JOIN Showtimes with Auditoriums to get SeatCapacity.
    - LEFT JOIN TicketSales to count tickets sold.
    - Compute SeatsRemaining = SeatCapacity - TicketsSold.
    """
    # TODO: implement database logic (raw SQL)
    raise HTTPException(status_code=501, detail="Not implemented yet")


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
    Assignment Query 3 (admin):

    - Input: optional limit on number of categories.
    - Output: concession categories with their total revenue.

    Implementation notes:
    - JOIN ConcessionSales with Concessions.
    - GROUP BY Category, SUM(ConcessionPrice).
    - ORDER BY TotalRevenue DESC, optionally LIMIT.
    """
    # TODO: implement database logic (raw SQL)
    raise HTTPException(status_code=501, detail="Not implemented yet")


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
    movie_id: int = Query(..., description="MovieID to look up lifetime ticket sales for"),
):
    """
    Assignment Query 4 (admin):

    - Input: MovieID.
    - Output: movie title and total number of tickets ever sold for that movie.

    Implementation notes:
    - SELECT from Movies by MovieID.
    - Subquery: COUNT(*) from TicketSales joined with Showtimes filtered by MovieID.
    """
    # TODO: implement database logic (raw SQL)
    raise HTTPException(status_code=501, detail="Not implemented yet")


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
    Assignment Query 5 (user/admin):

    - Input: optional days_ahead filter.
    - Output: upcoming showtimes with movie title, auditorium, and dynamic status.

    Implementation notes:
    - SELECT from UpcomingShowtimesView.
    - Optionally restrict StartTime <= NOW() + INTERVAL :days_ahead DAY.
    """
    # TODO: implement database logic (raw SQL)
    raise HTTPException(status_code=501, detail="Not implemented yet")


# ---------- Optional / function-based reports ----------

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
    target_date: date = Query(..., alias="date", description="Date (YYYY-MM-DD) to count ticket sales for"),
):
    """
    Optional report:

    - Input: date.
    - Output: number of ticket sales on that date.

    Implementation notes:
    - SELECT get_number_of_ticket_sales(:target_date) AS TicketsSold.
    """
    # TODO: implement database logic (raw SQL function call)
    raise HTTPException(status_code=501, detail="Not implemented yet")


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

    Implementation notes:
    - SELECT get_movie_profits(:movie_id) AS NetProfit.
    - Also SELECT movie title from Movies for display.
    """
    # TODO: implement database logic (raw SQL function call)
    raise HTTPException(status_code=501, detail="Not implemented yet")
