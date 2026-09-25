# backend/schemas.py
# Responsabilidade: definir os contratos de entrada e saída da API.

from pydantic import BaseModel, Field
from typing import Optional


class TipoDestinacaoCreate(BaseModel):
    """Payload esperado no POST /api/tipos-destinacao"""
    nome: str = Field(..., min_length=1, max_length=255,
                      description="Nome do tipo de destinação")
    descricao: Optional[str] = Field(None, description="Descrição detalhada")
    status: Optional[str] = Field("Ativo", description="Ativo ou Inativo")


class TipoDestinacaoResponse(BaseModel):
    """Formato de retorno da API"""
    id_tipo_destinacao: int
    nome: Optional[str] = None
    descricao: Optional[str] = None
    status: Optional[str] = None