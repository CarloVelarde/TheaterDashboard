from datetime import datetime, date
from pydantic import BaseModel, Field


class MovieRead(BaseModel):
    """Basic movie information used in general endpoints."""

    movie_id: int = Field(..., example=1)
    title: str = Field(..., example="Minecraft")
    genre: str = Field(..., example="Adventure")
    runtime: int = Field(..., example=120, description="Runtime in minutes")
    release_date: date = Field(..., example="2025-10-28")
    price: float = Field(..., example=250.00, description="Cost to theater per showing")
    is_active: bool = Field(..., example=True)


class ShowtimeRead(BaseModel):
    """Basic showtime information."""

    showtime_id: int = Field(..., example=1)
    movie_id: int = Field(..., example=1)
    theater_id: int = Field(..., example=3)
    start_time: datetime = Field(..., example="2025-11-05T18:00:00")
    end_time: datetime = Field(..., example="2025-11-05T20:12:00")


class CustomerRead(BaseModel):
    """Basic customer information."""

    customer_id: int = Field(..., example=1)
    fname: str = Field(..., example="Carlo")
    lname: str = Field(..., example="Velarde")
    membership_status: bool = Field(
        ...,
        example=True,
        description="True = Member, False = Non-member",
    )


class TicketSaleRead(BaseModel):
    """Basic ticket sale record."""

    ticket_sale_id: int = Field(..., example=1)
    customer_id: int = Field(..., example=1)
    showtime_id: int = Field(..., example=1)
    ticket_price: float = Field(..., example=15.00)
    time_ticket_sold: datetime = Field(..., example="2025-11-04T10:15:00")
