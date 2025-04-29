# Python and FastAPI Code Style Guide

This guide defines the code conventions to be followed in FastAPI projects to ensure consistency and facilitate maintenance.

## General Principles

- Follow Clean Code and SOLID principles
- Prioritize readability and maintainability
- Write self-explanatory code, avoiding unnecessary comments
- Use Type Hints in all functions and methods
- Document APIs with docstrings following the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) standard

## Code Formatting

- Use 4 spaces for indentation (not tabs)
- Limit lines to 120 characters
- Use [Ruff](https://github.com/charliermarsh/ruff) as the main tool for formatting and linting:
    - Configured to apply flake8 rules
    - Automatic import ordering (replacing isort)
    - Possibility of automatic fixes with `ruff --fix`
    - Type checking with mypy integration
    - Much faster than individual tools

## Import Organization

```python
# Standard libraries
import os
from datetime import datetime
from typing import List, Optional

# Third-party libraries
import fastapi
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# Local imports
from app.core import config
from app.db.session import get_db
from app.models import User
from app.schemas.user import UserCreate, UserResponse
```

## FastAPI API Structure

- Use routers to organize endpoints
- Separate endpoints into files by resource
- Define dependencies in `deps.py`
- Use Pydantic models for input and output validation
- Document endpoints with docstrings and OpenAPI parameters

```python
@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new user.
    
    Requires superuser privileges.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    return crud.user.create(db, obj_in=user_in)
```

## Models and Schemas

- Use SQLAlchemy for database models
- Use Pydantic for validation schemas
- Separate schemas into Request/Response
- Use inheritance for shared schemas

```python
# SQLAlchemy model
class User(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)

# Pydantic schemas
class UserBase(BaseModel):
    email: str
    is_active: Optional[bool] = True
    
class UserCreate(UserBase):
    password: str
    
class UserResponse(UserBase):
    id: int
    
    class Config:
        orm_mode = True
```

## CRUD Operations

- Use base classes for CRUD operations
- Implement specific operations in dedicated classes
- Organize in a `crud` module

## Error Handling

- Use HTTPException with appropriate status_code
- Provide clear and useful error messages
- Implement middleware for error logs

## Tests

- Write unit tests for all functions and methods
- Organize tests in the same structure as the code
- Use pytest fixtures to share resources
- Mock external dependencies
- Implement integration tests for endpoints
- Use pytest for tests
- Add type hints in all tests

```python
def test_create_user(client: Client, superuser_token_headers: Dict[dict, dict]) -> None:
    data = {
        "email": "test@example.com",
        "password": "testpassword",
        "is_active": True,
    }
    response = client.post(
        "/api/v1/users/", headers=superuser_token_headers, json=data
    )
    assert response.status_code == 201
    content = response.json()
    assert content["email"] == data["email"]
    assert "id" in content
```

## Logging

- Use Python's standard `logging` module
- Configure appropriate log levels for different environments
- Include relevant context in logs
- Do not log sensitive information

## Configuration

- Use environment variables for configuration
- Implement configuration validation via Pydantic
- Separate configuration by environment (dev, test, prod)

## Security

- Always validate user input with Pydantic
- Use OAuth2 with JWT for authentication
- Store only password hashes
- Define and verify permissions properly
- Implement rate limiting for public endpoints

## Useful Commands

```bash
# Formatting and lint
python -m ruff format .

# Type checking
python -m mypy .

# Tests
pytest -m auto

# Test coverage
pytest --cov=app
```

## Recommended VS Code Tools

- Python Extension
- Ruff Formatter
- mypy
- Pylance
- Python Test Explorer
- Git Lens
- Docker