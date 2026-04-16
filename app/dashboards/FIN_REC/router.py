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
async def get_receber_evolucao(inicio: str = "", fim: str = ""):
    try:
        data = service.get_bi_evolucao(inicio, fim)
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Erro no Router Evolução: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/aging")
async def get_receber_aging(inicio: str = "", fim: str = ""):
    try:
        data = service.get_aging_data(inicio, fim)
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Erro no Router Aging: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/devedores")
async def get_receber_devedores(inicio: str = "", fim: str = ""):
    try:
        data = service.get_top_devedores(inicio, fim)
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Erro no Router Devedores: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/fluxo-caixa")
async def get_receber_fluxo(inicio: str = "", fim: str = ""):
    try:
        data = service.get_fluxo_caixa(inicio, fim)
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Erro no Router Fluxo de Caixa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sparklines")
async def get_sparklines():
    try:
        data = service.get_sparklines()
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Erro no Router Sparklines: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_receber_performance(inicio: str = "", fim: str = ""):
    try:
        data = service.get_performance_mensal(inicio, fim)
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Erro no Router Performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))
