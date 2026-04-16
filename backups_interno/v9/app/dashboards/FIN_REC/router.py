from fastapi import APIRouter, HTTPException
from app.dashboards.FIN_REC.service import FinanceiroService

router = APIRouter()
service = FinanceiroService()

@router.get("/resumo")
async def get_receber_resumo(inicio: str = "", fim: str = ""):
    try:
        data = service.get_resumo(inicio, fim)
        if not data:
            return {"status": "success", "data": {}}
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Erro no Router Receber: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/evolucao")
async def get_receber_evolucao():
    """
    Nova rota para alimentar o gráfico de evolução (BI)
    """
    try:
        data = service.get_bi_evolucao()
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Erro no Router Evolução: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/aging")
async def get_receber_aging():
    """
    Versão 7: Rota para o gráfico de envelhecimento da dívida (Aging)
    """
    try:
        data = service.get_aging_data()
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Erro no Router Aging: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/devedores")
async def get_receber_devedores():
    """
    Versão 8: Rota para o ranking dos 10 maiores devedores
    """
    try:
        data = service.get_top_devedores()
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Erro no Router Devedores: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/fluxo-caixa")
async def get_receber_fluxo():
    """
    Versão 9: Rota para o resumo de Fluxo de Caixa (Entradas vs Saídas)
    """
    try:
        data = service.get_fluxo_caixa()
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Erro no Router Fluxo de Caixa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_receber_performance():
    """
    Versão 10: Rota para o gráfico de Performance Mensal (Faturamento vs Recebido + % Inadimplência)
    """
    try:
        data = service.get_performance_mensal()
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Erro no Router Performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))
