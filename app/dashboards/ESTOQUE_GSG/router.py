"""
ESTOQUE_GSG/router.py — Hub Stock completo para GSG
Dashboard, CASA, INFRA, Movimentações, Compras, Projeção
"""
import sqlite3, json, csv, io, logging
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional

BASE_DIR  = Path(__file__).resolve().parent.parent.parent
DB_PATH   = str(BASE_DIR / "gsg_estoque.db")
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "templates"))
log       = logging.getLogger(__name__)
router    = APIRouter()

def get_db():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    try: yield c
    finally: c.close()

def db():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def requer_user(request: Request):
    u = request.session.get("user")
    if not u:
        from fastapi.responses import RedirectResponse
        raise Exception("não autenticado")
    return u

def calcular_dias(saldo, consumo_dia):
    if not consumo_dia or consumo_dia <= 0: return 999
    return int(saldo / consumo_dia)

def status_item(dias, saldo):
    if saldo <= 0:    return "zerado"
    if dias < 10:     return "critico"
    if dias < 20:     return "alerta"
    return "normal"

def get_itens_categoria(cat_like):
    conn = db()
    rows = conn.execute("""
        SELECT p.id_produto, p.descricao, p.categoria, p.unidade,
               COALESCE(p.estoque_minimo,0) as estoque_minimo,
               COALESCE(s.saldo,0) as saldo,
               COALESCE(m.total_saida,0) as saida_periodo
        FROM produtos p
        LEFT JOIN saldos s ON s.id_produto = p.id_produto
        LEFT JOIN consumo_por_ativacao m ON m.id_produto = p.id_produto
        WHERE p.categoria LIKE ? AND p.ativo=1
        ORDER BY p.descricao
    """, (cat_like,)).fetchall()
    conn.close()
    result = []
    for r in rows:
        saldo      = float(r["saldo"])
        saida      = float(r["saida_periodo"])
        consumo    = saida / 90 if saida else 0
        dias       = calcular_dias(saldo, consumo)
        result.append({
            "id_produto":     r["id_produto"],
            "descricao":      r["descricao"],
            "categoria":      r["categoria"],
            "unidade":        r["unidade"] or "un",
            "estoque_minimo": round(float(r["estoque_minimo"]),2),
            "saldo":          round(saldo,2),
            "saida_periodo":  round(saida,2),
            "consumo_dia":    round(consumo,2),
            "dias_cobertura": dias,
            "status":         status_item(dias, saldo),
        })
    return result

def _safe(v):
    if v is None: return None
    if hasattr(v,'__class__') and v.__class__.__name__=='Decimal': return float(v)
    if hasattr(v,'isoformat'): return str(v)
    return v

# ── PÁGINAS HTML ──────────────────────────────────────────────

@router.get("/dashboard/estoque/hub", response_class=HTMLResponse)
async def pg_hub(request: Request):
    u = request.session.get("user")
    if not u: from fastapi.responses import RedirectResponse; return RedirectResponse("/")
    return TEMPLATES.TemplateResponse("dashboards/ESTOQUE_GSG/hub.html", {"request":request,"session":request.session})

@router.get("/dashboard/estoque/casa", response_class=HTMLResponse)
async def pg_casa(request: Request):
    u = request.session.get("user")
    if not u: from fastapi.responses import RedirectResponse; return RedirectResponse("/")
    return TEMPLATES.TemplateResponse("dashboards/ESTOQUE_GSG/casa.html", {"request":request,"session":request.session})

@router.get("/dashboard/estoque/infra", response_class=HTMLResponse)
async def pg_infra(request: Request):
    u = request.session.get("user")
    if not u: from fastapi.responses import RedirectResponse; return RedirectResponse("/")
    return TEMPLATES.TemplateResponse("dashboards/ESTOQUE_GSG/infra.html", {"request":request,"session":request.session})

