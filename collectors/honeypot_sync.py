import sqlite3
import datetime
import time
import os
import sys

# Tambahkan root path ke sys.path agar bisa import module root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import SessionLocal, Case, Finding, TimelineEvent
from case_manager import create_case

HONEYPOT_DB = os.path.join("integrations", "honeypot", "honeypot.db")

def parse_time(ts_str):
    if not ts_str:
        return datetime.datetime.utcnow()
    # Handle string from sqlite Like "2026-10-24 02:45:00.123456"
    try:
        return datetime.datetime.fromisoformat(ts_str)
    except:
        return datetime.datetime.utcnow()

def sync_honeypot():
    print("[HONEYPOT SYNC] Starting background sync process...")
    last_id = 0
    
    # Try to get the last_id from the existing db to avoid recreating thousands if present
    # But usually we want all to show.
    
    while True:
        if not os.path.exists(HONEYPOT_DB):
            time.sleep(5)
            continue
            
        try:
            conn = sqlite3.connect(HONEYPOT_DB)
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, service, src_ip, src_port, country, raw_data FROM events WHERE id > ?", (last_id,))
            rows = cursor.fetchall()
            conn.close()
            
            if rows:
                db = SessionLocal()
                # Cari atau buat Kasus baru khusus Honeypot
                case = db.query(Case).filter(Case.title == "Automated Honeypot Intrusions").first()
                if not case:
                    case = create_case("Automated Honeypot Intrusions", "Aggregates all intrusion attempts caught by the local honeypot", "high", "honeypot", ["honeypot", "automated"])
                    
                for row in rows:
                    evt_id, ts, service, ip, port, country, raw_data = row
                    event_time = parse_time(ts)
                    
                    # Tambah Timeline
                    te = TimelineEvent(
                        case_id = case.case_id,
                        event_time = event_time,
                        category="network",
                        title=f"{service} Connection Attempt",
                        description=f"Source: {ip}:{port} (Country: {country or 'Unknown'})",
                        source="honeypot"
                    )
                    db.add(te)
                    
                    # Tambah Finding jika ada raw_data (payload)
                    f = Finding(
                        case_id = case.case_id,
                        finding_type = "anomaly",
                        title = f"Unauthorized {service} Payload from {ip}",
                        description = f"Connection from {country or 'Unknown'}.\nRaw Data:\n{raw_data[:200] if raw_data else 'No payload captured'}",
                        severity="high" if raw_data else "medium",
                        timestamp = event_time
                    )
                    db.add(f)
                    
                    last_id = evt_id
                
                db.commit()
                db.close()
                print(f"[HONEYPOT SYNC] Successfully synced {len(rows)} new honeypot events to DFIR Dashboard.")
                
        except Exception as e:
            print(f"[HONEYPOT SYNC ERR] {e}")
            
        time.sleep(5)

if __name__ == "__main__":
    sync_honeypot()
