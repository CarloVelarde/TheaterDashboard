from datetime import date
from typing import List

from fastapi import APIRouter, HTTPException, Path, Query
from app.models import (
    TicketSaleRead,
    TicketPurchaseRequest,
    TicketPurchaseResponse,
    CustomerTicketHistoryEntry,
)

router = APIRouter(
    prefix="",
    tags=["tickets"],
)


@router.post(
    "/tickets/purchase",
    response_model=TicketPurchaseResponse,
    summary="Purchase a ticket (uses stored procedure & triggers)",
    description=(
        "Processes a ticket purchase for a given customer and showtime. "
        "This will call the stored procedure Process_Ticket_Purchase in MySQL, "
        "which may activate triggers to enforce business rules such as preventing "
        "overselling, buying for past showtimes, or buying during in-progress showings."
    ),
)
def purchase_ticket(req: TicketPurchaseRequest):
    """
    Ticket purchase endpoint:

    - Input: customer_id and showtime_id in the request body.
    - Output: a status flag and human-readable message.

    Implementation notes:
    - Will call: CALL Process_Ticket_Purchase(p_CustomerID, p_ShowtimeID).
    - On success: COMMIT and return success status/message.
    - On error: ROLLBACK and surface DB error message to the client.
    """
    # TODO: implement database logic (call stored procedure)
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get(
    "/tickets/today",
    response_model=List[TicketSaleRead],
    summary="Get all tickets sold today",
    description=(
        "Returns all ticket sales that occurred on the current date. "
        "Useful for viewing daily ticket activity."
    ),
)
def get_tickets_sold_today():
    """
    General endpoint:

    - Output: list of TicketSales where DATE(TimeTicketSold) = today's date.

    Implementation notes:
    - Will SELECT from TicketSales filtered by today's date.
    - Optionally may join with Showtimes/Movies for more context.
    """
    # TODO: implement database logic
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get(
    "/customers/{customer_id}/tickets",
    response_model=List[CustomerTicketHistoryEntry],
    summary="Get all tickets purchased by a given customer",
    description=(
        "Returns a ticket history for a specific customer, including movie titles, "
        "showtime information, and ticket sale details."
    ),
)
def get_customer_ticket_history(
    customer_id: int = Path(
        ..., description="ID of the customer whose ticket history to fetch"
    ),
):
    """
    General endpoint:

    - Input: CustomerID.
    - Output: list of ticket purchases with movie and showtime details.

    Implementation notes:
    - Will JOIN TicketSales, Showtimes, and Movies on appropriate keys.
    - Filter on TicketSales.CustomerID = :customer_id.
    """
    # TODO: implement database logic
    raise HTTPException(status_code=501, detail="Not implemented yet")