@router.get("/dashboard/estoque/movimentacoes", response_class=HTMLResponse)
async def pg_movs(request: Request):
    u = request.session.get("user")
    if not u: from fastapi.responses import RedirectResponse; return RedirectResponse("/")
    return TEMPLATES.TemplateResponse("dashboards/ESTOQUE_GSG/movimentacoes.html", {"request":request,"session":request.session})

@router.get("/dashboard/estoque/compras", response_class=HTMLResponse)
async def pg_compras(request: Request):
    u = request.session.get("user")
    if not u: from fastapi.responses import RedirectResponse; return RedirectResponse("/")
    return TEMPLATES.TemplateResponse("dashboards/ESTOQUE_GSG/compras.html", {"request":request,"session":request.session})

@router.get("/dashboard/estoque/projecao", response_class=HTMLResponse)
async def pg_projecao(request: Request):
    u = request.session.get("user")
    if not u: from fastapi.responses import RedirectResponse; return RedirectResponse("/")
    return TEMPLATES.TemplateResponse("dashboards/ESTOQUE_GSG/projecao.html", {"request":request,"session":request.session})

# ── APIs ESTOQUE ──────────────────────────────────────────────

@router.get("/api/estoque/hub/dashboard")
async def api_dashboard(request: Request):
    u = request.session.get("user")
    if not u: return {"erro":"não autenticado"}
    conn = db()
    rows = conn.execute("""
        SELECT p.id_produto, p.descricao, p.categoria, p.unidade,
               COALESCE(s.saldo,0) as saldo,
               COALESCE(m.total_saida,0) as saida_periodo
        FROM produtos p
        LEFT JOIN saldos s ON s.id_produto=p.id_produto
        LEFT JOIN consumo_por_ativacao m ON m.id_produto=p.id_produto
        WHERE p.ativo=1
    """).fetchall()
    ped_row = conn.execute("SELECT COUNT(*) as c FROM pedidos_compra WHERE status='pendente'").fetchone()
    pedidos_pendentes = ped_row["c"] if ped_row else 0
    conn.close()

    criticos=[]; alerta=[]; zerados=[]; top_consumo=[]
    dias_casa=[]; dias_infra=[]
    total_casa=total_infra=0
    dist_casa={"critico":0,"alerta":0,"normal":0,"zerado":0}
    dist_infra={"critico":0,"alerta":0,"normal":0,"zerado":0}

    for r in rows:
        saldo=float(r["saldo"]); saida=float(r["saida_periodo"])
        consumo=saida/90 if saida else 0
        dias=calcular_dias(saldo,consumo)
        cat=(r["categoria"] or "GERAL").upper()
        base={"id_produto":r["id_produto"],"descricao":r["descricao"],
              "categoria":cat,"unidade":r["unidade"],"saldo":round(saldo,2),
              "saida_periodo":round(saida,2),"consumo_dia":round(consumo,2),
              "dias_cobertura":dias,"status":status_item(dias,saldo)}
        dist=dist_casa if cat=="CASA" else dist_infra if cat=="INFRA" else None
        if cat=="CASA": total_casa+=1; dias_casa.append(dias) if dias<999 else None
        elif cat=="INFRA": total_infra+=1; dias_infra.append(dias) if dias<999 else None
        st=status_item(dias,saldo)
        if dist: dist[st]+=1 if st in dist else None
        if saldo<=0: zerados.append(base)
        elif dias<10: criticos.append(base)
        elif dias<20: alerta.append(base)
        if saida>0: top_consumo.append(base)

    top_consumo=sorted(top_consumo,key=lambda x:x["saida_periodo"],reverse=True)[:10]
    criticos=sorted(criticos,key=lambda x:x["dias_cobertura"])
    alerta=sorted(alerta,key=lambda x:x["dias_cobertura"])
    cob_casa=int(sum(dias_casa)/len(dias_casa)) if dias_casa else 0
    cob_infra=int(sum(dias_infra)/len(dias_infra)) if dias_infra else 0

    return {"resumo":{
        "cobertura_casa":cob_casa,"cobertura_infra":cob_infra,
        "itens_criticos":criticos,"itens_alerta":alerta,"itens_zerados":zerados,
        "pedidos_pendentes":pedidos_pendentes,"total_produtos":len(rows),
        "total_casa":total_casa,"total_infra":total_infra,
        "top_consumo":top_consumo,"dist_casa":dist_casa,"dist_infra":dist_infra,
    }}

