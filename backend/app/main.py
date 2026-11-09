import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models import User
from app.api import (
    auth_router,
    projects_router,
    documents_router,
    analysis_router,
    handovers_router,
    incoming_router,
    activity_router
)

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="KnowBridge Enterprise AI-Powered Project Knowledge Handover Platform API"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_system_accounts():
    """Seeds default enterprise accounts if not present."""
    db = SessionLocal()
    try:
        # 1. Project Lead
        lead_emails = ["lead@knowbridge.io", "lead@knowbridge.demo"]
        for email in lead_emails:
            lead = db.query(User).filter(User.email == email).first()
            if not lead:
                lead = User(
                    email=email,
                    password_hash=get_password_hash("DemoLead123!"),
                    full_name="Alex Chen",
                    role="PROJECT_LEAD",
                    is_active=True
                )
                db.add(lead)

        # 2. Incoming Member
        incoming_emails = ["incoming@knowbridge.io", "incoming@knowbridge.demo"]
        for email in incoming_emails:
            incoming = db.query(User).filter(User.email == email).first()
            if not incoming:
                incoming = User(
                    email=email,
                    password_hash=get_password_hash("Incoming123!"),
                    full_name="Jordan Reed",
                    role="INCOMING_MEMBER",
                    is_active=True
                )
                db.add(incoming)

        db.commit()

        # Feed realistic application projects if not already present
        lead_user = db.query(User).filter(User.email == "lead@knowbridge.io").first()
        if lead_user:
            from app.services.data_feeder import feed_application_data
            feed_application_data(db, lead_user)
    finally:
        db.close()

init_system_accounts()

# Register Routers under /api
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(projects_router, prefix=settings.API_V1_STR)
app.include_router(documents_router, prefix=settings.API_V1_STR)
app.include_router(analysis_router, prefix=settings.API_V1_STR)
app.include_router(handovers_router, prefix=settings.API_V1_STR)
app.include_router(incoming_router, prefix=settings.API_V1_STR)
app.include_router(activity_router, prefix=settings.API_V1_STR)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "knowbridge-backend",
        "database": "sqlite_ready",
        "version": settings.VERSION
    }

# Check for production frontend build
possible_dist_paths = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../frontend/dist")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../static")),
    os.path.abspath("./frontend/dist"),
    os.path.abspath("./static"),
]

frontend_dist = next((p for p in possible_dist_paths if os.path.exists(p) and os.path.exists(os.path.join(p, "index.html"))), None)

if frontend_dist:
    assets_path = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="static-assets")

    @app.get("/{full_path:path}")
    async def serve_spa_frontend(full_path: str):
        if full_path.startswith("api/") or full_path in ("docs", "redoc", "openapi.json"):
            return {"detail": "Not Found"}
        target_file = os.path.join(frontend_dist, full_path)
        if os.path.isfile(target_file):
            return FileResponse(target_file)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    def root():
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "operational",
            "docs_url": "/docs"
        }
