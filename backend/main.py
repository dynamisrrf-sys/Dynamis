# backend/main.py
# Responsabilidade: inicializar o FastAPI, configurar CORS e registrar as rotas.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import tipo_destinacao

app = FastAPI(
    title="DYNAMIS API",
    version="1.0.0",
    description="API de gestão de excedentes alimentares — DYNAMIS"
)

# CORS para permitir o frontend (HTML/JS) consumir a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro das rotas
app.include_router(tipo_destinacao.router)


@app.get("/", tags=["Health"])
def raiz():
    return {
        "status": "OK",
        "projeto": "DYNAMIS",
        "versao": "1.0.0",
        "docs": "/docs"
    }