from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel

class GlobalFilter(BaseModel):
    data_inicio: date
    data_fim: date
    unidade: Optional[str] = "Todas"

def get_current_filters(request_params: dict):
    """
    Extrai e valida os filtros da query string.
    Padrão Axiom: Mês atual se nada for informado.
    """
    hoje = datetime.now()
    primeiro_dia = hoje.replace(day=1).date()
    
    d_inicio = request_params.get("start", primeiro_dia.isoformat())
    d_fim = request_params.get("end", hoje.date().isoformat())
    
    return GlobalFilter(
        data_inicio=date.fromisoformat(d_inicio),
        data_fim=date.fromisoformat(d_fim),
        unidade=request_params.get("unidade", "Todas")
    )
