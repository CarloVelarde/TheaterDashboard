from typing import List

from fastapi import APIRouter, HTTPException
from app.models import MovieRead

router = APIRouter(
    prefix="/movies",
    tags=["movies"],
)


@router.get(
    "",
    response_model=List[MovieRead],
    summary="List all movies",
    description="Returns all movies in the database, regardless of status.",
)
def list_movies():
    """
    General endpoint:

    - Output: list of all movies (active, inactive, upcoming).
    - Implementation will SELECT from Movies table.
    """
    # TODO: implement database logic
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get(
    "/now-playing",
    response_model=List[MovieRead],
    summary="Get all movies currently playing",
    description=(
        "Returns all movies that are currently active (IsActive = 1). "
        "These represent movies that can currently be shown in the theater."
    ),
)
def get_now_playing_movies():
    """
    General endpoint:

    - Output: movies with IsActive = 1.
    - Implementation will filter Movies on IsActive flag.
    """
    # TODO: implement database logic
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get(
    "/upcoming",
    response_model=List[MovieRead],
    summary="Get all upcoming movies",
    description=(
        "Returns all movies whose ReleaseDate is in the future. "
        "These represent movies that will be available to show soon."
    ),
)
def get_upcoming_movies():
    """
    General endpoint:

    - Output: movies with ReleaseDate > current date.
    - Implementation will compare ReleaseDate with CURDATE()/NOW().
    """
    # TODO: implement database logic
    raise HTTPException(status_code=501, detail="Not implemented yet")
