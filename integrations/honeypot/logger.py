from database import SessionLocal, Event
from geoip import get_geo
import datetime

def log_event(service, src_ip, src_port, data=None, extra=None):
    geo = get_geo(src_ip)
    event = Event(
        timestamp = datetime.datetime.utcnow(),
        service   = service,
        src_ip    = src_ip,
        src_port  = src_port,
        country   = geo.get("country"),
        city      = geo.get("city"),
        raw_data  = data.decode("utf-8", errors="replace") if data else None,
        extra     = extra or {}
    )
    db = SessionLocal()
    try:
        db.add(event)
        db.commit()
        print(f"[LOG] {event.timestamp} | {service} | {src_ip} ({geo['country']})")
    except Exception as e:
        print(f"[LOG ERROR] {e}")
        db.rollback()
    finally:
        db.close()
    return event