@router.get("/api/estoque/hub/casa")
async def api_casa(request: Request, filtro: str = ""):
    u = request.session.get("user")
    if not u: return {"erro":"não autenticado"}
    itens = get_itens_categoria("%CASA%")
    if filtro: itens = [i for i in itens if filtro in i["status"]]
    return {"itens": itens, "total": len(itens)}

@router.get("/api/estoque/hub/infra")
async def api_infra(request: Request, filtro: str = ""):
    u = request.session.get("user")
    if not u: return {"erro":"não autenticado"}
    itens = get_itens_categoria("%INFRA%")
    if filtro: itens = [i for i in itens if filtro in i["status"]]
    return {"itens": itens, "total": len(itens)}

@router.get("/api/estoque/hub/movimentacoes")
async def api_movimentacoes(request: Request, de: str="", ate: str=""):
    u = request.session.get("user")
    if not u: return {"erro":"não autenticado"}
    conn = db()
    q = "SELECT m.*, p.descricao, p.categoria FROM movimentacoes m LEFT JOIN produtos p ON p.id_produto=m.id_produto WHERE 1=1"
    params = []
    if de:  q+=" AND m.data>=?"; params.append(de)
    if ate: q+=" AND m.data<=?"; params.append(ate)
    q+=" ORDER BY m.id DESC LIMIT 300"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return {"movimentacoes":[dict(r) for r in rows]}

@router.get("/api/estoque/hub/sugestao-compra")
async def api_sugestao(request: Request):
    u = request.session.get("user")
    if not u: return {"erro":"não autenticado"}
    conn = db()
    rows = conn.execute("""
        SELECT p.id_produto, p.descricao, p.categoria, p.unidade,
               COALESCE(s.saldo,0) as saldo,
               COALESCE(m.total_saida,0) as saida_periodo
        FROM produtos p
        LEFT JOIN saldos s ON s.id_produto=p.id_produto
        INNER JOIN consumo_por_ativacao m ON m.id_produto=p.id_produto
        WHERE m.total_saida>0 AND p.ativo=1
    """).fetchall()
    conn.close()
    result=[]
    for r in rows:
        saldo=float(r["saldo"]); saida=float(r["saida_periodo"])
        consumo=saida/90 if saida else 0
        dias=calcular_dias(saldo,consumo)
        if dias<30:
            qtd_sug=max(20,int(consumo*30*2-saldo))
            result.append({"id_produto":r["id_produto"],"descricao":r["descricao"],
                "categoria":r["categoria"],"unidade":r["unidade"],"saldo":round(saldo,2),
                "consumo_dia":round(consumo,2),"dias_cobertura":dias,"qtd_sugerida":qtd_sug,
                "status":status_item(dias,saldo)})
    return {"itens":sorted(result,key=lambda x:x["dias_cobertura"])}

