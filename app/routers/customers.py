from typing import List

from fastapi import APIRouter, HTTPException

from app.db import get_connection
from app.models import CustomerRead

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
)


@router.get(
    "",
    response_model=List[CustomerRead],
    summary="List all customers",
    description=(
        "Returns all customers in the system. "
        "Useful for populating dropdowns when selecting a customer "
        "for ticket purchase or viewing ticket history."
    ),
)
def list_customers():
    """
    General endpoint:

    - Output: list of all customers with their IDs, names, and membership status.

    Implementation notes:
    - Simple SELECT from Customers table.
    """
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                CustomerID AS customer_id,
                FName      AS fname,
                LName      AS lname,
                MembershipStatus AS membership_status
            FROM Customers
            ORDER BY CustomerID;
        """
        cursor.execute(query)
        rows = cursor.fetchall()  # list[dict]

        # Pydantic will validate/convert MembershipStatus (0/1) -> bool.
        return rows

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching customers: {e}",
        )
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
