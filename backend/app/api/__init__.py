from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from app.api.documents import router as documents_router
from app.api.analysis import router as analysis_router
from app.api.handovers import router as handovers_router
from app.api.incoming import router as incoming_router
from app.api.activity import router as activity_router

__all__ = [
    "auth_router",
    "projects_router",
    "documents_router",
    "analysis_router",
    "handovers_router",
    "incoming_router",
    "activity_router"
]
