from fastapi import APIRouter, Query
from app.dashboards.FIN_CONSOLIDADO.service import ConsolidadoService

router = APIRouter(prefix="/api/financeiro/consolidado")
service = ConsolidadoService()

@router.get("/resumo")
async def get_consolidado(inicio: str = Query(...), fim: str = Query(...)):
    data = service.get_fluxo_caixa(inicio, fim)
    return {"status": "success", "data": data}
