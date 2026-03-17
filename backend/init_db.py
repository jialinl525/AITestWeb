"""
Initialize the database and create the schema.
"""
from database import engine, Base
import models  # noqa: F401 - needed so model classes register with Base.metadata
from database import SessionLocal
from routers.personnel import bootstrap_security_data

def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        bootstrap_security_data(db)
    finally:
        db.close()
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
