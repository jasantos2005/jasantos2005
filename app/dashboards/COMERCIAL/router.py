from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.dashboards.COMERCIAL.service import ComercialService
from typing import Optional

router = APIRouter(prefix="/dashboard/comercial")
templates = Jinja2Templates(directory="app/templates")
service = ComercialService()


@router.get("/", response_class=HTMLResponse)
async def comercial_page(request: Request):
    return templates.TemplateResponse("dashboards/COMERCIAL/index.html", {
        "request": request,
        "session": request.session
    })


@router.get("/api/resumo")
async def get_resumo(inicio: str = "", fim: str = ""):
    try:
        data = service.get_resumo(inicio, fim)
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"[ComercialRouter] Resumo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ranking")
async def get_ranking(periodo: str = "mes"):
    try:
        data = service.get_ranking(periodo)
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"[ComercialRouter] Ranking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/evolucao")
async def get_evolucao(periodo: str = "mes"):
    try:
        data = service.get_evolucao(periodo)
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"[ComercialRouter] Evolução: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/motivos")
async def get_motivos(periodo: str = "mes"):
    try:
        data = service.get_motivos(periodo)
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"[ComercialRouter] Motivos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/produtividade")
async def get_produtividade():
    try:
        data = service.get_produtividade()
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"[ComercialRouter] Produtividade: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/bairros")
async def get_bairros(periodo: str = "mes"):
    try:
        data = service.get_vendas_por_bairro(periodo)
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"[ComercialRouter] Bairros: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/vendedor/{vendedor_id}")
async def get_perfil_vendedor(vendedor_id: int, periodo: str = "mes"):
    try:
        data = service.get_perfil_vendedor(vendedor_id, periodo)
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"[ComercialRouter] Perfil Vendedor: {e}")
        raise HTTPException(status_code=500, detail=str(e))
