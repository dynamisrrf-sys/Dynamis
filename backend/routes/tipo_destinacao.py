# backend/routes/tipo_destinacao.py
# Responsabilidade: definir os endpoints HTTP ligados à tabela tipo_destinacao.

from fastapi import APIRouter, HTTPException, status
from typing import List

from database import supabase
from schemas import TipoDestinacaoCreate, TipoDestinacaoResponse
from models import TABELA_TIPO_DESTINACAO

router = APIRouter(
    prefix="/api/tipos-destinacao",
    tags=["Tipo de Destinação"]
)


# ---------------------------------------------------------
# GET /api/tipos-destinacao — lista todos
# ---------------------------------------------------------
@router.get("", response_model=List[TipoDestinacaoResponse])
def listar_tipos_destinacao():
    resposta = (
        supabase.table(TABELA_TIPO_DESTINACAO)
        .select("*")
        .order("id_tipo_destinacao")
        .execute()
    )
    return resposta.data


# ---------------------------------------------------------
# GET /api/tipos-destinacao/{id} — busca por ID
# ---------------------------------------------------------
@router.get("/{id_tipo}", response_model=TipoDestinacaoResponse)
def buscar_tipo_destinacao(id_tipo: int):
    resposta = (
        supabase.table(TABELA_TIPO_DESTINACAO)
        .select("*")
        .eq("id_tipo_destinacao", id_tipo)
        .execute()
    )
    if not resposta.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de destinação não encontrado"
        )
    return resposta.data[0]


# ---------------------------------------------------------
# POST /api/tipos-destinacao — cria novo
# ---------------------------------------------------------
@router.post(
    "",
    response_model=TipoDestinacaoResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_tipo_destinacao(payload: TipoDestinacaoCreate):
    try:
        resposta = (
            supabase.table(TABELA_TIPO_DESTINACAO)
            .insert({
                "nome": payload.nome,
                "descricao": payload.descricao,
                "status": payload.status or "Ativo",
            })
            .execute()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao inserir no Supabase: {str(e)}"
        )

    if not resposta.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="O Supabase não retornou o registro criado."
        )
    return resposta.data[0]