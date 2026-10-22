
from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

OUTPUT_DIR = Path(__file__).resolve().parent / "certificates"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "sample_certificate.pdf"

width, height = landscape(A4)
pdf = canvas.Canvas(str(OUTPUT_FILE), pagesize=(width, height))

pdf.setTitle("Sample Academic Certificate")
pdf.setStrokeColorRGB(0.12, 0.25, 0.45)
pdf.setLineWidth(4)
pdf.rect(25, 25, width - 50, height - 50)

pdf.setLineWidth(1)
pdf.rect(35, 35, width - 70, height - 70)

pdf.setFont("Helvetica-Bold", 24)
pdf.drawCentredString(
    width / 2, height - 100, "SAMPLE ACADEMIC CERTIFICATE"
)

pdf.setFont("Helvetica", 13)
pdf.drawCentredString(
    width / 2, height - 140, "For software testing only"
)

pdf.setFont("Helvetica", 15)
pdf.drawCentredString(
    width / 2, height - 190, "This certifies that"
)

pdf.setFont("Helvetica-Bold", 23)
pdf.drawCentredString(
    width / 2, height - 230, "Test Student"
)

pdf.setFont("Helvetica", 14)
pdf.drawCentredString(
    width / 2, height - 270, "Student ID: TEST-V2-001"
)
pdf.drawCentredString(
    width / 2, height - 300, "Degree: BE Computer Science Engineering"
)
pdf.drawCentredString(
    width / 2, height - 330, "Institution: Sample University"
)

pdf.setFont("Helvetica-Oblique", 10)
pdf.drawCentredString(
    width / 2, 60, "FICTIONAL TEST DOCUMENT — NOT AN OFFICIAL CERTIFICATE"
)

pdf.save()

print("Sample certificate created:", OUTPUT_FILE)
print("File size:", OUTPUT_FILE.stat().st_size, "bytes")
