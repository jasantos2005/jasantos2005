from fastapi import APIRouter, HTTPException, Request
from app.dashboards.FIN_REC.service import FinanceiroService

router = APIRouter()
service = FinanceiroService()

@router.get("/resumo")
async def get_receber_resumo(inicio: str = "", fim: str = ""):
    """
    Retorna os dados dos cards de KPI (Resumo financeiro atual)
    """
    try:
        data = service.get_resumo(inicio, fim)
        if not data:
            return {"status": "success", "data": {}}
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Erro no Router Receber (Resumo): {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/evolucao")
async def get_receber_evolucao():
    """
    NOVO V6: Retorna os dados para o gráfico de linha (BI)
    Mostra a evolução de Recebidos vs Inadimplência
    """
    try:
        data = service.get_bi_evolucao()
        if not data:
            return {"status": "success", "data": {"labels": [], "recebido": [], "inadimplente": []}}
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Erro no Router Receber (Evolução BI): {e}")
        raise HTTPException(status_code=500, detail=str(e))
