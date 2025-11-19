from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


# ---------- Generic message / status ----------


class MessageResponse(BaseModel):
    """Generic status + message response."""

    status: str = Field(..., example="success")
    message: str = Field(..., example="Ticket purchased successfully")


# ---------- Query movie showtimes for a date ----------


class MovieShowtime(BaseModel):
    """
    Represents a single showtime entry for a given movie on a given date.
    Used in: /api/reports/movie-showtimes
    """

    title: str = Field(..., example="Minecraft")
    showtime_id: int = Field(..., example=1)
    theater_id: int = Field(..., example=3)
    start_time: datetime = Field(..., example="2025-11-05T18:00:00")
    end_time: datetime = Field(..., example="2025-11-05T20:12:00")


# ---------- Query showtime availability ----------


class ShowtimeAvailability(BaseModel):
    """
    Capacity and remaining seats for a showtime.
    Used in: /api/reports/showtime-availability
    """

    showtime_id: int = Field(..., example=1)
    seat_capacity: int = Field(..., example=120)
    tickets_sold: int = Field(..., example=85)
    seats_remaining: int = Field(..., example=35)


# ---------- Query concession category revenue ----------


class ConcessionCategoryRevenue(BaseModel):
    """
    Total revenue aggregated by concession category.
    Used in: /api/reports/concessions/top-categories
    """

    category: str = Field(..., example="Popcorn")
    total_revenue: float = Field(..., example=1234.50)


# ---------- Query lifetime ticket sales for movie ----------


class MovieLifetimeSales(BaseModel):
    """
    Lifetime ticket sales for a movie.
    Used in: /api/reports/movie-lifetime-sales
    """

    movie_id: int = Field(..., example=2)
    title: str = Field(..., example="Tron")
    lifetime_ticket_sales: int = Field(..., example=250)


# ---------- Query upcoming showtimes from view ----------


class UpcomingShowtime(BaseModel):
    """
    Upcoming showtime entry from UpcomingShowtimesView.
    Used in: /api/reports/upcoming-showtimes
    """

    showtime_id: int = Field(..., example=5)
    movie_id: int = Field(..., example=1)
    movie_title: str = Field(..., example="Minecraft")
    theater_id: int = Field(..., example=1)
    start_time: datetime = Field(..., example="2025-11-06T15:15:00")
    end_time: datetime = Field(..., example="2025-11-06T17:27:00")
    is_sold_out: bool = Field(..., example=False)
    dynamic_status: str = Field(..., example="Scheduled")


# ---------- Operation: ticket purchase (procedure) ----------


class TicketPurchaseRequest(BaseModel):
    """Request body for purchasing a ticket."""

    customer_id: int = Field(..., example=1)
    showtime_id: int = Field(..., example=5)


class TicketPurchaseResponse(MessageResponse):
    """
    Response after attempting a ticket purchase.
    Inherits status and message; can be extended later.
    """

    pass


# ---------- Optional analytic: daily ticket sales (function) ----------


class DailyTicketSales(BaseModel):
    """Number of ticket sales for a given day."""

    report_date: date = Field(..., example="2025-11-05")
    tickets_sold: int = Field(..., example=42)


# ---------- Optional analytic: movie profit (function) ----------


class MovieProfit(BaseModel):
    """Net profit for a movie, using get_movie_profits(p_MovieID)."""

    movie_id: int = Field(..., example=2)
    title: str = Field(..., example="Tron")
    net_profit: float = Field(..., example=5432.10)


# ---------- General: customer ticket history (for /customers/{id}/tickets) ----------


class CustomerTicketHistoryEntry(BaseModel):
    """
    Represents a row in a customer's ticket history:
    combines ticket sale data with movie and showtime details.
    Used in: /api/customers/{customer_id}/tickets
    """

    ticket_sale_id: int = Field(..., example=1)
    movie_title: str = Field(..., example="Minecraft")
    showtime_id: int = Field(..., example=5)
    theater_id: int = Field(..., example=3)
    start_time: datetime = Field(..., example="2025-11-05T18:00:00")
    ticket_price: float = Field(..., example=15.00)
    time_ticket_sold: datetime = Field(..., example="2025-11-04T10:15:00")
