import csv, io, json
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import date
import os

from app.dashboards.ESTOQUE.service import (
    get_dashboard, get_itens, get_sugestao, get_movimentacoes,
    registrar_movimentacao, get_pedidos, criar_pedido, get_historico
)

router = APIRouter(prefix="/dashboard/estoque", tags=["estoque"])
BASE_DIR  = "/opt/automacoes/GSG/gestao/diretoria/dashboards/app"
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

def _user(request: Request):
    return request.session.get("user")

def _datas():
    hoje = date.today()
    return str(hoje.replace(day=1)), str(hoje)

# ── PÁGINA SPA ──────────────────────────────────────────────────
@router.get("/", response_class=HTMLResponse)
async def estoque_spa(request: Request):
    user = _user(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)
    if "EST" not in user.get("permissao","") and user.get("nivel") != 99:
        return RedirectResponse(url="/dashboard/home?error=sem_permissao", status_code=303)
    return templates.TemplateResponse("dashboards/ESTOQUE/index.html", {
        "request": request, "session": request.session
    })

# ── API DASHBOARD ───────────────────────────────────────────────
@router.get("/api/dashboard")
async def api_dashboard(request: Request, de: str = "", ate: str = ""):
    if not _user(request):
        return JSONResponse({"error": "401"}, status_code=401)
    ini, fim = _datas()
    return get_dashboard(de or ini, ate or fim)

# ── API ESTOQUE ─────────────────────────────────────────────────
@router.get("/api/estoque/casa")
async def api_casa(request: Request, de: str = "", ate: str = ""):
    if not _user(request):
        return JSONResponse({"error": "401"}, status_code=401)
    ini, fim = _datas()
    return {"itens": get_itens("%CASA%", de or ini, ate or fim)}

@router.get("/api/estoque/infra")
async def api_infra(request: Request, de: str = "", ate: str = ""):
    if not _user(request):
        return JSONResponse({"error": "401"}, status_code=401)
    ini, fim = _datas()
    return {"itens": get_itens("%INFRA%", de or ini, ate or fim)}

# ── API SUGESTÃO ────────────────────────────────────────────────
@router.get("/api/sugestao")
async def api_sugestao(request: Request, de: str = "", ate: str = ""):
    if not _user(request):
        return JSONResponse({"error": "401"}, status_code=401)
    ini, fim = _datas()
    return {"itens": get_sugestao(de or ini, ate or fim)}

# ── API MOVIMENTAÇÕES ───────────────────────────────────────────
@router.get("/api/movimentacoes")
async def api_movimentacoes(request: Request, de: str = "", ate: str = ""):
    if not _user(request):
        return JSONResponse({"error": "401"}, status_code=401)
    ini, fim = _datas()
    return {"movimentacoes": get_movimentacoes(de or ini, ate or fim)}

@router.post("/api/movimentacao")
async def api_registrar_mov(request: Request):
    user = _user(request)
    if not user:
        return JSONResponse({"error": "401"}, status_code=401)
    body = await request.json()
    body["responsavel"] = user.get("nome", "sistema")
    registrar_movimentacao(body)
    return {"ok": True}

# ── API PEDIDOS ─────────────────────────────────────────────────
@router.get("/api/pedidos")
async def api_pedidos(request: Request):
    if not _user(request):
        return JSONResponse({"error": "401"}, status_code=401)
    return {"pedidos": get_pedidos()}

@router.post("/api/pedido")
async def api_criar_pedido(request: Request):
    user = _user(request)
    if not user:
        return JSONResponse({"error": "401"}, status_code=401)
    body = await request.json()
    itens = body.get("itens", [])
    if not itens:
        return JSONResponse({"error": "Nenhum item"}, status_code=400)
    pid = criar_pedido(itens, user.get("nome", "sistema"))
    return {"ok": True, "id": pid}

# ── API HISTÓRICO ───────────────────────────────────────────────
@router.get("/api/historico")
async def api_historico(request: Request, de: str = "", ate: str = ""):
    if not _user(request):
        return JSONResponse({"error": "401"}, status_code=401)
    ini, fim = _datas()
    return {"itens": get_historico(de or ini, ate or fim)}

# ── EXPORT CSV ──────────────────────────────────────────────────
@router.get("/api/estoque/casa/csv")
async def csv_casa(request: Request, de: str = "", ate: str = ""):
    if not _user(request):
        return JSONResponse({"error": "401"}, status_code=401)
    ini, fim = _datas()
    itens = get_itens("%CASA%", de or ini, ate or fim)
    return _gerar_csv(itens, "estoque_casa")

@router.get("/api/estoque/infra/csv")
async def csv_infra(request: Request, de: str = "", ate: str = ""):
    if not _user(request):
        return JSONResponse({"error": "401"}, status_code=401)
    ini, fim = _datas()
    itens = get_itens("%INFRA%", de or ini, ate or fim)
    return _gerar_csv(itens, "estoque_infra")

def _gerar_csv(itens, nome):
    buf = io.StringIO()
    if itens:
        w = csv.DictWriter(buf, fieldnames=itens[0].keys())
        w.writeheader()
        w.writerows(itens)
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={nome}.csv"}
    )
