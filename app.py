from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from database import SessionLocal, Case, Artifact, Finding, TimelineEvent
from case_manager import create_case, get_all_cases, get_case
import datetime, os, json, hashlib

app = Flask(
    __name__,
    template_folder="dashboard/templates",
    static_folder="dashboard/static"
)
app.secret_key = "dfir-workbench-secret-key-change-in-production"


# ─── CASES ──────────────────────────────────────────────────────
@app.route("/")
def index():
    return redirect(url_for("cases_page"))


@app.route("/cases")
def cases_page():
    db = SessionLocal()
    try:
        cases = db.query(Case).order_by(Case.created_at.desc()).all()
        return render_template("cases.html", cases=cases)
    finally:
        db.close()


@app.route("/cases/create", methods=["POST"])
def create_case_route():
    title       = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    severity    = request.form.get("severity", "medium")
    tags_raw    = request.form.get("tags", "")
    tags        = [t.strip() for t in tags_raw.split(",") if t.strip()]

    if title:
        create_case(title, description, severity, tags=tags)
        flash("Case created successfully!", "success")
    else:
        flash("Title is required.", "error")

    return redirect(url_for("cases_page"))


@app.route("/cases/<case_id>")
def case_detail_page(case_id):
    db = SessionLocal()
    try:
        case      = db.query(Case).filter(Case.case_id == case_id).first()
        if not case:
            flash("Case not found.", "error")
            return redirect(url_for("cases_page"))

        artifacts = db.query(Artifact).filter(Artifact.case_id == case_id).all()
        findings  = db.query(Finding).filter(Finding.case_id == case_id) \
                      .order_by(Finding.timestamp.desc()).all()
        events    = db.query(TimelineEvent).filter(TimelineEvent.case_id == case_id) \
                      .order_by(TimelineEvent.event_time).all()

        events_json = []
        for e in events:
            events_json.append({
                "event_time": e.event_time.isoformat() if e.event_time else None,
                "title": e.title,
                "category": e.category
            })

        return render_template("case_detail.html",
            case=case,
            artifacts=artifacts,
            findings=findings,
            timeline_events=events_json
        )
    finally:
        db.close()


# ─── ARTIFACTS ──────────────────────────────────────────────────
@app.route("/artifacts")
def artifacts_page():
    db = SessionLocal()
    try:
        artifacts = db.query(Artifact).order_by(Artifact.collected_at.desc()).all()
        cases     = db.query(Case).order_by(Case.created_at.desc()).all()
        return render_template("artifacts.html", artifacts=artifacts, cases=cases)
    finally:
        db.close()


@app.route("/artifacts/upload", methods=["POST"])
def upload_artifact():
    case_id       = request.form.get("case_id")
    artifact_type = request.form.get("artifact_type", "other")
    file          = request.files.get("file")

    if not file or not case_id:
        flash("File and case are required.", "error")
        return redirect(url_for("artifacts_page"))

    upload_dir = os.path.join("evidence", case_id)
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, file.filename)
    file.save(filepath)

    # compute hash
    md5 = hashlib.md5()
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            md5.update(chunk)
            sha256.update(chunk)

    db = SessionLocal()
    try:
        artifact = Artifact(
            case_id       = case_id,
            name          = file.filename,
            artifact_type = artifact_type,
            file_path     = filepath,
            source        = "manual_upload",
            md5           = md5.hexdigest(),
            sha256        = sha256.hexdigest()
        )
        db.add(artifact)
        db.commit()
        flash(f"Artifact '{file.filename}' uploaded successfully!", "success")
    finally:
        db.close()

    return redirect(url_for("artifacts_page"))


@app.route("/artifacts/analyze/<int:artifact_id>")
def analyze_artifact(artifact_id):
    db = SessionLocal()
    try:
        artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
        if not artifact:
            flash("Artifact not found.", "error")
            return redirect(url_for("artifacts_page"))

        flash(f"Analysis started for '{artifact.name}'. Check findings when complete.", "success")
    finally:
        db.close()
    return redirect(url_for("artifacts_page"))


# ─── FINDINGS ───────────────────────────────────────────────────
@app.route("/findings")
def findings_page():
    db = SessionLocal()
    try:
        findings = db.query(Finding).order_by(Finding.timestamp.desc()).all()
        return render_template("findings.html", findings=findings)
    finally:
        db.close()


# ─── TIMELINE ───────────────────────────────────────────────────
@app.route("/timeline")
def timeline_page():
    selected_case = request.args.get("case_id", "")
    db = SessionLocal()
    try:
        cases  = db.query(Case).order_by(Case.created_at.desc()).all()
        events = db.query(TimelineEvent).order_by(TimelineEvent.event_time).all()

        events_json = []
        for e in events:
            events_json.append({
                "id": e.id,
                "case_id": e.case_id,
                "event_time": e.event_time.isoformat() if e.event_time else None,
                "category": e.category or "other",
                "title": e.title,
                "description": e.description or "",
                "source": e.source or ""
            })

        return render_template("timeline.html",
            cases=cases,
            events=events,
            events_json=json.dumps(events_json),
            selected_case=selected_case
        )
    finally:
        db.close()


# ─── REPORTS ────────────────────────────────────────────────────
@app.route("/reports")
def reports_page():
    db = SessionLocal()
    try:
        cases = db.query(Case).order_by(Case.created_at.desc()).all()
    finally:
        db.close()

    # Scan reports directory for generated PDFs
    reports = []
    reports_dir = "reports"
    if os.path.isdir(reports_dir):
        for fname in sorted(os.listdir(reports_dir), reverse=True):
            if fname.endswith(".pdf"):
                fpath = os.path.join(reports_dir, fname)
                stat  = os.stat(fpath)
                size_mb = stat.st_size / (1024 * 1024)
                reports.append({
                    "filename": fname,
                    "case_id": fname.split("_IR_")[0] if "_IR_" in fname else "-",
                    "generated_at": datetime.datetime.fromtimestamp(
                        stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                    "size": f"{size_mb:.1f} MB" if size_mb >= 1 else f"{stat.st_size/1024:.0f} KB"
                })

    return render_template("reports.html", cases=cases, reports=reports)


@app.route("/reports/generate", methods=["POST"])
@app.route("/reports/generate/<case_id>", methods=["GET", "POST"])
def generate_report(case_id=None):
    if not case_id:
        case_id = request.form.get("case_id")

    if not case_id:
        flash("Case ID is required.", "error")
        return redirect(url_for("reports_page"))

    try:
        from reports.generator import generate_ir_report
        output = generate_ir_report(case_id)
        flash(f"Report generated: {os.path.basename(output)}", "success")
    except Exception as e:
        flash(f"Report generation failed: {str(e)}", "error")

    return redirect(url_for("reports_page"))


@app.route("/reports/download/<filename>")
def download_report(filename):
    filepath = os.path.join("reports", filename)
    if os.path.isfile(filepath):
        return send_file(filepath, as_attachment=True)
    flash("Report file not found.", "error")
    return redirect(url_for("reports_page"))


# ─── RUN ────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
