from fastapi import APIRouter, Query
from app.dashboards.FIN_PAG.service import PagarService

router = APIRouter(prefix="/api/financeiro/pagar")
service = PagarService()

@router.get("/resumo")
async def get_pagar_resumo(
    inicio: str = Query("", description="Data de início"),
    fim: str = Query("", description="Data de fim")
):
    return {
        "status": "success", 
        "data": service.get_resumo_pagar(inicio=inicio, fim=fim)
    }
