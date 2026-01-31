from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from database import SessionLocal
from models_db import Detection

def generate_pdf():
    path = "report.pdf"
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    db = SessionLocal()
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Отчёт по детектированию")
    y -= 40

    for r in db.query(Detection).all():
        c.setFont("Helvetica", 11)
        c.drawString(50, y, f"Файл: {r.filename}")
        y -= 16
        c.drawString(
            50, y,
            f"Мотоциклов: {r.motorcycles}, Нарушений: {r.violations}"
        )
        y -= 30

        if y < 100:
            c.showPage()
            y = height - 50

    db.close()
    c.save()
    return path