from database import SessionLocal, Case
import datetime

def generate_case_id():
    db = SessionLocal()
    year = datetime.datetime.utcnow().year
    count = db.query(Case).filter(
        Case.case_id.like(f"CASE-{year}-%")
    ).count()
    db.close()
    return f"CASE-{year}-{count+1:03d}"

def create_case(title, description, severity,
                source="manual", tags=None):
    db = SessionLocal()
    try:
        case = Case(
            case_id     = generate_case_id(),
            title       = title,
            description = description,
            severity    = severity,
            source      = source,
            tags        = tags or []
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        print(f"[CASE] Created: {case.case_id} — {title}")
        return case
    finally:
        db.close()

def update_case_status(case_id, status):
    db = SessionLocal()
    try:
        case = db.query(Case).filter(Case.case_id == case_id).first()
        if case:
            case.status     = status
            case.updated_at = datetime.datetime.utcnow()
            db.commit()
        return case
    finally:
        db.close()

def get_all_cases():
    db = SessionLocal()
    try:
        return db.query(Case).order_by(Case.created_at.desc()).all()
    finally:
        db.close()

def get_case(case_id):
    db = SessionLocal()
    try:
        return db.query(Case).filter(Case.case_id == case_id).first()
    finally:
        db.close()
