from database import SessionLocal
from routers.bugs import get_bug_stats
db = SessionLocal()
stats = get_bug_stats(recent_days=365, db=db)
print("Monthly trend:", stats['monthly_trend'])
print("By status:", stats['by_status'])
