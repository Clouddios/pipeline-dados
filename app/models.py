from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class ImportFile(Base):
    __tablename__ = "import_files"

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, processing, done, failed
    created_at = Column(DateTime, default=datetime.utcnow)