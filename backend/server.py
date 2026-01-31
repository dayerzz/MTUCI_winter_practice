from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models_db import Detection, Base
from detector import run_detection
from datetime import datetime
import shutil
import uuid
import os

from pdf_generator import generate_pdf
from excel_generator import generate_excel
from database import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    uid = f"{uuid.uuid4()}_{file.filename}"
    image_path = os.path.join(UPLOAD_DIR, uid)

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = run_detection(image_path)
    motorcycles = result["motorcycles"]
    violations = sum(1 for m in motorcycles if m["violation"])

    db: Session = next(get_db())
    record = Detection(
        filename=file.filename,
        created_at=datetime.utcnow(),
        motorcycles=len(motorcycles),
        violations=violations
    )
    db.add(record)
    db.commit()

    return {
        "motorcycles": motorcycles
    }

@app.get("/history")
def history():
    db: Session = next(get_db())
    records = db.query(Detection).order_by(Detection.created_at.desc()).all()

    return [
        {
            "filename": r.filename,
            "date": r.created_at.strftime("%d.%m.%Y %H:%M:%S"),
            "motorcycles": r.motorcycles,
            "violations": r.violations
        }
        for r in records
    ]

@app.get("/report/pdf")
def report_pdf():
    return generate_pdf()

@app.get("/report/excel")
def report_excel():
    return generate_excel()