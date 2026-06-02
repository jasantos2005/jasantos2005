"""
badges_api.py — Contadores para badges do menu lateral
"""
import sqlite3, logging
from pathlib import Path
from fastapi import APIRouter, Request

BASE_DIR  = Path(__file__).resolve().parent.parent
DB_EST    = str(BASE_DIR / "gsg_estoque.db")
log       = logging.getLogger(__name__)
router    = APIRouter()

def _est_db():
    c = sqlite3.connect(DB_EST, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

@router.get("/api/badges")
async def api_badges(request: Request):
    u = request.session.get("user")
    if not u: return {"erro": "não autenticado"}

    badges = {}

    # Estoque — itens críticos
    try:
        conn = _est_db()
        rows = conn.execute("""
            SELECT COUNT(*) as n FROM (
                SELECT p.id_produto,
                       COALESCE(s.saldo,0) as saldo,
                       COALESCE(m.total_saida,0)/90.0 as consumo_dia
                FROM produtos p
                LEFT JOIN saldos s ON s.id_produto=p.id_produto
                LEFT JOIN consumo_por_ativacao m ON m.id_produto=p.id_produto
                WHERE p.ativo=1 AND p.categoria IN ('CASA','INFRA')
                  AND COALESCE(m.total_saida,0) > 0
            ) t WHERE (saldo <= 0) OR (consumo_dia > 0 AND CAST(saldo/consumo_dia AS INTEGER) < 10)
        """).fetchone()
        badges["estoque_criticos"] = int(rows["n"] or 0)
        conn.close()
    except Exception as e:
        badges["estoque_criticos"] = 0

    # Pedidos pendentes
    try:
        conn = _est_db()
        rows = conn.execute("SELECT COUNT(*) as n FROM pedidos_compra WHERE status='pendente'").fetchone()
        badges["pedidos_pendentes"] = int(rows["n"] or 0)
        conn.close()
    except:
        badges["pedidos_pendentes"] = 0

    # Financeiro — inadimplentes (via IXC)
    try:
        from app.core.ixc_db_gsg import ixc_select_one
        r = ixc_select_one("""
            SELECT COUNT(DISTINCT cc.id) as n
            FROM ixcprovedor.cliente_contrato cc
            JOIN ixcprovedor.fn_areceber f ON f.id_contrato=cc.id
            WHERE cc.status='A' AND f.status='A'
              AND f.data_vencimento < CURDATE()
              AND DATEDIFF(CURDATE(), f.data_vencimento) > 30
        """)
        badges["inadimplentes"] = int(r["n"] or 0) if r else 0
    except:
        badges["inadimplentes"] = 0

    return badges
