"""
COMERCIAL_GSG/router.py
Ranking de vendedores, metas, painel TV e inadimplentes por vendedor.
Dados direto do IXC via ixc_db_gsg.
"""
import sqlite3, logging, os
from datetime import date, timedelta
from pathlib import Path
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

BASE_DIR   = Path(__file__).resolve().parent.parent.parent
DB_COM     = str(BASE_DIR / "gsg_comercial.db")
TEMPLATES  = Jinja2Templates(directory=str(BASE_DIR / "templates"))
log        = logging.getLogger(__name__)
router     = APIRouter()

def get_db():
    c = sqlite3.connect(DB_COM, check_same_thread=False)
    c.row_factory = sqlite3.Row
    try: yield c
    finally: c.close()

def _requer_usuario(request: Request):
    user = request.session.get("user")
    if not user:
        from fastapi.responses import RedirectResponse
        return None
    return user

def _hoje(): return date.today().strftime("%Y-%m-%d")
def _mes():  return date.today().replace(day=1).strftime("%Y-%m-%d")

def _safe(v):
    if v is None: return None
    if hasattr(v, '__class__') and v.__class__.__name__ == 'Decimal': return float(v)
    if hasattr(v, 'isoformat'): return str(v)
    return v

# ── PÁGINAS HTML ──────────────────────────────────────────────

@router.get("/dashboard/comercial/ranking", response_class=HTMLResponse)
async def pg_ranking(request: Request):
    user = request.session.get("user")
    if not user: from fastapi.responses import RedirectResponse; return RedirectResponse("/")
    return TEMPLATES.TemplateResponse("dashboards/COMERCIAL_GSG/ranking.html",
                                      {"request": request, "session": request.session})

@router.get("/dashboard/comercial/metas", response_class=HTMLResponse)
async def pg_metas(request: Request):
    user = request.session.get("user")
    if not user: from fastapi.responses import RedirectResponse; return RedirectResponse("/")
    return TEMPLATES.TemplateResponse("dashboards/COMERCIAL_GSG/metas.html",
                                      {"request": request, "session": request.session})

@router.get("/dashboard/comercial/painel-tv", response_class=HTMLResponse)
async def pg_tv(request: Request):
    user = request.session.get("user")
    if not user: from fastapi.responses import RedirectResponse; return RedirectResponse("/")
    return TEMPLATES.TemplateResponse("dashboards/COMERCIAL_GSG/painel_tv.html",
                                      {"request": request, "session": request.session})

@router.get("/dashboard/comercial/inadimplentes", response_class=HTMLResponse)
async def pg_inadimplentes(request: Request):
    user = request.session.get("user")
    if not user: from fastapi.responses import RedirectResponse; return RedirectResponse("/")
    return TEMPLATES.TemplateResponse("dashboards/COMERCIAL_GSG/inadimplentes.html",
                                      {"request": request, "session": request.session})

# ── APIs ──────────────────────────────────────────────────────

@router.get("/api/comercial/ranking")
async def api_ranking(request: Request, periodo: str = "mes"):
    user = request.session.get("user")
    if not user: return {"erro": "não autenticado"}
    datas = {
        "hoje":      _hoje(),
        "mes":       _mes(),
        "trimestre": (date.today() - timedelta(days=90)).strftime("%Y-%m-%d"),
    }
    inicio = datas.get(periodo, _mes())
    try:
        from app.core.ixc_db_gsg import ixc_conn
        with ixc_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT v.id, v.nome,
                       COUNT(DISTINCT cc.id) AS total,
                       SUM(cc.status_internet='A')  AS ativados,
                       SUM(cc.status_internet='AA') AS aguard_assinatura,
                       SUM(cc.status='C')            AS cancelados
                FROM ixcprovedor.vendedor v
                JOIN ixcprovedor.cliente_contrato cc ON cc.id_vendedor_ativ = v.id
                WHERE cc.data >= %s AND cc.id_vendedor_ativ > 0
                  AND cc.id_vendedor_ativ != 29
                GROUP BY v.id, v.nome
                ORDER BY ativados DESC, total DESC
                LIMIT 20
            """, (inicio,))
            rows = cur.fetchall()
        return {
            "periodo": periodo,
            "inicio": inicio,
            "vendedores": [{k: _safe(val) for k, val in dict(r).items()} for r in rows]
        }
    except Exception as e:
        log.error(f"ranking: {e}")
        return {"vendedores": [], "erro": str(e)}


@router.get("/api/comercial/metas")
async def api_metas(request: Request, mes: str = ""):
    user = request.session.get("user")
    if not user: return {"erro": "não autenticado"}
    if not mes: mes = date.today().strftime("%Y-%m")
    inicio = f"{mes}-01"
    try:
        db = sqlite3.connect(DB_COM); db.row_factory = sqlite3.Row
        metas_rows = db.execute("SELECT vendedor_id, meta FROM gsg_metas WHERE mes=?", (mes,)).fetchall()
        metas_map = {r["vendedor_id"]: r["meta"] for r in metas_rows}
        db.close()

        from app.core.ixc_db_gsg import ixc_conn
        with ixc_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT v.id, v.nome,
                       COUNT(DISTINCT cc.id) AS ativados
                FROM ixcprovedor.vendedor v
                LEFT JOIN ixcprovedor.cliente_contrato cc
                    ON cc.id_vendedor_ativ = v.id
                    AND cc.data >= %s
                    AND cc.status_internet = 'A'
                WHERE v.id > 0 AND v.id != 29
                GROUP BY v.id, v.nome
                ORDER BY ativados DESC
            """, (inicio,))
            rows = cur.fetchall()

        resultado = []
        for r in rows:
            ativ = int(r["ativados"] or 0)
            meta = metas_map.get(r["id"], 0)
            pct  = round(ativ / max(meta, 1) * 100, 1) if meta > 0 else 0
            resultado.append({
                "id": r["id"], "nome": r["nome"],
                "ativados": ativ, "meta": meta, "percentual": pct
            })
        return {"mes": mes, "vendedores": resultado}
    except Exception as e:
        log.error(f"metas: {e}")
        return {"vendedores": [], "erro": str(e)}


