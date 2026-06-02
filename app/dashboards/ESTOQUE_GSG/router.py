"""
ESTOQUE_GSG/router.py
Estoque principal, estoque por técnico, requisições e auditoria IXC.
"""
import sqlite3, logging
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

BASE_DIR   = Path(__file__).resolve().parent.parent.parent
DB_EST     = str(BASE_DIR / "gsg_estoque.db")
TEMPLATES  = Jinja2Templates(directory=str(BASE_DIR / "templates"))
log        = logging.getLogger(__name__)
router     = APIRouter()

def get_db():
    c = sqlite3.connect(DB_EST, check_same_thread=False)
    c.row_factory = sqlite3.Row
    try: yield c
    finally: c.close()

def brt():
    from datetime import timezone, timedelta
    return (datetime.now(timezone.utc) - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")

def _safe(v):
    if v is None: return None
    if hasattr(v, '__class__') and v.__class__.__name__ == 'Decimal': return float(v)
    if hasattr(v, 'isoformat'): return str(v)
    return v

# ── PÁGINAS HTML ──────────────────────────────────────────────

@router.get("/dashboard/estoque/principal", response_class=HTMLResponse)
async def pg_estoque_principal(request: Request):
    user = request.session.get("user")
    if not user: from fastapi.responses import RedirectResponse; return RedirectResponse("/")
    return TEMPLATES.TemplateResponse("dashboards/ESTOQUE_GSG/principal.html",
                                      {"request": request, "session": request.session})

@router.get("/dashboard/estoque/tecnicos", response_class=HTMLResponse)
async def pg_estoque_tecnicos(request: Request):
    user = request.session.get("user")
    if not user: from fastapi.responses import RedirectResponse; return RedirectResponse("/")
    return TEMPLATES.TemplateResponse("dashboards/ESTOQUE_GSG/tecnicos.html",
                                      {"request": request, "session": request.session})

@router.get("/dashboard/estoque/requisicoes", response_class=HTMLResponse)
async def pg_requisicoes(request: Request):
    user = request.session.get("user")
    if not user: from fastapi.responses import RedirectResponse; return RedirectResponse("/")
    return TEMPLATES.TemplateResponse("dashboards/ESTOQUE_GSG/requisicoes.html",
                                      {"request": request, "session": request.session})

@router.get("/dashboard/estoque/auditoria", response_class=HTMLResponse)
async def pg_auditoria(request: Request):
    user = request.session.get("user")
    if not user: from fastapi.responses import RedirectResponse; return RedirectResponse("/")
    return TEMPLATES.TemplateResponse("dashboards/ESTOQUE_GSG/auditoria.html",
                                      {"request": request, "session": request.session})

# ── APIs ──────────────────────────────────────────────────────

@router.get("/api/estoque/principal")
async def api_estoque_principal(request: Request):
    user = request.session.get("user")
    if not user: return {"erro": "não autenticado"}
    try:
        from app.core.ixc_db_gsg import ixc_select
        rows = ixc_select("""
            SELECT p.id, p.descricao AS nome, p.unidade,
                   SUM(e.saldo) AS saldo
            FROM ixcprovedor.estoque_produtos_almox_filial e
            JOIN ixcprovedor.produtos p ON p.id = e.id_produto
            WHERE e.id_almox = 1 AND e.produto_ativo = 'S'
            GROUP BY p.id, p.descricao, p.unidade
            HAVING saldo > 0
            ORDER BY p.descricao
        """)
        return {"produtos": [{k: _safe(val) for k, val in dict(r).items()} for r in rows]}
    except Exception as e:
        log.error(f"estoque_principal: {e}")
        return {"produtos": [], "erro": str(e)}


@router.get("/api/estoque/tecnicos")
async def api_estoque_tecnicos(request: Request):
    user = request.session.get("user")
    if not user: return {"erro": "não autenticado"}
    try:
        from app.core.ixc_db_gsg import ixc_select
        almoxs = ixc_select("""
            SELECT a.id, a.descricao AS nome,
                   f.funcionario AS tecnico
            FROM ixcprovedor.almoxarifado a
            LEFT JOIN ixcprovedor.funcionarios f ON f.id_almoxarifado = a.id
            WHERE a.id != 1 AND a.ativo = 'S'
            ORDER BY a.descricao
        """)

        resultado = []
        for almox in almoxs:
            saldos = ixc_select("""
                SELECT p.id, p.descricao AS nome, p.unidade,
                       SUM(e.saldo) AS saldo
                FROM ixcprovedor.estoque_produtos_almox_filial e
                JOIN ixcprovedor.produtos p ON p.id = e.id_produto
                WHERE e.id_almox = %s AND e.produto_ativo = 'S'
                GROUP BY p.id, p.descricao, p.unidade
                HAVING saldo > 0
                ORDER BY p.descricao
            """, (almox["id"],))
            resultado.append({
                "almox_id":   almox["id"],
                "almox_nome": almox["nome"],
                "tecnico":    almox["tecnico"],
                "produtos":   [{k: _safe(val) for k, val in dict(s).items()} for s in saldos],
                "total_itens": len(saldos),
            })
        return {"tecnicos": resultado}
    except Exception as e:
        log.error(f"estoque_tecnicos: {e}")
        return {"tecnicos": [], "erro": str(e)}


@router.get("/api/estoque/requisicoes")
async def api_requisicoes(request: Request):
    user = request.session.get("user")
    if not user: return {"erro": "não autenticado"}
    db = sqlite3.connect(DB_EST); db.row_factory = sqlite3.Row
    rows = db.execute("""
        SELECT r.*, t.nome AS tecnico_nome
        FROM gsg_requisicoes r
        LEFT JOIN gsg_tecnicos_estoque t ON t.id = r.id_tecnico
        ORDER BY r.criada_em DESC LIMIT 50
    """).fetchall()
    resultado = []
    for r in rows:
        itens = db.execute("""
            SELECT ri.*, p.nome AS produto_nome, p.unidade
            FROM gsg_requisicao_itens ri
            LEFT JOIN gsg_produtos p ON p.id = ri.id_produto
            WHERE ri.id_requisicao = ?
        """, (r["id"],)).fetchall()
        resultado.append({**dict(r), "itens": [dict(i) for i in itens]})
    db.close()
    return {"requisicoes": resultado}


@router.post("/api/estoque/sync")
async def api_sync_estoque(request: Request):
    user = request.session.get("user")
    if not user or user.get("nivel") != 99:
        return {"erro": "sem permissão"}
    try:
        from app.core.ixc_db_gsg import ixc_select
        db = sqlite3.connect(DB_EST); db.row_factory = sqlite3.Row

        saldos = ixc_select("""
            SELECT p.id AS ixc_id, p.descricao AS nome,
                   p.unidade, p.tipo,
                   SUM(e.saldo) AS saldo
            FROM ixcprovedor.estoque_produtos_almox_filial e
            JOIN ixcprovedor.produtos p ON p.id = e.id_produto
            WHERE e.id_almox = 1 AND e.produto_ativo = 'S'
            GROUP BY p.id, p.descricao, p.unidade, p.tipo
            HAVING saldo > 0
        """)
        total = 0
        for s in saldos:
            db.execute("""
                INSERT INTO gsg_produtos(ixc_produto_id, nome, unidade, tipo)
                VALUES(?,?,?,?)
                ON CONFLICT(ixc_produto_id) DO UPDATE SET nome=excluded.nome
            """, (s["ixc_id"], s["nome"], s["unidade"] or "un", s["tipo"] or "O"))
            prod = db.execute("SELECT id FROM gsg_produtos WHERE ixc_produto_id=?", (s["ixc_id"],)).fetchone()
            if prod:
                db.execute("""
                    INSERT INTO gsg_estoque_principal(id_produto, quantidade, ultima_atualizacao)
                    VALUES(?,?,?)
                    ON CONFLICT(id_produto) DO UPDATE SET
                        quantidade=excluded.quantidade,
                        ultima_atualizacao=excluded.ultima_atualizacao
                """, (prod["id"], float(s["saldo"]), brt()))
                total += 1
        db.commit(); db.close()
        return {"ok": True, "msg": f"Sync concluído — {total} produtos atualizados", "total": total}
    except Exception as e:
        log.error(f"sync_estoque: {e}")
        return {"ok": False, "erro": str(e)}


@router.get("/api/estoque/auditoria")
async def api_auditoria(request: Request):
    user = request.session.get("user")
    if not user: return {"erro": "não autenticado"}
    db = sqlite3.connect(DB_EST); db.row_factory = sqlite3.Row
    logs = db.execute("""
        SELECT * FROM gsg_auditoria_log
        ORDER BY criado_em DESC LIMIT 30
    """).fetchall()
    db.close()
    return {"logs": [dict(r) for r in logs]}
