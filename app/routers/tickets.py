import mysql.connector

from datetime import date
from typing import List

from fastapi import APIRouter, HTTPException, Path, Query
from app.models import (
    TicketSaleRead,
    TicketPurchaseRequest,
    TicketPurchaseResponse,
    CustomerTicketHistoryEntry,
)
from app.db import get_connection

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)


#  uses stored procedure & triggers
@router.post(
    "/purchase",
    response_model=TicketPurchaseResponse,
    summary="Purchase a ticket",
    description=(
        "Processes a ticket purchase for a given customer and showtime. "
        "This will call the stored procedure Process_Ticket_Purchase in MySQL, "
        "which may activate triggers to enforce business rules such as preventing "
        "overselling, buying for past showtimes, or buying during in progress showings."
    ),
)
def purchase_ticket(req: TicketPurchaseRequest):
    """
    Ticket purchase endpoint:

    - Input: customer_id and showtime_id in the request body.
    - Output: a status flag and human-readable message.

    Implementation notes:
    - Calls: CALL Process_Ticket_Purchase(p_CustomerID, p_ShowtimeID).
    - On success: COMMIT and return success status/message.
    - On error: ROLLBACK and surface DB error message to the client.
    """
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Call stored procedure defined in SQL:
        # CREATE PROCEDURE Process_Ticket_Purchase(IN p_CustomerID INT, IN p_ShowtimeID INT) ...
        cursor.callproc(
            "Process_Ticket_Purchase",
            [req.customer_id, req.showtime_id],
        )

        # If we reach here, the procedure completed without SIGNAL / errors
        conn.commit()

        return TicketPurchaseResponse(
            status="success",
            message="Ticket purchased successfully.",
        )
    except mysql.connector.Error as e:
        # Errors raised with SIGNAL inside the procedure/triggers will show up here
        if conn:
            conn.rollback()

        # e.msg will usually contain the MESSAGE_TEXT you set in SIGNAL.
        detail_msg = getattr(e, "msg", str(e)) or str(e)

        # 400 = client error (bad request) since its usually a rule violation (theater specific)
        raise HTTPException(
            status_code=400,
            detail=f"Ticket purchase failed: {detail_msg}",
        )
    except Exception as e:
        if conn:
            conn.rollback()
        # Unexpected server error
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during ticket purchase: {e}",
        )
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


@router.get(
    "/today",
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

    - Output: list of TicketSales where DATE(TimeTicketSold) = todays date.

    Implementation notes:
    - Uses CURDATE() on the MySQL side to match the current date.
    """
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
         SELECT
               TicketSaleID  AS ticket_sale_id,
               CustomerID   AS customer_id,
               ShowtimeID  AS showtime_id,
               TicketPrice   AS ticket_price,
               TimeTicketSold AS time_ticket_sold
         FROM TicketSales
         WHERE DATE(TimeTicketSold) = CURDATE()
         ORDER BY TimeTicketSold ASC
      """
        cursor.execute(query)
        rows = cursor.fetchall()

        return [
            TicketSaleRead(
                ticket_sale_id=row["ticket_sale_id"],
                customer_id=row["customer_id"],
                showtime_id=row["showtime_id"],
                ticket_price=float(row["ticket_price"]),
                time_ticket_sold=row["time_ticket_sold"],
            )
            for row in rows
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while fetching todays ticket sales: {e}",
        )
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


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
    - JOIN TicketSales ts
      JOIN Showtimes s ON ts.ShowtimeID = s.ShowtimeID
      JOIN Movies    m ON s.MovieID    = m.MovieID
    - Filter WHERE ts.CustomerID = :customer_id.
    """
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                ts.TicketSaleID   AS ticket_sale_id,
                m.Title      AS movie_title,
                ts.ShowtimeID   AS showtime_id,
                s.TheaterID    AS theater_id,
                s.StartTime    AS start_time,
                ts.TicketPrice  AS ticket_price,
                ts.TimeTicketSold AS time_ticket_sold
            FROM TicketSales ts
            JOIN Showtimes s ON ts.ShowtimeID = s.ShowtimeID
            JOIN Movies    m ON s.MovieID    = m.MovieID
            WHERE ts.CustomerID = %s
            ORDER BY ts.TimeTicketSold DESC
        """
        cursor.execute(query, (customer_id,))
        rows = cursor.fetchall()

        return [
            CustomerTicketHistoryEntry(
                ticket_sale_id=row["ticket_sale_id"],
                movie_title=row["movie_title"],
                showtime_id=row["showtime_id"],
                theater_id=row["theater_id"],
                start_time=row["start_time"],
                ticket_price=float(row["ticket_price"]),
                time_ticket_sold=row["time_ticket_sold"],
            )
            for row in rows
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while fetching ticket history: {e}",
        )
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


@router.get(
    "",
    response_model=List[TicketSaleRead],
    summary="List all ticket sales",
    description=(
        "Returns every ticket sale in the system. "
        "Useful as a general admin/debugging endpoint."
    ),
)
def list_all_tickets():
    """
    General endpoint:

    - Output: list of all TicketSales records in the database.

    Implementation notes:
    - Simple SELECT from TicketSales, ordered by TimeTicketSold, most recent first
    """
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                TicketSaleID AS ticket_sale_id,
                CustomerID   AS customer_id,
                ShowtimeID   AS showtime_id,
                TicketPrice  AS ticket_price,
                TimeTicketSold AS time_ticket_sold
            FROM TicketSales
            ORDER BY TimeTicketSold DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        return [
            TicketSaleRead(
                ticket_sale_id=row["ticket_sale_id"],
                customer_id=row["customer_id"],
                showtime_id=row["showtime_id"],
                ticket_price=float(row["ticket_price"]),
                time_ticket_sold=row["time_ticket_sold"],
            )
            for row in rows
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while fetching all ticket sales: {e}",
        )
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
