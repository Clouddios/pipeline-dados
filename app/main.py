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

@app.post("/test-transacao-quebrada")
def test_transacao_quebrada():
    db = SessionLocal()
    db.add(ImportFile(filename="arquivo_1.csv"))
    db.add(ImportFile(filename="arquivo_2.csv"))
    db.add(ImportFile(filename=None))  # isso vai violar o "nullable=False" e quebrar
    db.commit()  # nunca chega aqui
    db.close()
    return {"status": "nunca deveria chegar aqui"}

@app.post("/test-transacao-por-linha")
def test_transacao_por_linha():
    arquivos = ["arquivo_a.csv", "arquivo_b.csv", None, "arquivo_c.csv"]
    sucesso = []
    falhas = []

    for nome in arquivos:
        db = SessionLocal()
        try:
            db.add(ImportFile(filename=nome))
            db.commit()
            sucesso.append(nome)
        except Exception as e:
            db.rollback()  # desfaz só essa tentativa
            falhas.append({"arquivo": nome, "erro": str(e)[:100]})
        finally:
            db.close()

    return {"sucesso": sucesso, "falhas": falhas}

import random

@app.post("/test-popular")
def test_popular():
    db = SessionLocal()
    for i in range(50000):
        db.add(ImportFile(filename=f"arquivo_{i}.csv"))
        if i % 1000 == 0:  # commita em lotes, não um por um (isso ia demorar muito)
            db.commit()
    db.commit()
    db.close()
    return {"status": "50000 registros criados"}