@router.post("/api/comercial/metas/salvar")
async def api_salvar_meta(request: Request):
    user = request.session.get("user")
    if not user or user.get("nivel") != 99:
        return {"erro": "sem permissão"}
    body = await request.json()
    vendedor_id = body.get("vendedor_id")
    mes = body.get("mes")
    meta = int(body.get("meta", 0))
    db = sqlite3.connect(DB_COM)
    db.execute("""
        INSERT INTO gsg_metas(vendedor_id, mes, meta) VALUES(?,?,?)
        ON CONFLICT(vendedor_id, mes) DO UPDATE SET meta=excluded.meta
    """, (vendedor_id, mes, meta))
    db.commit(); db.close()
    return {"ok": True}


@router.get("/api/comercial/painel-tv")
async def api_painel_tv(request: Request):
    user = request.session.get("user")
    if not user: return {"erro": "não autenticado"}
    hoje = _hoje()
    try:
        from app.core.ixc_db_gsg import ixc_conn
        with ixc_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    COUNT(*) AS total,
                    SUM(cc.status_internet='A')  AS ativados,
                    SUM(cc.status_internet='AA') AS aguard_assinatura,
                    SUM(cc.status='P')           AS pendentes
                FROM ixcprovedor.cliente_contrato cc
                WHERE cc.data >= %s
                  AND cc.id_vendedor_ativ > 0
                  AND cc.id_vendedor_ativ != 29
            """, (hoje,))
            totais = cur.fetchone()

            cur.execute("""
                SELECT c.razao, v.nome AS vendedor,
                       cc.data AS data_cadastro,
                       cc.status_internet,
                       o.data_fechamento AS data_instalacao,
                       f.funcionario AS tecnico
                FROM ixcprovedor.cliente_contrato cc
                JOIN ixcprovedor.cliente c ON c.id = cc.id_cliente
                LEFT JOIN ixcprovedor.vendedor v ON v.id = cc.id_vendedor_ativ
                LEFT JOIN ixcprovedor.su_oss_chamado o
                    ON o.id_contrato_kit = cc.id
                    AND o.id_assunto IN (227,110,75,15)
                LEFT JOIN ixcprovedor.funcionarios f ON f.id = o.id_tecnico
                WHERE cc.data >= %s
                  AND cc.id_vendedor_ativ > 0
                  AND cc.id_vendedor_ativ != 29
                ORDER BY cc.id DESC LIMIT 15
            """, (hoje,))
            atividades = cur.fetchall()

        def fmt(r):
            d = {}
            for k, val in dict(r).items():
                d[k] = _safe(val)
            return d

        return {
            "totais": {
                "total":             int(totais["total"] or 0),
                "ativados":          int(totais["ativados"] or 0),
                "aguard_assinatura": int(totais["aguard_assinatura"] or 0),
                "pendentes":         int(totais["pendentes"] or 0),
            },
            "atividades": [fmt(r) for r in atividades],
        }
    except Exception as e:
        log.error(f"painel-tv: {e}")
        return {"totais": {"total":0,"ativados":0,"aguard_assinatura":0,"pendentes":0}, "atividades": []}


@router.get("/api/comercial/inadimplentes")
async def api_inadimplentes(request: Request, dias_min: int = 1):
    user = request.session.get("user")
    if not user: return {"erro": "não autenticado"}
    try:
        from app.core.ixc_db_gsg import ixc_conn
        with ixc_conn() as conn:
            cur = conn.cursor()
            cur.execute(f"""
                SELECT v.nome AS vendedor,
                       c.razao, c.telefone_celular,
                       ci.nome AS cidade,
                       vc.nome AS plano,
                       MAX(DATEDIFF(CURDATE(), f.data_vencimento)) AS dias_atraso,
                       SUM(f.valor_aberto) AS valor_total,
                       cc.id_vendedor_ativ AS vendedor_id
                FROM ixcprovedor.cliente_contrato cc
                JOIN ixcprovedor.cliente c ON c.id = cc.id_cliente
                LEFT JOIN ixcprovedor.cidade ci ON ci.id = c.cidade
                LEFT JOIN ixcprovedor.vd_contratos vc ON vc.id = cc.id_vd_contrato
                LEFT JOIN ixcprovedor.vendedor v ON v.id = cc.id_vendedor_ativ
                JOIN ixcprovedor.fn_areceber f
                    ON f.id_contrato = cc.id
                    AND f.status = 'A'
                    AND f.data_vencimento < CURDATE()
                WHERE cc.status = 'A'
                  AND cc.id_vendedor_ativ > 0
                  AND cc.id_vendedor_ativ != 29
                GROUP BY cc.id
                HAVING dias_atraso >= {dias_min}
                ORDER BY dias_atraso DESC
                LIMIT 200
            """)
            rows = cur.fetchall()
        return {"inadimplentes": [{k: _safe(val) for k, val in dict(r).items()} for r in rows]}
    except Exception as e:
        log.error(f"inadimplentes: {e}")
        return {"inadimplentes": [], "erro": str(e)}
