from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.dashboards.TECNICO.service import TecnicoService

# Definimos o prefixo /dashboard/tecnico para todas as rotas deste arquivo
router = APIRouter(prefix="/dashboard/tecnico")
templates = Jinja2Templates(directory="app/templates")
service = TecnicoService()

@router.get("/", response_class=HTMLResponse)
async def tecnico_page(request: Request):
    """
    Renderiza a página principal do Dashboard Técnico.
    """
    return templates.TemplateResponse("dashboards/TECNICO/index.html", {
        "request": request,
        "session": request.session
    })

@router.get("/api/resumo")
async def get_tecnico_api(inicio: str, fim: str):
    """
    Rota de API que o JavaScript vai chamar para buscar os dados dos gráficos.
    """
    try:
        dados = service.get_dashboard_tecnico(inicio, fim)
        
        if not dados:
            return {"status": "success", "data": {}}
            
        return {"status": "success", "data": dados}
        
    except Exception as e:
        print(f"Erro no Router Técnico: {e}")
        raise HTTPException(status_code=500, detail=str(e))
