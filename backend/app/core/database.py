from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# SQLite connection args
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_safe_migrations():
    """Safely adds missing columns to existing SQLite / PostgreSQL tables without data loss."""
    with engine.connect() as conn:
        # Check SQLite or Postgres
        is_sqlite = settings.DATABASE_URL.startswith("sqlite")
        
        tables_to_check = {
            "documents": [("sha256_hash", "VARCHAR(64)")],
            "handovers": [("snapshot_hash", "VARCHAR(64)")],
            "audit_logs": [("sha256_hash", "VARCHAR(64)")]
        }
        
        for table, cols in tables_to_check.items():
            try:
                if is_sqlite:
                    res = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
                    existing_cols = [r[1] for r in res]
                else:
                    res = conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'")).fetchall()
                    existing_cols = [r[0] for r in res]
                
                if existing_cols:
                    for col_name, col_type in cols:
                        if col_name not in existing_cols:
                            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}"))
                            conn.commit()
            except Exception as e:
                # Table might not exist yet before create_all
                pass
