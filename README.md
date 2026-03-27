# DFIR Workbench

A Digital Forensics and Incident Response (DFIR) platform built with Python. Covers the full IR lifecycle from alert detection to forensic analysis and report generation, following the NIST SP 800-61 incident handling framework.

---

## Features

- **Case management** — create, track, and close IR cases with auto-generated case IDs (CASE-YYYY-NNN)
- **Artifact collector** — collect log files, uploaded files, and PCAP captures per case with automatic hashing
- **Timeline builder** — chronological reconstruction of all events and findings per case
- **Report generator** — automated PDF generator (works interchangeably directly on Windows/Linux environments without GUI dependencies)
- **Live dashboard** — premium web UI for case management, alerts, findings, and timeline visualization using minimalist aesthetic
- **Honeypot integration** — custom SQLite syncing service that runs identically alongside the honeypot to auto-create IR cases from honeypot intrusions.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend Web Server | Flask |
| Database | SQLite + SQLAlchemy ORM |
| Report Generation | fpdf2 |
| Frontend | HTML, CSS, JavaScript, Chart.js, Jinja2 |
| Honeypot Integration | Native SQLite Sync Service |

---

## Project Structure

```
dfir-workbench/
├── database.py              # SQLAlchemy models: Case, Artifact, Finding, TimelineEvent
├── case_manager.py          # Case CRUD operations
├── collectors/
│   └── honeypot_sync.py     # Background sync service pulling data from honeypot DB
├── reports/
│   └── generator.py         # PDF report generation via fpdf2
├── dashboard/
│   ├── templates/           # Clean, minimalist UI Template Logic
│   │   ├── base.html
│   │   ├── cases.html
│   │   ├── case_detail.html
│   │   ├── timeline.html
│   │   ├── findings.html
│   │   ├── artifacts.html
│   │   └── reports.html
├── integrations/
│   └── honeypot/            # Fully embedded proxy HTTP/FTP/SSH honeypot directory
└── app.py                   # Main Flask routes and Dashboard Engine
```

---

## Requirements

- Python 3.10+
- Support for concurrent scripts execution

---

## Installation

**1. Clone the repository:**
```bash
git clone https://github.com/SamuelKaunang/DFIR-Workpanel.git
cd DFIR-Workpanel
```

**2. Create virtual environment and install packages:**
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux:
source venv/bin/activate

pip install flask sqlalchemy fpdf2
```

---

## Usage

For the workbench and auto-detection system to be fully operational, you need to run **three overlapping processes**:

**1. Start the Flask Dashboard:**
```bash
python app.py
```
> Open browser at `http://127.0.0.1:5000`

**2. Start the Honeypot Services (simulating attack environment):**
```bash
python integrations/honeypot/main.py
```

**3. Start the Honeypot DB Integration Sync:**
```bash
python collectors/honeypot_sync.py
```

---

## IR Workflow

This workbench follows the NIST SP 800-61 incident response lifecycle.

1. **Detection**: Attack hits honeypot services (`integrations/honeypot/main.py`)
2. **Synchronization**: Loop on (`honeypot_sync.py`) detects intrusion → Auto-creates CASE on Dashboard Data.
3. **Collection**: Analysts attach artifacts directly via the UI upload panel.
4. **Analysis**: Findings are automatically displayed identically with associated timestamps mapped across the Case Timeline graphic.
5. **Report & Containment**: Generate an automated Incident PDF Report outlining Findings, Status, Context, and Artifact Hashes within the UI layout.

---

## API Endpoints (Flask Routing)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/cases` | Dashboard UI Base (List cases and actions) |
| POST | `/cases/create` | Manual creation of a new case |
| GET | `/cases/<case_id>` | Detailed overview of a case with specific configurations |
| GET | `/artifacts` | Evidence file and configurations overview |
| POST | `/artifacts/upload` | Upload a forensic artifact (generates MD5 + SHA256 integrity verification) |
| GET | `/findings` | Master List of tracked severity violations |
| GET | `/timeline` | Visual chart activity and historical log tracing |
| GET | `/reports` | Activity and Log extractions list |
| POST | `/reports/generate/<case_id>` | Export automated log investigation as PDF |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**Samuel Kaunang**
S1 Informatika — Cybersecurity Project