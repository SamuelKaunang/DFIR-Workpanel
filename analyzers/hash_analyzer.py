import hashlib
from database import SessionLocal, Finding
import datetime

KNOWN_MALWARE = {
    "44d88612fea8a8f36de82e1278abb02f": "EICAR test file",
}

def analyze_hash(artifact):
    results = {}
    if not artifact.file_path:
        return results

    md5    = hashlib.md5()
    sha256 = hashlib.sha256()
    sha1   = hashlib.sha1()
    with open(artifact.file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            md5.update(chunk); sha256.update(chunk); sha1.update(chunk)

    results = {
        "md5":    md5.hexdigest(),
        "sha1":   sha1.hexdigest(),
        "sha256": sha256.hexdigest()
    }

    # Cek ke known malware list
    if results["md5"] in KNOWN_MALWARE:
        save_finding(artifact.case_id, artifact.id,
            "ioc", "Known malware hash detected",
            f"Hash matches: {KNOWN_MALWARE[results['md5']]}",
            "critical", results)
    return results

def save_finding(case_id, artifact_id, ftype,
                  title, desc, severity, data):
    db = SessionLocal()
    try:
        f = Finding(
            case_id      = case_id,
            artifact_id  = artifact_id,
            finding_type = ftype,
            title        = title,
            description  = desc,
            severity     = severity,
            timestamp    = datetime.datetime.utcnow(),
            data         = data
        )
        db.add(f); db.commit()
        print(f"[FINDING] {severity.upper()}: {title}")
    finally:
        db.close()