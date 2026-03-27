import sys
sys.path.insert(0, '/mnt/d/Cyber Projects/honeypot')

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import SessionLocal, Event
from stats import get_stats

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="/mnt/d/Cyber Projects/honeypot/dashboard/static"),
    name="static"
)
templates = Jinja2Templates(
    directory="/mnt/d/Cyber Projects/honeypot/dashboard/templates"
)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/api/stats")
async def api_stats():
    return get_stats()

@app.get("/api/events")
async def api_events(limit: int = 50):
    db = SessionLocal()
    try:
        events = db.query(Event)\
            .order_by(Event.timestamp.desc())\
            .limit(limit).all()
        return [{
            "id": e.id,
            "timestamp": e.timestamp.isoformat(),
            "service": e.service,
            "src_ip": e.src_ip,
            "country": e.country or "Unknown",
            "city": e.city or "Unknown",
            "extra": e.extra or {}
        } for e in events]
    finally:
        db.close()

@app.get("/api/events/{event_id}")
async def api_event_detail(event_id: int):
    db = SessionLocal()
    try:
        e = db.query(Event).filter(Event.id == event_id).first()
        if not e:
            return {"error": "not found"}
        return {
            "id": e.id,
            "timestamp": e.timestamp.isoformat(),
            "service": e.service,
            "src_ip": e.src_ip,
            "src_port": e.src_port,
            "country": e.country or "Unknown",
            "city": e.city or "Unknown",
            "raw_data": e.raw_data,
            "extra": e.extra or {}
        }
    finally:
        db.close()
