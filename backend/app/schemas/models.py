from datetime import date, time
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


TipoPerfil = Literal["consumidor", "estabelecimento", "agente"]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class SignupRequest(LoginRequest):
    tipo_perfil: TipoPerfil
    nome: str = Field(min_length=2, max_length=150)
    documento: str = Field(min_length=11, max_length=18)
    tipo: str = Field(min_length=2, max_length=60)
    telefone: str | None = Field(default=None, max_length=20)
    responsavel: str | None = Field(default=None, max_length=150)
    cidade: str | None = Field(default=None, max_length=100)

    @field_validator("documento")
    @classmethod
    def normalize_document(cls, value: str) -> str:
        digits = "".join(character for character in value if character.isdigit())
        if len(digits) not in (11, 14):
            raise ValueError("O documento deve conter CPF ou CNPJ válido em quantidade de dígitos.")
        return digits

    @model_validator(mode="after")
    def validate_profile_document(self):
        expected = 11 if self.tipo_perfil == "consumidor" else 14
        if len(self.documento) != expected:
            label = "CPF" if expected == 11 else "CNPJ"
            raise ValueError(f"O perfil selecionado exige {label}.")
        return self


class ExcedenteCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    categoria: str = Field(min_length=2, max_length=80)
    descricao: str | None = None
    quantidade: Decimal = Field(gt=0)
    unidade_medida: str = Field(min_length=1, max_length=20)
    data_producao: date | None = None
    validade: date
    condicao: str = Field(min_length=2, max_length=80)
    temperatura_conservacao: Decimal | None = None
    embalagem: str | None = Field(default=None, max_length=100)
    horario_disponibilidade: time | None = None
    urgencia: str = Field(default="normal", max_length=30)
    observacoes: str | None = None


class ClassificacaoCreate(BaseModel):
    id_excedente: int = Field(gt=0)
    aptidao_consumo: bool
    destino_recomendado: str = Field(min_length=2, max_length=30)
    prioridade: str = Field(default="normal", max_length=30)
    justificativa: str = Field(min_length=5)
    responsavel: str = Field(min_length=2, max_length=150)
    observacoes: str | None = None


class DestinacaoCreate(BaseModel):
    id_classificacao: int = Field(gt=0)
    id_tipo_destinacao: int = Field(gt=0)
    quantidade: Decimal = Field(gt=0)
    unidade_medida: str = Field(min_length=1, max_length=20)
    condicao: str = Field(min_length=2, max_length=80)
    responsavel: str = Field(min_length=2, max_length=150)
    data_inicio: date
    data_fim: date | None = None
    horario_inicio: time | None = None
    horario_fim: time | None = None
    local: str = Field(min_length=2, max_length=180)
    preco_original: Decimal | None = Field(default=None, ge=0)
    preco_final: Decimal | None = Field(default=None, ge=0)
    percentual_desconto: Decimal | None = Field(default=None, ge=0, le=100)
    motivo: str | None = None
    observacoes: str | None = None


class ReservaCreate(BaseModel):
    id_destinacao: int = Field(gt=0)
    quantidade: Decimal = Field(gt=0)


class CancelamentoReserva(BaseModel):
    motivo: str = Field(min_length=5, max_length=500)
