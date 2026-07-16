from fastapi import FastAPI
from sqlalchemy import create_engine, text
from app.models import Base, ImportFile
from sqlalchemy.orm import sessionmaker

app = FastAPI()

DATABASE_URL = "postgresql://pipeline:pipeline@localhost:5432/pipeline"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(engine)  # cria as tabelas que ainda não existem

@app.get("/health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok", "db": "connected"}

@app.post("/test-insert")
def test_insert():
    db = SessionLocal()
    novo = ImportFile(filename="teste.csv")
    db.add(novo)
    db.commit()
    db.refresh(novo)
    db.close()
    return {"id": novo.id, "status": novo.status}

@app.get("/test-list")
def test_list():
    db = SessionLocal()
    arquivos = db.query(ImportFile).all()
    db.close()
    return [{"id": a.id, "filename": a.filename, "status": a.status} for a in arquivos]