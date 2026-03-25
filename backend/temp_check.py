from database import SessionLocal
from models import Bug

db = SessionLocal()
print("Total bugs:", db.query(Bug).count())
print("First 5 bugs dates:", db.query(Bug.cr_created_on).limit(5).all())
