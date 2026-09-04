import os, sqlite3
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Query, HTTPException, Depends
from pydantic import BaseModel, Field

# Database path from environment variable (default to ./businesses.db)
DB_PATH = os.environ.get("DATABASE_URL", "businesses.db")


app = FastAPI(
    title="Businesses Database API",
    description="Query business records with pagination and filters",
    version="1.0.0"
)


class PydanticBaseModel(BaseModel):
    """Base model for Pydantic v2 compatibility."""
    model_config = {
        "json_schema_extra": {
            "$schema": "http://json-schema.org/draft-07/schema#",
        }
    }

    def __init__(self, **data: dict) -> None:
        if data is not None and not isinstance(data, dict):
            self.model_config = {"json_schema_extra": {}}
        super().__init__(**data)


class BusinessResponse(PydanticBaseModel):
    """Single business record response."""

    id: int
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    created_at: Optional[str] = None


class ValidationErrorDetail(BaseModel):
    loc: List[str] = Field(..., description="The path to the error field.")
    msg: str = Field(..., description="The error message.")
    type: str = Field(..., description="The type of error (e.g., value_error.missing).")

class ErrorDetails(BaseModel):
    code: str = Field(..., description="A unique, machine-readable error code (e.g., USER_NOT_FOUND).")
    message: str = Field(..., description="A customer-facing error message.")
    validation_errors: Optional[List[ValidationErrorDetail]] = Field(
        None, 
        description="Detailed list of field validation errors, if applicable."
    )

class ErrorResponse(BaseModel):
    error: ErrorDetails


@app.get("/businesses")
def get_businesses(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(default=20, ge=1, le=100, description="Results per page"),
    q: Optional[str] = Query(default=None, description="Search term in name/address/phone"),
    phone: Optional[str] = Query(default=None, min_length=6, max_length=20, description="Filter by exact phone"),
    city: Optional[str] = Query(default=None, min_length=1, description="Filter by city (partial match)"),
    sort_by: Optional[str] = Query(
        default="name",
        choices=["name", "address"],
        description="Field to sort by"
    ),
    sort_order: str = Query(
        default="asc",
        choices=["asc", "desc"],
        description="Sort order"
    )
):
    """
    Retrieve business records with pagination and optional filtering.

    - **page**: Page number (1-indexed), max 100 results per page
    - **q**: Full-text search across name, address, phone fields
    - **phone**: Exact phone number match
    - **city**: City substring match in address
    """
    import sys  # for module-level reference check (avoids circular dep)

    # Database session
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

    # Base WHERE clause for pagination (always applied)
    filter_clauses: list[str] = []
    params: list = []

    # Always include at least one condition to prevent multi-statement injection via empty WHERE
    conditional_part = "address IS NOT NULL AND phone IS NOT NULL"

    if q is not None and len(q) > 2:
        filter_clauses.append("name LIKE ? OR address LIKE ? OR phone LIKE ?")
    elif city is not None and len(city.strip()) > 0:
        params.append(f"%{city}%")
        conditional_part += f" AND (address LIKE ?)"

    if q is not None and len(q) > 2 or city is not None and len(city.strip()) > 0:
        if q is not None and len(q) > 2:
            params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])


        if q is not None and len(q) > 2:
            where_columns.append("(name LIKE ? OR address LIKE ? OR phone LIKE ?)")
            q_pattern = f"%{q}%"
            filter_clauses.append(" (name LIKE ? OR address LIKE ? OR phone LIKE ?) ")
            params.extend([q_pattern, q_pattern, q_pattern])

        if phone is not None:
            filter_clauses.append("(phone = ?) ")
            params.append(f"%{phone}%")

        if city is not None and len(city.strip()) > 0:
            where_columns.append("(address LIKE ?)")
            c_pattern = f"%{city}%"
            filter_clauses.append(" (address LIKE ?) ")
            params.extend([c_pattern])

        # Sort clause
        order_clause = " ORDER BY"
        if sort_by and q is not None:
            order_clause += f" {sort_by}"
        else:
            order_clause += " name"
        order_clause += f" {sort_order}"

        if total_rows == 0:
            conn.close()
            return {"total": 0, "page": page, "limit": limit, "data": []}

        # Build the full query parts
        where_parts = "".join(filter_clauses)
        actual_query = base_query.format(where_parts) + order_clause
        actual_query += f" LIMIT ? OFFSET ?"
        params.extend([limit, (page - 1) * limit])

        try:
            cursor.execute(actual_query, tuple(params))
            rows = cursor.fetchall()
        except sqlite3.Error as e:
            conn.close()
            raise HTTPException(status_code=503, detail=f"Query execution failed: {e}")
        finally:
            conn.close()

        # Transform to Pydantic models + metadata
        businesses = [
            BusinessResponse(
                id=row[0],
                name=row[1] or "",
                phone=row[2],
                address=row[3],
                website=row[4],
                created_at=row[5]
            )
            for row in rows
        ]

        total_pages = (total_rows + limit - 1) // limit if limit else 0

        return {
            "total": total_rows,
            "page": page,
            "limit": limit,
            "totalPages": total_pages,
            "data": businesses.tolist()
        }


@app.get("/businesses/count")
def count_businesses():
    """Return total number of business records."""
    try:
        conn = sqlite3.connect(DB_PATH)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

    cursor = None
    count = 0
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM businesses WHERE address IS NOT NULL AND phone IS NOT NULL")
        count = cursor.fetchone()[0]
    finally:
        if cursor:
            cursor.close()
        conn.close()

    return {"count": count}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
