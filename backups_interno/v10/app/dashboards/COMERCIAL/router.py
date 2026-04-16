from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.dashboards.COMERCIAL.service import ComercialService
from typing import Optional

# Mantendo o padrão: Prefixo comercial para organizar as URLs
router = APIRouter(prefix="/dashboard/comercial")
templates = Jinja2Templates(directory="app/templates")
service = ComercialService()

@router.get("/", response_class=HTMLResponse)
async def comercial_page(request: Request):
    """
    Renderiza a página HTML do Dashboard Comercial.
    """
    return templates.TemplateResponse("dashboards/COMERCIAL/index.html", {
        "request": request,
        "session": request.session
    })

@router.get("/api/resumo")
async def get_comercial_api(inicio: str = "", fim: str = "", vendedor_id: Optional[int] = None):
    """
    Rota de API para alimentar os gráficos.
    Agora aceita vendedor_id como parâmetro opcional.
    """
    try:
        # Passamos o vendedor_id para o service processar nas queries
        dados = service.get_dashboard_comercial(inicio, fim, vendedor_id)

        if not dados:
            return {"status": "success", "data": {}}

        return {"status": "success", "data": dados}

    except Exception as e:
        print(f"Erro no Router Comercial (API): {e}")
        raise HTTPException(status_code=500, detail=str(e))
