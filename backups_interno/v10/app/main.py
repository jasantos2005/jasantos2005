import sys
import os
from datetime import datetime
import sqlite3
import uvicorn

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from app.admin.service import AdminService
from app.dashboards.FIN_REC.router import router as fin_rec_router
from app.dashboards.FIN_PAG.router import router as fin_pag_router
from app.dashboards.FIN_CONSOLIDADO.router import router as fin_cons_router
from app.dashboards.COMERCIAL.router import router as comercial_router
from app.dashboards.TECNICO.router import router as tecnico_router
try:
    from app.admin.router import router as admin_router
except:
    admin_router = None

app = FastAPI(title="Axiom Core - Intelligence System")
admin_service = AdminService()
BASE_DIR = "/opt/automacoes/GSG/gestao/diretoria/dashboards/app"
DB_PATH = os.path.join(BASE_DIR, "axiom_core.db")

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.add_middleware(SessionMiddleware, secret_key="axiom_governance_secure_key_ailton")

def buscar_usuario_no_banco(login, senha):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        query = "SELECT id, nome, nivel_acesso, setor, permissao_dash FROM usuarios WHERE login = ? AND senha_hash = ?"
        cur.execute(query, (login, senha))
        user = cur.fetchone()
        conn.close()
        return user
    except Exception as e:
        print(f"Erro de Banco: {e}")
        return None

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.post("/auth/login")
async def acao_autenticar(request: Request, username: str = Form(...), password: str = Form(...)):
    user_data = buscar_usuario_no_banco(username, password)
    if user_data:
        request.session["user"] = {
            "id": user_data["id"], "nome": user_data["nome"],
            "nivel": int(user_data["nivel_acesso"]), "setor": user_data["setor"],
            "permissao": user_data["permissao_dash"] or ""
        }
        admin_service.registrar_acao(user_data["nome"], "Realizou login no sistema", "success")
        return RedirectResponse(url="/dashboard/home", status_code=303) if int(user_data["nivel_acesso"]) != 99 else RedirectResponse(url="/portal", status_code=303)
    return RedirectResponse(url="/?error=1", status_code=303)

@app.get("/auth/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

# --- ROTAS DE DASHBOARDS ---

@app.get("/dashboard/home", response_class=HTMLResponse)
async def rota_home(request: Request):
    user = request.session.get("user")
    if not user: return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request, "session": request.session})

@app.get("/dashboard/financeiro", response_class=HTMLResponse)
async def rota_dash_financeiro(request: Request):
    user = request.session.get("user")
    if not user or ("FIN_REC" not in user["permissao"] and user["nivel"] != 99):
        return RedirectResponse(url="/dashboard/home?error=sem_permissao", status_code=303)
    admin_service.registrar_acao(user["nome"], "Acessou Dashboard: Contas a Receber", "info")
    return templates.TemplateResponse("dashboards/FIN_REC/index.html", {"request": request, "session": request.session})

@app.get("/dashboard/pagar", response_class=HTMLResponse)
async def dashboard_pagar(request: Request):
    user = request.session.get("user")
    if not user or ("FIN_PAG" not in user["permissao"] and user["nivel"] != 99):
        return RedirectResponse(url="/dashboard/home?error=sem_permissao", status_code=303)
    admin_service.registrar_acao(user["nome"], "Acessou Dashboard: Contas a Pagar", "info")
    return templates.TemplateResponse("dashboards/FIN_PAG/index.html", {"request": request, "session": request.session})

@app.get("/dashboard/visao_geral", response_class=HTMLResponse)
async def dashboard_consolidado(request: Request):
    user = request.session.get("user")
    if not user or ("FIN_CON" not in user["permissao"] and user["nivel"] != 99):
        return RedirectResponse(url="/dashboard/home?error=sem_permissao", status_code=303)
    admin_service.registrar_acao(user["nome"], "Acessou Dashboard: Visão Geral", "info")
    return templates.TemplateResponse("dashboards/FIN_CONSOLIDADO/index.html", {"request": request, "session": request.session})

# --- REGISTRO DE APIS ---
app.include_router(fin_rec_router, prefix="/api/financeiro", tags=["financeiro"])
app.include_router(fin_pag_router, tags=["financeiro_pagar"])
app.include_router(fin_cons_router, tags=["financeiro_consolidado"])
app.include_router(comercial_router)
app.include_router(tecnico_router)

if admin_router:
    app.include_router(admin_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
