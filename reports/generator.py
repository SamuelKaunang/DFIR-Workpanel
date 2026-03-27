import os
import datetime
from fpdf import FPDF
from database import SessionLocal, Case, Artifact, Finding, TimelineEvent

class PDFReport(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'DFIR Incident Report', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_ir_report(case_id, output_path=None):
    db = SessionLocal()
    try:
        case = db.query(Case).filter(Case.case_id == case_id).first()
        artifacts = db.query(Artifact).filter(Artifact.case_id == case_id).all()
        findings = db.query(Finding).filter(Finding.case_id == case_id).all()
    finally:
        db.close()

    if not case:
        raise ValueError(f"Case {case_id} not found.")

    pdf = PDFReport()
    pdf.add_page()
    
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, f"Case Details: {case_id}", 0, 1)
    
    pdf.set_font('helvetica', '', 10)
    pdf.cell(50, 8, "Title:", 0, 0)
    pdf.cell(0, 8, case.title, 0, 1)
    pdf.cell(50, 8, "Severity:", 0, 0)
    pdf.cell(0, 8, case.severity.upper(), 0, 1)
    pdf.cell(50, 8, "Status:", 0, 0)
    pdf.cell(0, 8, case.status.upper(), 0, 1)
    pdf.cell(50, 8, "Date Created:", 0, 0)
    pdf.cell(0, 8, str(case.created_at), 0, 1)
    pdf.ln(5)
    
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 8, "Description / Summary", 0, 1)
    pdf.set_font('helvetica', '', 10)
    pdf.multi_cell(0, 6, case.description or "No description provided.")
    pdf.ln(5)
    
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, "Critical Findings", 0, 1)
    pdf.set_font('helvetica', '', 10)
    if not findings:
        pdf.cell(0, 8, "No findings recorded.", 0, 1)
    else:
        for f in findings:
            pdf.set_font('helvetica', 'B', 10)
            pdf.cell(0, 8, f"- {f.title} ({f.severity.upper()})", 0, 1)
            pdf.set_font('helvetica', '', 9)
            # Encode string carefully to avoid character map errors in basic FPDF
            desc = (f.description or "N/A").encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 5, desc)
            pdf.ln(3)

    pdf.ln(5)
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, "Evidence Artifacts", 0, 1)
    pdf.set_font('helvetica', '', 10)
    if not artifacts:
        pdf.cell(0, 8, "No artifacts collected.", 0, 1)
    else:
        for a in artifacts:
            pdf.cell(0, 6, f"- {a.name} [{a.artifact_type.upper()}] (MD5: {a.md5})", 0, 1)

    os.makedirs("reports", exist_ok=True)
    output = output_path or f"reports/{case_id}_IR_Report.pdf"
    pdf.output(output)
    print(f"[REPORT] Generated: {output}")
    return output