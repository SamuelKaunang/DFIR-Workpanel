from sqlalchemy import func
from database import SessionLocal, Event

def get_stats():
    db = SessionLocal()
    try:
        total = db.query(Event).count()

        unique_ips = db.query(
            func.count(func.distinct(Event.src_ip))
        ).scalar()

        top_ips = db.query(
            Event.src_ip,
            func.count(Event.id).label("count")
        ).group_by(Event.src_ip)\
         .order_by(func.count(Event.id).desc())\
         .limit(10).all()

        by_service = db.query(
            Event.service,
            func.count(Event.id).label("count")
        ).group_by(Event.service).all()

        return {
            "total": total,
            "unique_ips": unique_ips,
            "top_ips": [{"ip": r[0], "count": r[1]} for r in top_ips],
            "by_service": [{"service": r[0], "count": r[1]} for r in by_service]
        }
    finally:
        db.close()