@router.get("/api/estoque/hub/projecao")
async def api_projecao(request: Request, ativacoes: int = 100):
    u = request.session.get("user")
    if not u: return {"erro":"não autenticado"}
    conn = db()
    rows = conn.execute("""
        SELECT p.id_produto, p.descricao, p.categoria, p.unidade,
               COALESCE(s.saldo,0) as saldo,
               COALESCE(m.total_saida,0) as saida_90dias,
               COALESCE(m.media_por_os,0) as media_por_os
        FROM produtos p
        LEFT JOIN saldos s ON s.id_produto=p.id_produto
        LEFT JOIN consumo_por_ativacao m ON m.id_produto=p.id_produto
        WHERE s.saldo>0 AND p.ativo=1
        ORDER BY p.descricao
    """).fetchall()
    conn.close()
    result=[]
    for r in rows:
        saldo=float(r["saldo"]); saida=float(r["saida_90dias"])
        consumo=saida/90 if saida else 0
        dias=calcular_dias(saldo,consumo)
        media=float(r["media_por_os"])
        necessario=round(media*ativacoes,2) if media>0 else 0
        a_comprar=max(0,round(necessario-saldo,2))
        result.append({"id_produto":r["id_produto"],"descricao":r["descricao"],
            "categoria":r["categoria"],"unidade":r["unidade"],"saldo":round(saldo,2),
            "consumo_dia":round(consumo,2),"dias_cobertura":dias,
            "necessario":necessario,"a_comprar":a_comprar})
    return {"itens":sorted(result,key=lambda x:x["dias_cobertura"]),"ativacoes":ativacoes}

@router.get("/api/estoque/hub/fornecedores")
async def api_fornecedores(request: Request):
    u = request.session.get("user")
    if not u: return {"erro":"não autenticado"}
    try:
        from app.core.ixc_db_gsg import ixc_select
        rows = ixc_select("SELECT id, razao, fantasia FROM ixcprovedor.fornecedor WHERE ativo='S' ORDER BY razao")
        return {"fornecedores":[{"id":r["id"],"nome":r["fantasia"] or r["razao"]} for r in rows]}
    except Exception as e:
        return {"fornecedores":[],"erro":str(e)}

@router.get("/api/estoque/hub/condicoes")
async def api_condicoes(request: Request):
    u = request.session.get("user")
    if not u: return {"erro":"não autenticado"}
    try:
        from app.core.ixc_db_gsg import ixc_select
        rows = ixc_select("SELECT id, nome FROM ixcprovedor.condicoes_pagamento WHERE ativo='S' AND compra_venda IN ('A','C') ORDER BY nome")
        return {"condicoes":[dict(r) for r in rows]}
    except Exception as e:
        return {"condicoes":[],"erro":str(e)}

class PedidoIXCBody(BaseModel):
    itens: List[str]
    id_fornecedor: int
    id_condicao: int
    obs: Optional[str] = ""

