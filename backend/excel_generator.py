import openpyxl
from database import SessionLocal
from models_db import Detection

def generate_excel():
    path = "report.xlsx"

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Статистика"

    ws.append([
        "Файл",
        "Дата",
        "Мотоциклов",
        "Нарушений"
    ])

    db = SessionLocal()

    for r in db.query(Detection).all():
        ws.append([
            r.filename,
            r.created_at.strftime("%d.%m.%Y %H:%M:%S"),
            r.motorcycles,
            r.violations
        ])

    db.close()
    wb.save(path)
    return path