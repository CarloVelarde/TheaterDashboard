from typing import List

from fastapi import APIRouter, HTTPException
from app.models import MovieRead
from app.db import get_connection

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

    try:
        conn = get_connection()
        # dictionary=True so we get dicts instead of tuples
        cursor = conn.cursor(dictionary=True)

        query = """
         SELECT
               MovieID   AS movie_id,
               Title     AS title,
               Genre     AS genre,
               Runtime   AS runtime,
               ReleaseDate AS release_date,
               Price     AS price,
               IsActive  AS is_active,
               DistributorID AS distributor_id
         FROM Movies
         ORDER BY Title
      """
        cursor.execute(query)
        rows = cursor.fetchall()

        # Clean up DB resources
        cursor.close()
        conn.close()

        # Map rows to Pydantic models
        movies: List[MovieRead] = []
        for row in rows:
            movies.append(
                MovieRead(
                    movie_id=row["movie_id"],
                    title=row["title"],
                    genre=row["genre"],
                    runtime=row["runtime"],
                    release_date=row["release_date"],
                    price=float(row["price"]),
                    # IsActive is stored as TINYINT(1) (either 0 or 1) so we convert to bool for clarity
                    is_active=bool(row["is_active"]),
                    distributor_id=row["distributor_id"],
                )
            )

        return movies

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


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
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
               SELECT
                  MovieID  AS movie_id,
                  Title    AS title,
                  Genre  AS genre,
                  Runtime  AS runtime,
                  ReleaseDate AS release_date,
                  Price   AS price,
                  IsActive AS is_active,
                  DistributorID AS distributor_id
               FROM MOVIES
               WHERE IsActive = 1
               ORDER BY Title
               """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # Map rows to Pydantic models
        movies: List[MovieRead] = []
        for row in rows:
            movies.append(
                MovieRead(
                    movie_id=row["movie_id"],
                    title=row["title"],
                    genre=row["genre"],
                    runtime=row["runtime"],
                    release_date=row["release_date"],
                    price=float(row["price"]),
                    # IsActive is stored as TINYINT(1) (either 0 or 1) so we convert to bool for clarity
                    is_active=bool(row["is_active"]),
                    distributor_id=row["distributor_id"],
                )
            )
        return movies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


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
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
               SELECT
                  MovieID   AS movie_id,
                  Title    AS title,
                  Genre     AS genre,
                  Runtime    AS runtime,
                  ReleaseDate  AS release_date,
                  Price   AS price,
                  IsActive   AS is_active,
                  DistributorID AS distributor_id
               FROM Movies
               WHERE ReleaseDate > CURDATE()
               ORDER BY ReleaseDate ASC
      """

        cursor.execute(query)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return [
            MovieRead(
                movie_id=row["movie_id"],
                title=row["title"],
                genre=row["genre"],
                runtime=row["runtime"],
                release_date=row["release_date"],
                price=float(row["price"]),
                is_active=bool(row["is_active"]),
                distributor_id=row["distributor_id"],
            )
            for row in rows
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
