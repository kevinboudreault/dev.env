import os
import sqlite3
from enum import Enum
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Query, HTTPException

# Pydantic v2 syntax
from pydantic import BaseModel, Field

# Database path from environment variable
DB_PATH = os.environ.get("DATABASE_URL", "businesses.db")

app = FastAPI(
    title="Businesses Database API",
    description="Query business records with pagination and filters",
    version="1.0.0"
)

# --- ENUMS FOR VALIDATION ---
class SortByOptions(str, Enum):
    name = "name"
    address = "address"

class SortOrderOptions(str, Enum):
    asc = "asc"
    desc = "desc"

# --- PYDANTIC SCHEMAS ---
class BusinessResponse(BaseModel):
    """Single business record response."""
    id: int
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    created_at: Optional[str] = None

class PaginatedBusinessResponse(BaseModel):
    """Structured paginated list wrap."""
    total: int
    page: int
    limit: int
    totalPages: int
    data: List[BusinessResponse]

class ValidationErrorDetail(BaseModel):
    loc: List[str] = Field(..., description="The path to the error field.")
    msg: str = Field(..., description="The error message.")
    type: str = Field(..., description="The type of error.")

class ErrorDetails(BaseModel):
    code: str = Field(..., description="A unique, machine-readable error code.")
    message: str = Field(..., description="A customer-facing error message.")
    validation_errors: Optional[List[ValidationErrorDetail]] = None

class ErrorResponse(BaseModel):
    error: ErrorDetails


# --- DATABASE DEPENDENCY ---
def get_db_cursor():
    """Context-managed database connection helper."""
    conn = sqlite3.connect(DB_PATH)
    # Allows fetching rows as dictionaries instead of tuples
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        cursor.close()
        conn.close()


# --- ENDPOINTS ---
@app.get("/businesses", response_model=PaginatedBusinessResponse)
def get_businesses(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(default=20, ge=1, le=100, description="Results per page"),
    q: Optional[str] = Query(default=None, description="Search term in name/address/phone"),
    phone: Optional[str] = Query(default=None, min_length=6, max_length=20, description="Filter by exact phone"),
    city: Optional[str] = Query(default=None, min_length=1, description="Filter by city (partial match)"),
    sort_by: SortByOptions = Query(default=SortByOptions.name, description="Field to sort by"),
    sort_order: SortOrderOptions = Query(default=SortOrderOptions.asc, description="Sort order")
):
    """Retrieve business records with dynamic SQL filtering and pagination."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

    try:
        # 1. Build Dynamic Filter Clauses safely
        # Enforce base business constraints if necessary, or default to 1=1
        filter_clauses = ["address IS NOT NULL", "phone IS NOT NULL"]
        params = []

        if q and len(q.strip()) > 2:
            filter_clauses.append("(name LIKE ? OR address LIKE ? OR phone LIKE ?)")
            q_pattern = f"%{q.strip()}%"
            params.extend([q_pattern, q_pattern, q_pattern])

        if phone:
            filter_clauses.append("phone = ?")
            params.append(phone.strip())

        if city and len(city.strip()) > 0:
            filter_clauses.append("address LIKE ?")
            params.append(f"%{city.strip()}%")

        where_stmt = " WHERE " + " AND ".join(filter_clauses)

        # 2. Get Total Count for Pagination metadata
        count_query = f"SELECT COUNT(*) FROM businesses {where_stmt}"
        cursor.execute(count_query, tuple(params))
        total_rows = cursor.fetchone()[0]

        if total_rows == 0:
            return {"total": 0, "page": page, "limit": limit, "totalPages": 0, "data": []}

        # 3. Fetch Paginated Records
        # Safe interpolation because sort_by and sort_order are restricted via Enums
        order_stmt = f" ORDER BY {sort_by.value} {sort_order.value}"
        limit_stmt = f" LIMIT ? OFFSET ?"
        
        data_query = f"SELECT id, name, phone, address, website, created_at FROM businesses {where_stmt} {order_stmt} {limit_stmt}"
        
        # Add limit and offset params
        offset = (page - 1) * limit
        extended_params = params + [limit, offset]

        cursor.execute(data_query, tuple(extended_params))
        rows = cursor.fetchall()

        # 4. Format Output Map matching Pydantic response models
        businesses = [
            BusinessResponse(
                id=row["id"],
                name=row["name"] or "",
                phone=row["phone"],
                address=row["address"],
                website=row["website"],
                created_at=row["created_at"]
            )
            for row in rows
        ]

        total_pages = (total_rows + limit - 1) // limit

        return {
            "total": total_rows,
            "page": page,
            "limit": limit,
            "totalPages": total_pages,
            "data": businesses
        }

    except sqlite3.Error as e:
        raise HTTPException(status_code=503, detail=f"Query execution failed: {e}")
    finally:
        cursor.close()
        conn.close()


@app.get("/businesses/count")
def count_businesses():
    """Return total number of active business records."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM businesses WHERE address IS NOT NULL AND phone IS NOT NULL")
        count = cursor.fetchone()[0]
        return {"count": count}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database operational error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
