from pydantic import BaseModel
from datetime import datetime

class HistoryOut(BaseModel):
    id: int
    filename: str
    created_at: datetime
    total_motorcycles: int
    violations: int

    class Config:
        from_attributes = True