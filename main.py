import uvicorn
from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError

from utils.exceptions import BaseAppException
from utils.error_handlers import (
    app_exception_handler,
    sqlalchemy_exception_handler,
    unhandled_exception_handler
)

app = FastAPI(
    title="FastAPI Auth Service",
    description="Authentication and Authorization Service",
    version="1.0.0"
)

# Register exception handlers
app.add_exception_handler(BaseAppException, app_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

def main():
    uvicorn.run(
        app="app.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()