@router.post("/api/estoque/hub/pedido-ixc")
async def api_criar_pedido(request: Request, body: PedidoIXCBody):
    u = request.session.get("user")
    if not u: return {"erro":"não autenticado"}
    conn_local = db()
    c_local    = conn_local.cursor()
    itens_data = []
    for pid in body.itens:
        p = c_local.execute("""
            SELECT p.id_produto, p.descricao, p.unidade, COALESCE(s.saldo,0) as saldo,
                   COALESCE(m.total_saida,0)/90.0 as consumo_dia
            FROM produtos p LEFT JOIN saldos s ON s.id_produto=p.id_produto
            LEFT JOIN consumo_por_ativacao m ON m.id_produto=p.id_produto
            WHERE p.id_produto=?
        """, (pid,)).fetchone()
        if p:
            consumo=float(p["consumo_dia"] or 0)
            qtd_sug=max(20,int(consumo*60-float(p["saldo"])))
            itens_data.append({"id_produto":pid,"descricao":p["descricao"],
                "unidade":p["unidade"] or "un","qtd":qtd_sug,"saldo":float(p["saldo"])})
    if not itens_data:
        conn_local.close(); return {"erro":"Nenhum produto válido"}
    hoje=datetime.now().strftime("%Y-%m-%d")
    try:
        from app.core.ixc_db_gsg import ixc_conn, ixc_select_one
        with ixc_conn() as conn_ixc:
            cur=conn_ixc.cursor()
            cur.execute("""
                INSERT INTO ixcprovedor.pedido_compra
                    (data,id_fornecedor,id_condicoes_pagamento,previsao_faturamento,
                     previsao_entrega,status,filial_id,id_modelo,valor_negociado,
                     obs,status_liberado,tipo_frete,valor_frete,tipo_desconto,valor_desconto)
                VALUES(%s,%s,%s,%s,%s,'A',1,1,0,%s,'N','S',0,'V',0)
            """, (hoje,body.id_fornecedor,body.id_condicao,hoje,hoje,body.obs or "Gerado pelo HubEstoque GSG"))
            conn_ixc.commit()
            cur.execute("SELECT MAX(id) as id FROM ixcprovedor.pedido_compra")
            ixc_id=cur.fetchone()["id"]
            for it in itens_data:
                cur.execute("""
                    SELECT COALESCE(NULLIF(custo,0),valor_unitario,0) as preco
                    FROM ixcprovedor.movimento_produtos
                    WHERE id_produto=%s AND COALESCE(NULLIF(custo,0),valor_unitario,0)>0
                    ORDER BY data DESC LIMIT 1
                """, (int(it["id_produto"]),))
                pr=cur.fetchone(); preco=float(pr["preco"]) if pr else 0.0
                vt=round(preco*it["qtd"],2); it["preco"]=preco
                cur.execute("""
                    INSERT INTO ixcprovedor.pedido_compra_itens
                        (id_produto,id_unidade,quantidade,valor_unitario,valor_total,
                         id_pedido_compra,status,tipo,filial_id,unidade_sigla,observacao)
                    VALUES(%s,1,%s,%s,%s,%s,'A','E',1,%s,'')
                """, (int(it["id_produto"]),it["qtd"],preco,vt,ixc_id,it["unidade"]))
            conn_ixc.commit()
        criado_por=u.get("nome","master")
        c_local.execute("""
            INSERT INTO pedidos_compra(itens,status,criado_por,criado_em)
            VALUES(?,'enviado_ixc',?,datetime('now','-3 hours'))
        """, (json.dumps([i["id_produto"] for i in itens_data]),criado_por))
        conn_local.commit(); conn_local.close()
        # Telegram
        try:
            import os, requests as req
            token=os.getenv("TELEGRAM_TOKEN"); chat=os.getenv("TELEGRAM_AILTON")
            if token and chat:
                val_total=sum(i.get("preco",0)*i["qtd"] for i in itens_data)
                msg=f"🛒 Pedido Compra GSG #{ixc_id}\nCriado por: {criado_por}\nItens: {len(itens_data)}\nValor total: R$ {val_total:.2f}"
                req.post(f"https://api.telegram.org/bot{token}/sendMessage",
                    json={"chat_id":chat,"text":msg},timeout=5)
        except: pass
        return {"ok":True,"id_ixc":ixc_id,"msg":f"Pedido #{ixc_id} criado no IXC com {len(itens_data)} itens!"}
    except Exception as e:
        conn_local.close(); log.error(f"pedido_ixc: {e}"); return {"erro":str(e)}

@router.post("/api/estoque/hub/sync")
async def api_sync(request: Request):
    u = request.session.get("user")
    if not u or u.get("nivel")!=99: return {"erro":"sem permissão"}
    try:
        import subprocess, sys
        r=subprocess.run([f"{BASE_DIR}/venv/bin/python3",
            str(BASE_DIR/"app"/"core"/"sync_estoque_gsg.py")],
            capture_output=True,text=True,timeout=60,cwd=str(BASE_DIR))
        return {"ok":True,"msg":r.stdout.strip().split("\n")[-1]}
    except Exception as e:
        return {"ok":False,"erro":str(e)}

@router.post("/api/estoque/hub/estoque-minimo")
async def api_estoque_minimo(request: Request):
    u = request.session.get("user")
    if not u: return {"erro":"não autenticado"}
    body = await request.json()
    conn=db()
    conn.execute("UPDATE produtos SET estoque_minimo=? WHERE id_produto=?",(body["estoque_minimo"],body["id_produto"]))
    conn.commit(); conn.close()
    return {"ok":True}
