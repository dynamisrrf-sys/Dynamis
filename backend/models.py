# backend/models.py
# Responsabilidade: manter constantes de domínio e (futuramente) regras
# que não pertencem às rotas nem aos schemas.

class TipoDestinacaoStatus:
    ATIVO = "Ativo"
    INATIVO = "Inativo"

    @classmethod
    def valores_validos(cls) -> list[str]:
        return [cls.ATIVO, cls.INATIVO]


TABELA_TIPO_DESTINACAO = "tipo_destinacao"