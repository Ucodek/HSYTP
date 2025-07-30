# API Component Documentation

This document provides a comprehensive overview of the API component in the backend_v2 application.

## Overview

The API component provides a structured approach to building REST APIs with standardized:
- Pagination
- Sorting
- Filtering
- Query parameter handling
- Consistent response formatting

## Directory Structure

```
app/api/
├── common/                  # Common utilities for endpoints
│   ├── __init__.py          # Exports from all common modules
│   ├── filtering.py         # Filtering utilities
│   ├── pagination.py        # Pagination utilities
│   ├── query_params.py      # Combined query parameter handling
│   └── sorting.py           # Sorting utilities
├── v1/                      # API version 1
│   ├── __init__.py
│   └── router.py            # Main API router for v1
├── __init__.py              # API package exports
└── dependencies.py          # Common dependencies for API endpoints
```

## Core Components

### Pagination

Provides standardized pagination for API endpoints:

```python
# Example: Using pagination in a route
@router.get("/items")
async def list_items(
    pagination: PaginationParams = Depends(get_pagination_params),
    db: Session = Depends(get_db)
):
    query = db.query(Item)
    total = query.count()
    items = pagination.paginate_query(query).all()
    return PagedResponse.create(items, total, pagination)
```

Key components:
- `PaginationParams`: Handles pagination parameters (page, page_size)
- `PagedResponse`: Standardized response format for paginated data
- `get_pagination_params`: FastAPI dependency for pagination

### Sorting

Provides utilities for sorting query results:

```python
# Example: Using sorting in a route
@router.get("/items")
async def list_items(
    sorting: SortingParams = Depends(get_sorting_params),
    db: Session = Depends(get_db)
):
    query = db.query(Item)
    sorted_query = sorting.apply_to_query(
        query, 
        Item, 
        allowed_fields=["name", "created_at"]
    )
    return sorted_query.all()
```

Key components:
- `SortingParams`: Handles sorting parameters (sort, order)
- `apply_sorting`: Helper function for applying sorting
- `get_sorting_params`: FastAPI dependency for sorting

### Filtering

Provides utilities for filtering query results:

```python
# Example: Creating filter parameters
class UserFilterParams(FilterParams):
    name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None

# Example: Using filters in a route
@router.get("/users")
async def list_users(
    filters: UserFilterParams = Depends(),
    db: Session = Depends(get_db)
):
    query = db.query(User)
    filtered_query = apply_filters_from_params(query, User, filters)
    return filtered_query.all()
```

Key components:
- `FilterParams`: Base class for creating filter parameters
- `Filter`: Represents a single filter condition
- `FilterOperator`: Enum for filter operators (eq, ne, gt, etc.)
- `apply_filters_from_params`: Helper for applying filters from parameters

### Combined Query Parameters

Unifies filtering, sorting, and pagination:

```python
# Example: Creating and using QueryParams
UserQueryParams = create_query_params_dependency(UserFilterParams)

@router.get("/users")
async def list_users(
    query_params: QueryParams = Depends(UserQueryParams),
    db: Session = Depends(get_db)
):
    query = db.query(User)
    results, total = query_params.apply_all_params(
        query, 
        User,
        sort_allowed_fields=["name", "email", "created_at"],
        default_sort_field="created_at"
    )
    return PagedResponse.create(results, total, query_params.pagination)
```

Key component:
- `QueryParams`: Combines filtering, pagination, and sorting parameters
- `create_query_params_dependency`: Factory function for QueryParams dependencies

### Dependencies

Common FastAPI dependencies for API endpoints:

```python
# Example: Using dependencies in a route
@router.get("/me")
async def get_profile(
    current_user: CurrentActiveUser,
    db: DbSession,
    language: Language
):
    return {"user": current_user.safe_dict(), "language": language}
```

Key dependencies:
- `CurrentUser`, `CurrentActiveUser`, `CurrentAdminUser`: User authentication
- `OptionalUser`: Optional user authentication
- `DbSession`: Database session
- `Language`: Language preference
- `PaginationDep`, `SortingDep`: Pagination and sorting
- `CommonQueryParams`: Common query parameters
- `RequestId`: Request ID tracking

## Common Usage Patterns

### Basic CRUD Operation

```python
@router.get("/{id}")
async def get_item(
    id: int,
    db: DbSession,
    current_user: CurrentActiveUser
):
    item = get_item_by_id(db, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return create_success_response(item.model_dump())
```

### Paginated List

```python
@router.get("/")
async def list_items(
    pagination: PaginationParams = Depends(get_pagination_params),
    db: DbSession,
    current_user: CurrentActiveUser
):
    query = db.query(Item)
    total = query.count()
    items = pagination.paginate_query(query).all()
    return PagedResponse.create([item.model_dump() for item in items], total, pagination)
```

### Advanced List with Filtering and Sorting

```python
@router.get("/")
async def list_items(
    query_params: QueryParams = Depends(create_query_params_dependency(ItemFilterParams)),
    db: DbSession,
    current_user: CurrentActiveUser
):
    query = db.query(Item)
    results, total = query_params.apply_all_params(
        query,
        Item,
        sort_allowed_fields=["name", "created_at"],
        default_sort_field="created_at"
    )
    return PagedResponse.create([item.model_dump() for item in results], total, query_params.pagination)
```

## Best Practices

1. **Follow the Implementation Order:**
   - Basic CRUD operations first
   - Pagination second
   - Sorting third
   - Filtering last

2. **Serialization:**
   - Always call `model_dump()` or convert to dictionaries before returning responses
   - Example: `return create_success_response(item.model_dump())`

3. **Error Handling:**
   - Use appropriate HTTP status codes
   - Include descriptive error messages
   - Validate input parameters

4. **Documentation:**
   - Add docstrings to all functions
   - Include type hints
   - Document parameters and return values

5. **Dependency Injection:**
   - Use FastAPI's dependency system
   - Create type-safe dependencies using Annotated
   - Keep dependencies focused on one responsibility
