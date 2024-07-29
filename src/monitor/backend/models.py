from sqlmodel import SQLModel

# Obviously this codebase doesn't use a database, but SQLModel is essentially just a wrapper around
# Pydantic and SQLAlchemy, so if there was a _need_ to move to a database, we're most of the way 
# there already.

# It also interoperates quite nicely with FastAPI (same developer!)

class MessageResultRequest(SQLModel):
    message: str
    phone: str
    success: bool
    delay: float

class MessageStatistics(SQLModel):
    success_messages: int
    failed_messages: int
    average_delay: float

class ErrorResponse(SQLModel):
    message: str