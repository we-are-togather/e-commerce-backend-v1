from fastapi import FastAPI

import app.models
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.core.database import engine

from app.core.exception_handlers import register_exception_handlers
from app.middleware.middleware import register_middleware

app = FastAPI(title=settings.app_name)
register_exception_handlers(app)
# Base.metadata.create_all(bind=engine)
app.include_router(api_router, prefix="/api/v1")
register_middleware(app)