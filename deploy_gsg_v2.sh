#!/bin/bash
# ═══════════════════════════════════════════════════
#  GSG HUB GERENCIAL — DEPLOY COMPLETO v2.0
#  Executa: layout + home + login + portal
# ═══════════════════════════════════════════════════

BASE="/opt/automacoes/GSG/gestao/diretoria/dashboards/app"
echo "🚀 Iniciando deploy GSG Hub Gerencial v2.0..."
echo ""

# ── BACKUP ──────────────────────────────────────────
echo "📦 Fazendo backup dos arquivos originais..."
cp "$BASE/templates/base/layout.html"   "$BASE/templates/base/layout.html.bkp2"   2>/dev/null
cp "$BASE/templates/index.html"         "$BASE/templates/index.html.bkp2"          2>/dev/null
cp "$BASE/templates/auth/login.html"    "$BASE/templates/auth/login.html.bkp2"     2>/dev/null
cp "$BASE/templates/portal/index.html"  "$BASE/templates/portal/index.html.bkp2"   2>/dev/null
echo "✅ Backups salvos (.bkp2)"
echo ""

# ════════════════════════════════════════════════════
# 1. LAYOUT BASE
# ════════════════════════════════════════════════════
echo "📝 Gerando layout.html..."
cat > "$BASE/templates/base/layout.html" << 'PYEOF'
<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hub Gerencial — GSG</title>
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#080b11;--bg2:#0e1117;--bg3:#13181f;--bg4:#1a2030;
  --border:rgba(255,255,255,0.06);--border2:rgba(255,255,255,0.10);
  --text:#e8ecf2;--text2:#8892a4;--text3:#4f5a6b;
  --green:#10d9a0;--green2:#06b585;--greenglow:rgba(16,217,160,0.15);
  --red:#f04f5e;--redglow:rgba(240,79,94,0.12);
  --warn:#f5a623;--warnglow:rgba(245,166,35,0.12);
  --blue:#4f8ef7;--blueglow:rgba(79,142,247,0.12);
  --purple:#8b5cf6;--purpleglow:rgba(139,92,246,0.12);
  --sidebar-w:240px;--topbar-h:56px;
  --radius:10px;--radius-lg:14px;
  --shadow:0 8px 32px rgba(0,0,0,0.4);--trans:all 0.2s ease;
}
body.light{
  --bg:#f0f4f9;--bg2:#ffffff;--bg3:#f8fafc;--bg4:#eef2f8;
  --border:rgba(0,0,0,0.07);--border2:rgba(0,0,0,0.12);
  --text:#111827;--text2:#4b5563;--text3:#9ca3af;
  --shadow:0 4px 20px rgba(0,0,0,0.08);
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{height:100%}
body{min-height:100vh;background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;font-size:13.5px;line-height:1.5;display:flex;transition:background .3s,color .3s}
#sidebar{width:var(--sidebar-w);min-height:100vh;background:var(--bg2);border-right:1px solid var(--border);display:flex;flex-direction:column;position:fixed;top:0;left:0;bottom:0;z-index:200;transition:var(--trans)}
.sb-brand{display:flex;align-items:center;gap:11px;padding:20px 18px 18px;border-bottom:1px solid var(--border)}
.sb-logo{width:36px;height:36px;background:linear-gradient(135deg,var(--green),var(--green2));border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:0 0 16px var(--greenglow)}
.sb-logo i{color:#fff;font-size:15px}
.sb-brand-text{line-height:1.15}
.sb-brand-name{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:13.5px;color:var(--text);letter-spacing:.3px}
.sb-brand-sub{font-size:9.5px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--green)}
.sb-body{flex:1;overflow-y:auto;padding:10px 0}
.sb-body::-webkit-scrollbar{width:3px}
.sb-body::-webkit-scrollbar-thumb{background:var(--border2);border-radius:2px}
.sb-section{padding:16px 14px 4px}
.sb-section-label{font-size:9px;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:var(--text3);padding:0 6px 8px}
.sb-item{list-style:none;margin-bottom:1px}
.sb-link{display:flex;align-items:center;gap:9px;padding:8px 10px;border-radius:8px;color:var(--text2);text-decoration:none;font-size:13px;font-weight:500;transition:var(--trans);position:relative}
.sb-link:hover{background:var(--greenglow);color:var(--green);text-decoration:none}
.sb-link.active{background:var(--greenglow);color:var(--green)}
.sb-link.active::before{content:'';position:absolute;left:0;top:20%;bottom:20%;width:3px;border-radius:0 3px 3px 0;background:var(--green)}
.sb-icon{width:28px;height:28px;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:12px;flex-shrink:0;background:transparent;transition:var(--trans)}
.sb-link:hover .sb-icon,.sb-link.active .sb-icon{background:rgba(16,217,160,0.12)}
.sb-link span{flex:1}
.sb-footer{padding:12px 14px;border-top:1px solid var(--border)}
.sb-user{display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:9px;background:var(--bg3)}
.sb-avatar{width:32px;height:32px;background:linear-gradient(135deg,var(--green),var(--green2));border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff;flex-shrink:0}
.sb-user-name{font-size:12.5px;font-weight:600;color:var(--text);line-height:1.2}
.sb-user-role{font-size:10px;color:var(--text3)}
.sb-separator{height:1px;background:var(--border);margin:6px 14px}
#main{margin-left:var(--sidebar-w);flex:1;display:flex;flex-direction:column;min-height:100vh}
#topbar{height:var(--topbar-h);background:var(--bg2);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 24px;position:sticky;top:0;z-index:100;transition:var(--trans)}
.topbar-left{display:flex;align-items:center;gap:10px}
.topbar-breadcrumb{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text3)}
.topbar-breadcrumb span{color:var(--text);font-weight:600;font-size:13.5px}
.topbar-right{display:flex;align-items:center;gap:8px}
.topbar-user-dot{display:flex;align-items:center;gap:6px;font-size:13px;font-weight:600;color:var(--green)}
.topbar-user-dot::before{content:'';width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 8px var(--green)}
.btn-icon{width:32px;height:32px;border-radius:8px;background:var(--bg3);border:1px solid var(--border);color:var(--text2);font-size:12px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:var(--trans)}
.btn-icon:hover{background:var(--greenglow);color:var(--green);border-color:rgba(16,217,160,.3)}
.btn-logout{display:flex;align-items:center;gap:6px;padding:6px 14px;border-radius:8px;background:var(--redglow);border:1px solid rgba(240,79,94,.2);color:var(--red);font-size:12px;font-weight:600;text-decoration:none;transition:var(--trans)}
.btn-logout:hover{background:rgba(240,79,94,.2);color:var(--red);text-decoration:none}
#content{flex:1;padding:24px 28px;max-width:1600px;width:100%;margin:0 auto}
.card{background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius-lg);overflow:hidden;transition:var(--trans)}
.card:hover{border-color:var(--border2)}
.card-header{padding:14px 18px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between}
.card-title{font-family:'Space Grotesk',sans-serif;font-size:11px;font-weight:600;letter-spacing:1.2px;text-transform:uppercase;color:var(--text2)}
.card-body{padding:18px}
.kpi-card{background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius-lg);padding:18px 20px 16px;position:relative;overflow:hidden;transition:var(--trans);cursor:default}
.kpi-card::after{content:'';position:absolute;top:0;left:0;right:0;height:2px}
.kpi-card:hover{transform:translateY(-2px);box-shadow:var(--shadow)}
.kpi-card.c-green::after{background:linear-gradient(90deg,var(--green),var(--green2))}
.kpi-card.c-red::after{background:linear-gradient(90deg,var(--red),#ff7a86)}
.kpi-card.c-warn::after{background:linear-gradient(90deg,var(--warn),#fbbf24)}
.kpi-card.c-blue::after{background:linear-gradient(90deg,var(--blue),#7cb3ff)}
.kpi-card.c-purple::after{background:linear-gradient(90deg,var(--purple),#a78bfa)}
.kpi-icon{width:36px;height:36px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:14px;margin-bottom:14px}
.c-green .kpi-icon{background:var(--greenglow);color:var(--green)}
.c-red .kpi-icon{background:var(--redglow);color:var(--red)}
.c-warn .kpi-icon{background:var(--warnglow);color:var(--warn)}
.c-blue .kpi-icon{background:var(--blueglow);color:var(--blue)}
.c-purple .kpi-icon{background:var(--purpleglow);color:var(--purple)}
.kpi-label{font-size:9.5px;font-weight:700;letter-spacing:1.8px;text-transform:uppercase;color:var(--text3);margin-bottom:5px}
.kpi-value{font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:700;color:var(--text);line-height:1.1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.kpi-sub{font-size:12px;color:var(--text3);margin-top:5px}
.v-green{color:var(--green)!important}.v-red{color:var(--red)!important}.v-warn{color:var(--warn)!important}.v-blue{color:var(--blue)!important}.v-purple{color:var(--purple)!important}
.badge{display:inline-flex;align-items:center;gap:4px;font-size:10px;font-weight:700;padding:3px 8px;border-radius:5px;letter-spacing:.4px}
.badge-green{background:var(--greenglow);color:var(--green)}.badge-red{background:var(--redglow);color:var(--red)}.badge-warn{background:var(--warnglow);color:var(--warn)}.badge-blue{background:var(--blueglow);color:var(--blue)}.badge-gray{background:var(--bg4);color:var(--text2)}
.table-gsg{width:100%;border-collapse:collapse}
.table-gsg thead th{font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--text3);padding:10px 14px;border-bottom:1px solid var(--border);white-space:nowrap}
.table-gsg tbody td{padding:11px 14px;font-size:13px;color:var(--text);border-bottom:1px solid var(--border);transition:var(--trans)}
.table-gsg tbody tr:hover td{background:var(--bg3)}
.table-gsg tbody tr:last-child td{border-bottom:none}
.date-filter{display:flex;align-items:center;gap:8px;background:var(--bg3);border:1px solid var(--border);border-radius:9px;padding:7px 14px}
.date-filter input[type=date]{background:transparent;border:none;outline:none;color:var(--text);font-family:'Inter',sans-serif;font-size:12.5px;font-weight:500}
.date-filter input[type=date]::-webkit-calendar-picker-indicator{filter:invert(.5);cursor:pointer}
body.light .date-filter input[type=date]::-webkit-calendar-picker-indicator{filter:invert(.3)}
.date-sep{color:var(--text3);font-size:11px}
.btn-refresh{width:28px;height:28px;border-radius:7px;background:var(--green);border:none;color:#fff;font-size:11px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:var(--trans)}
.btn-refresh:hover{background:var(--green2);transform:rotate(90deg)}
.btn-period{padding:5px 11px;border-radius:6px;background:var(--bg3);border:1px solid var(--border);color:var(--text2);font-size:11px;font-weight:600;cursor:pointer;transition:var(--trans);font-family:'Inter',sans-serif}
.btn-period:hover{background:var(--greenglow);color:var(--green);border-color:rgba(16,217,160,.3)}
.btn-period.active{background:var(--greenglow);color:var(--green);border-color:rgba(16,217,160,.4)}
.page-header{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:24px;flex-wrap:wrap;gap:14px}
.page-header-left h1{font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:700;color:var(--text);line-height:1.2}
.page-header-left p{font-size:12px;color:var(--text3);margin-top:3px}
::-webkit-scrollbar{width:4px;height:4px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:2px}
footer{padding:14px 28px;border-top:1px solid var(--border);font-size:11px;color:var(--text3);display:flex;align-items:center;justify-content:space-between}
@media(max-width:768px){
  :root{--sidebar-w:60px}
  .sb-brand-text,.sb-section-label,.sb-link span,.sb-user-name,.sb-user-role{display:none}
  .sb-brand{padding:18px 13px;justify-content:center}
  .sb-link{justify-content:center;padding:10px}
  .sb-user{justify-content:center}
  #content{padding:16px}
}
</style>
</head>
<body>
<div id="sidebar">
  <div class="sb-brand">
    <div class="sb-logo"><i class="fas fa-chart-pie"></i></div>
    <div class="sb-brand-text">
      <div class="sb-brand-name">HUB GERENCIAL</div>
      <div class="sb-brand-sub">GSG Intelligence</div>
    </div>
  </div>
  <div class="sb-body">
    {% if session.user.nivel == 99 %}
    <div class="sb-section">
      <div class="sb-section-label">Master</div>
      <ul style="list-style:none">
        <li class="sb-item"><a class="sb-link" href="/portal"><div class="sb-icon"><i class="fas fa-users-cog"></i></div><span>Governança</span></a></li>
      </ul>
    </div>
    <div class="sb-separator"></div>
    {% endif %}
    <div class="sb-section">
      <div class="sb-section-label">Financeiro</div>
      <ul style="list-style:none">
        {% if 'FIN_CON' in session.user.permissao or session.user.nivel == 99 %}
        <li class="sb-item"><a class="sb-link" href="/dashboard/visao_geral"><div class="sb-icon"><i class="fas fa-layer-group"></i></div><span>Visão Geral</span></a></li>
        {% endif %}
        {% if 'FIN_REC' in session.user.permissao or session.user.nivel == 99 %}
        <li class="sb-item"><a class="sb-link" href="/dashboard/financeiro"><div class="sb-icon"><i class="fas fa-arrow-trend-up"></i></div><span>Contas a Receber</span></a></li>
        {% endif %}
        {% if 'FIN_PAG' in session.user.permissao or session.user.nivel == 99 %}
        <li class="sb-item"><a class="sb-link" href="/dashboard/pagar"><div class="sb-icon"><i class="fas fa-file-invoice-dollar"></i></div><span>Contas a Pagar</span></a></li>
        {% endif %}
      </ul>
    </div>
    <div class="sb-separator"></div>
    <div class="sb-section">
      <div class="sb-section-label">Crescimento</div>
      <ul style="list-style:none">
        {% if 'COM' in session.user.permissao or session.user.nivel == 99 %}
        <li class="sb-item"><a class="sb-link" href="/dashboard/comercial/"><div class="sb-icon"><i class="fas fa-chart-line"></i></div><span>Performance Vendas</span></a></li>
        {% endif %}
      </ul>
    </div>
    <div class="sb-separator"></div>
    <div class="sb-section">
      <div class="sb-section-label">Operacional</div>
      <ul style="list-style:none">
        {% if 'TEC' in session.user.permissao or session.user.nivel == 99 %}
        <li class="sb-item"><a class="sb-link" href="/dashboard/tecnico/"><div class="sb-icon"><i class="fas fa-tools"></i></div><span>Setor Técnico</span></a></li>
        {% endif %}
        {% if 'EST' in session.user.permissao or session.user.nivel == 99 %}
        <li class="sb-item"><a class="sb-link" href="/dashboard/estoque/"><div class="sb-icon"><i class="fas fa-boxes-stacked"></i></div><span>Estoque</span></a></li>
        {% endif %}
      </ul>
    </div>
  </div>
  <div class="sb-footer">
    <div class="sb-user">
      <div class="sb-avatar">{{ session.user.nome[0] | upper }}</div>
      <div style="min-width:0;flex:1">
        <div class="sb-user-name">{{ session.user.nome }}</div>
        <div class="sb-user-role">{{ session.user.setor }}</div>
      </div>
    </div>
  </div>
</div>
<div id="main">
  <div id="topbar">
    <div class="topbar-left">
      <div class="topbar-breadcrumb">
        <i class="fas fa-home" style="font-size:11px"></i>
        <i class="fas fa-chevron-right" style="font-size:9px;color:var(--text3)"></i>
        <span>{% block page_title %}Dashboard{% endblock %}</span>
      </div>
    </div>
    <div class="topbar-right">
      <div class="topbar-user-dot">{{ session.user.nome }}</div>
      <button class="btn-icon" id="btnTheme" onclick="toggleTheme()" title="Alternar tema">
        <i class="fas fa-moon" id="themeIcon"></i>
      </button>
      <a href="/auth/logout" class="btn-logout"><i class="fas fa-right-from-bracket"></i> Sair</a>
    </div>
  </div>
  <div id="content">{% block content %}{% endblock %}</div>
  <footer><span>Hub Gerencial &copy; 2026 — GSG IaTechHub</span><span style="font-size:10px;color:var(--text3)">v2.0</span></footer>
</div>
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
document.querySelectorAll('#sidebar .sb-link').forEach(link=>{
  if(link.getAttribute('href')===window.location.pathname||
     window.location.pathname.startsWith(link.getAttribute('href').replace(/\/$/,'')+'/'))
    link.classList.add('active');
});
function toggleTheme(){
  const l=document.body.classList.toggle('light');
  localStorage.setItem('gsg_theme',l?'light':'dark');
  document.getElementById('themeIcon').className=l?'fas fa-sun':'fas fa-moon';
}
(function(){
  if(localStorage.getItem('gsg_theme')==='light'){
    document.body.classList.add('light');
    const ic=document.getElementById('themeIcon');
    if(ic)ic.className='fas fa-sun';
  }
})();
</script>
{% block scripts %}{% endblock %}
</body>
</html>
PYEOF
echo "  ✅ layout.html"

# ════════════════════════════════════════════════════
# 2. HOME (index.html)
# ════════════════════════════════════════════════════
echo "📝 Gerando index.html (home)..."
cat > "$BASE/templates/index.html" << 'PYEOF'
{% extends "base/layout.html" %}
{% block page_title %}Visão Executiva{% endblock %}
{% block content %}
<div class="page-header">
  <div class="page-header-left">
    <h1><i class="fas fa-chart-pie" style="color:var(--green);margin-right:10px;font-size:18px"></i>Performance de Recebimento</h1>
    <p>Visão geral da saúde financeira e fluxo de caixa</p>
  </div>
  <div class="date-filter">
    <i class="fas fa-calendar-alt" style="color:var(--text3);font-size:11px"></i>
    <input type="date" id="date-start">
    <span class="date-sep">até</span>
    <input type="date" id="date-end">
    <button class="btn-refresh" onclick="updateUI()" title="Atualizar"><i class="fas fa-sync-alt" id="icon-refresh"></i></button>
  </div>
</div>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin-bottom:24px">
  <div class="kpi-card c-green"><div class="kpi-icon"><i class="fas fa-circle-check"></i></div><div class="kpi-label">Pagamento no Prazo</div><div class="kpi-value v-green" id="prazo-perc">—</div><div class="kpi-sub" id="prazo-val">carregando...</div></div>
  <div class="kpi-card c-blue"><div class="kpi-icon"><i class="fas fa-rotate"></i></div><div class="kpi-label">Recuperação Mês Ant.</div><div class="kpi-value v-blue" id="rec-perc">—</div><div class="kpi-sub" id="rec-val">carregando...</div></div>
  <div class="kpi-card c-purple"><div class="kpi-icon"><i class="fas fa-users"></i></div><div class="kpi-label">ARPU Real / Cliente</div><div class="kpi-value v-purple" id="arpu-val">—</div><div class="kpi-sub" id="arpu-cli">0 clientes pagantes</div></div>
  <div class="kpi-card c-red"><div class="kpi-icon"><i class="fas fa-triangle-exclamation"></i></div><div class="kpi-label">Inadimplência Mês</div><div class="kpi-value v-red" id="inad-mes-perc">—</div><div class="kpi-sub" id="inad-mes-val">carregando...</div></div>
  <div class="kpi-card c-warn"><div class="kpi-icon"><i class="fas fa-calendar-xmark"></i></div><div class="kpi-label">Inadimplência Anual</div><div class="kpi-value v-warn" id="inad-ano-perc">—</div><div class="kpi-sub" id="inad-ano-val">carregando...</div></div>
  <div class="kpi-card c-red" style="border-color:rgba(240,79,94,.25)"><div class="kpi-icon" style="background:rgba(240,79,94,.18)"><i class="fas fa-shield-halved"></i></div><div class="kpi-label">Exposição de Risco</div><div class="kpi-value v-red" id="exp-val">—</div><div class="kpi-sub" id="exp-qtd">0 títulos vencidos</div></div>
</div>
<div style="margin-bottom:8px">
  <div style="font-family:'Space Grotesk',sans-serif;font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--text3);margin-bottom:14px">Acessos Rápidos</div>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(185px,1fr));gap:10px">
    {% if 'FIN_REC' in session.user.permissao or session.user.nivel == 99 %}
    <a href="/dashboard/financeiro" style="text-decoration:none"><div class="card" style="padding:16px 18px;display:flex;align-items:center;gap:13px;transition:all .2s;cursor:pointer" onmouseover="this.style.borderColor='var(--green)'" onmouseout="this.style.borderColor='var(--border)'"><div style="width:38px;height:38px;border-radius:9px;background:var(--greenglow);display:flex;align-items:center;justify-content:center;color:var(--green);font-size:15px;flex-shrink:0"><i class="fas fa-arrow-trend-up"></i></div><div><div style="font-weight:600;font-size:13px;color:var(--text)">Contas a Receber</div><div style="font-size:11px;color:var(--text3);margin-top:1px">Inadimplência & KPIs</div></div></div></a>
    {% endif %}
    {% if 'FIN_PAG' in session.user.permissao or session.user.nivel == 99 %}
    <a href="/dashboard/pagar" style="text-decoration:none"><div class="card" style="padding:16px 18px;display:flex;align-items:center;gap:13px;transition:all .2s;cursor:pointer" onmouseover="this.style.borderColor='var(--blue)'" onmouseout="this.style.borderColor='var(--border)'"><div style="width:38px;height:38px;border-radius:9px;background:var(--blueglow);display:flex;align-items:center;justify-content:center;color:var(--blue);font-size:15px;flex-shrink:0"><i class="fas fa-file-invoice-dollar"></i></div><div><div style="font-weight:600;font-size:13px;color:var(--text)">Contas a Pagar</div><div style="font-size:11px;color:var(--text3);margin-top:1px">Obrigações & Vencimentos</div></div></div></a>
    {% endif %}
    {% if 'FIN_CON' in session.user.permissao or session.user.nivel == 99 %}
    <a href="/dashboard/visao_geral" style="text-decoration:none"><div class="card" style="padding:16px 18px;display:flex;align-items:center;gap:13px;transition:all .2s;cursor:pointer" onmouseover="this.style.borderColor='var(--purple)'" onmouseout="this.style.borderColor='var(--border)'"><div style="width:38px;height:38px;border-radius:9px;background:var(--purpleglow);display:flex;align-items:center;justify-content:center;color:var(--purple);font-size:15px;flex-shrink:0"><i class="fas fa-layer-group"></i></div><div><div style="font-weight:600;font-size:13px;color:var(--text)">Visão Geral</div><div style="font-size:11px;color:var(--text3);margin-top:1px">Consolidado Financeiro</div></div></div></a>
    {% endif %}
    {% if 'COM' in session.user.permissao or session.user.nivel == 99 %}
    <a href="/dashboard/comercial/" style="text-decoration:none"><div class="card" style="padding:16px 18px;display:flex;align-items:center;gap:13px;transition:all .2s;cursor:pointer" onmouseover="this.style.borderColor='var(--warn)'" onmouseout="this.style.borderColor='var(--border)'"><div style="width:38px;height:38px;border-radius:9px;background:var(--warnglow);display:flex;align-items:center;justify-content:center;color:var(--warn);font-size:15px;flex-shrink:0"><i class="fas fa-chart-line"></i></div><div><div style="font-weight:600;font-size:13px;color:var(--text)">Performance Vendas</div><div style="font-size:11px;color:var(--text3);margin-top:1px">Comercial & Metas</div></div></div></a>
    {% endif %}
    {% if 'TEC' in session.user.permissao or session.user.nivel == 99 %}
    <a href="/dashboard/tecnico/" style="text-decoration:none"><div class="card" style="padding:16px 18px;display:flex;align-items:center;gap:13px;transition:all .2s;cursor:pointer" onmouseover="this.style.borderColor='var(--red)'" onmouseout="this.style.borderColor='var(--border)'"><div style="width:38px;height:38px;border-radius:9px;background:var(--redglow);display:flex;align-items:center;justify-content:center;color:var(--red);font-size:15px;flex-shrink:0"><i class="fas fa-screwdriver-wrench"></i></div><div><div style="font-weight:600;font-size:13px;color:var(--text)">Setor Técnico</div><div style="font-size:11px;color:var(--text3);margin-top:1px">OS & Produtividade</div></div></div></a>
    {% endif %}
    {% if 'EST' in session.user.permissao or session.user.nivel == 99 %}
    <a href="/dashboard/estoque/" style="text-decoration:none"><div class="card" style="padding:16px 18px;display:flex;align-items:center;gap:13px;transition:all .2s;cursor:pointer" onmouseover="this.style.borderColor='var(--text2)'" onmouseout="this.style.borderColor='var(--border)'"><div style="width:38px;height:38px;border-radius:9px;background:var(--bg4);display:flex;align-items:center;justify-content:center;color:var(--text2);font-size:15px;flex-shrink:0"><i class="fas fa-boxes-stacked"></i></div><div><div style="font-weight:600;font-size:13px;color:var(--text)">Estoque</div><div style="font-size:11px;color:var(--text3);margin-top:1px">Inventário & Controle</div></div></div></a>
    {% endif %}
  </div>
</div>
<script>
const fmt=v=>new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(v||0);
const fmtP=v=>`${parseFloat(v||0).toFixed(2)}%`;
function setLoading(on){document.getElementById('icon-refresh').classList.toggle('fa-spin',on)}
async function updateUI(){
  const start=document.getElementById('date-start').value;
  const end=document.getElementById('date-end').value;
  setLoading(true);
  try{
    const res=await fetch(`/api/financeiro/resumo?inicio=${start}&fim=${end}`);
    const r=await res.json();
    if(r.status==='success'){
      const d=r.data;
      if(d.pagamento_prazo){document.getElementById('prazo-perc').innerText=fmtP(d.pagamento_prazo.percentual_no_prazo);document.getElementById('prazo-val').innerText=fmt(d.pagamento_prazo.total_pago_no_prazo)+' recebido';}
      if(d.recuperacao_mes_ant){document.getElementById('rec-perc').innerText=fmtP(d.recuperacao_mes_ant.taxa_recuperacao);document.getElementById('rec-val').innerText=fmt(d.recuperacao_mes_ant.total_recuperado);}
      if(d.arpu_caixa){document.getElementById('arpu-val').innerText=fmt(d.arpu_caixa.arpu_real);document.getElementById('arpu-cli').innerText=`${d.arpu_caixa.clientes_pagantes||0} clientes pagantes`;}
      if(d.inadimplencia_mes){document.getElementById('inad-mes-perc').innerText=fmtP(d.inadimplencia_mes.percentual_inadimplencia);document.getElementById('inad-mes-val').innerText=fmt(d.inadimplencia_mes.total_ainda_em_aberto)+' em aberto';}
      if(d.inadimplencia_ano){document.getElementById('inad-ano-perc').innerText=fmtP(d.inadimplencia_ano.percentual_inadimplencia_ano);document.getElementById('inad-ano-val').innerText=fmt(d.inadimplencia_ano.total_em_aberto_no_ano)+' acumulado';}
      if(d.exposicao_mes){document.getElementById('exp-val').innerText=fmt(d.exposicao_mes.total_exposto);document.getElementById('exp-qtd').innerText=`${d.exposicao_mes.qtd_titulos_vencidos||0} títulos vencidos`;}
    }
  }catch(e){console.error(e);}
  setLoading(false);
}
window.onload=()=>{
  const now=new Date();
  document.getElementById('date-start').value=new Date(now.getFullYear(),now.getMonth(),1).toISOString().split('T')[0];
  document.getElementById('date-end').value=now.toISOString().split('T')[0];
  updateUI();
};
</script>
{% endblock %}
PYEOF
echo "  ✅ index.html"

# ════════════════════════════════════════════════════
# 3. LOGIN
# ════════════════════════════════════════════════════
echo "📝 Gerando login.html..."
cat > "$BASE/templates/auth/login.html" << 'PYEOF'
<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hub Gerencial — GSG</title>
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#080b11;--bg2:#0e1117;--bg3:#13181f;--border:rgba(255,255,255,0.06);--text:#e8ecf2;--text2:#8892a4;--text3:#4f5a6b;--green:#10d9a0;--green2:#06b585;--greenglow:rgba(16,217,160,0.15);--red:#f04f5e}
body{min-height:100vh;background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;display:flex;align-items:center;justify-content:center;padding:20px;position:relative;overflow:hidden}
body::before{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(16,217,160,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(16,217,160,0.03) 1px,transparent 1px);background-size:48px 48px;pointer-events:none}
body::after{content:'';position:fixed;top:-200px;left:-200px;width:600px;height:600px;background:radial-gradient(circle,rgba(16,217,160,0.06) 0%,transparent 70%);pointer-events:none}
.wrap{width:100%;max-width:400px;position:relative;z-index:1}
.brand{text-align:center;margin-bottom:32px}
.logo{width:52px;height:52px;background:linear-gradient(135deg,var(--green),var(--green2));border-radius:14px;display:inline-flex;align-items:center;justify-content:center;font-size:22px;color:#fff;box-shadow:0 0 32px var(--greenglow);margin-bottom:14px}
.title{font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:700;color:var(--text)}
.subtitle{font-size:12.5px;color:var(--text3);margin-top:4px}
.card{background:var(--bg2);border:1px solid var(--border);border-radius:16px;padding:32px;box-shadow:0 24px 64px rgba(0,0,0,0.4)}
.fg{margin-bottom:18px}
.lbl{display:block;font-size:11.5px;font-weight:600;color:var(--text2);margin-bottom:8px;letter-spacing:.3px}
.iw{position:relative}
.inp{width:100%;padding:11px 14px 11px 40px;background:var(--bg3);border:1px solid var(--border);border-radius:9px;color:var(--text);font-family:'Inter',sans-serif;font-size:13.5px;outline:none;transition:all .2s}
.inp:focus{border-color:rgba(16,217,160,.4);box-shadow:0 0 0 3px rgba(16,217,160,.08)}
.inp::placeholder{color:var(--text3)}
.ic{position:absolute;left:13px;top:50%;transform:translateY(-50%);color:var(--text3);font-size:13px;pointer-events:none}
.btn{width:100%;padding:12px;background:linear-gradient(135deg,var(--green),var(--green2));border:none;border-radius:9px;color:#fff;font-family:'Inter',sans-serif;font-size:14px;font-weight:600;cursor:pointer;transition:all .2s;letter-spacing:.3px;margin-top:6px}
.btn:hover{transform:translateY(-1px);box-shadow:0 8px 24px var(--greenglow)}
.err{display:flex;align-items:center;gap:8px;background:rgba(240,79,94,.1);border:1px solid rgba(240,79,94,.2);border-radius:8px;padding:10px 14px;color:var(--red);font-size:12.5px;margin-bottom:18px}
.foot{text-align:center;margin-top:20px;font-size:11px;color:var(--text3)}
</style>
</head>
<body>
<div class="wrap">
  <div class="brand">
    <div class="logo"><i class="fas fa-chart-pie"></i></div>
    <div class="title">Hub Gerencial</div>
    <div class="subtitle">GSG Intelligence — Acesso Restrito</div>
  </div>
  <div class="card">
    {% if request.query_params.get('error') %}
    <div class="err"><i class="fas fa-circle-xmark"></i>Login ou senha incorretos. Tente novamente.</div>
    {% endif %}
    <form action="/auth/login" method="POST">
      <div class="fg">
        <label class="lbl">Usuário</label>
        <div class="iw"><i class="fas fa-user ic"></i><input type="text" name="username" class="inp" placeholder="seu.login" autocomplete="username" required autofocus></div>
      </div>
      <div class="fg">
        <label class="lbl">Senha</label>
        <div class="iw"><i class="fas fa-lock ic"></i><input type="password" name="password" class="inp" placeholder="••••••••" autocomplete="current-password" required></div>
      </div>
      <button type="submit" class="btn"><i class="fas fa-right-to-bracket" style="margin-right:7px"></i>Entrar</button>
    </form>
  </div>
  <div class="foot">Hub Gerencial &copy; 2026 — GSG IaTechHub</div>
</div>
</body>
</html>
PYEOF
echo "  ✅ login.html"

# ════════════════════════════════════════════════════
# 4. PORTAL / GOVERNANÇA
# ════════════════════════════════════════════════════
echo "📝 Gerando portal/index.html..."
cat > "$BASE/templates/portal/index.html" << 'PYEOF'
{% extends "base/layout.html" %}
{% block page_title %}Governança{% endblock %}
{% block content %}
<style>
.btn-action{display:inline-flex;align-items:center;gap:7px;padding:9px 18px;border-radius:9px;background:var(--green);border:none;color:#fff;font-family:'Inter',sans-serif;font-size:13px;font-weight:600;cursor:pointer;transition:all .2s}
.btn-action:hover{background:var(--green2);transform:translateY(-1px)}
.btn-sm-icon{width:30px;height:30px;border-radius:7px;background:var(--bg3);border:1px solid var(--border);color:var(--text2);font-size:11px;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;transition:all .2s}
.btn-sm-icon:hover{background:var(--warnglow);color:var(--warn);border-color:rgba(245,166,35,.3)}
.perm-badge{display:inline-flex;align-items:center;font-size:10px;font-weight:700;padding:2px 8px;border-radius:4px;margin-right:4px;letter-spacing:.4px}
.perm-FIN_REC{background:var(--greenglow);color:var(--green)}.perm-FIN_PAG{background:var(--blueglow);color:var(--blue)}.perm-FIN_CON{background:var(--purpleglow);color:var(--purple)}.perm-COM{background:var(--warnglow);color:var(--warn)}.perm-TEC{background:var(--redglow);color:var(--red)}.perm-EST{background:var(--bg4);color:var(--text2)}
.timeline{padding-left:18px;border-left:1px solid var(--border)}
.tl-item{position:relative;padding:0 0 16px 18px}
.tl-item::before{content:'';position:absolute;left:-5px;top:4px;width:9px;height:9px;border-radius:50%;background:var(--bg3);border:2px solid var(--border2)}
.tl-item.success::before{border-color:var(--green);background:var(--greenglow)}.tl-item.info::before{border-color:var(--blue);background:var(--blueglow)}.tl-item.warning::before{border-color:var(--warn);background:var(--warnglow)}.tl-item.danger::before{border-color:var(--red);background:var(--redglow)}
.tl-time{font-size:10px;color:var(--text3);margin-bottom:2px}.tl-user{font-size:12.5px;font-weight:600;color:var(--text)}.tl-action{font-size:12px;color:var(--text2)}
.modal-content{background:var(--bg2);border:1px solid var(--border2);border-radius:14px;color:var(--text)}
.modal-header{background:var(--bg3);border-bottom:1px solid var(--border);border-radius:14px 14px 0 0;padding:18px 22px}
.modal-header .modal-title{font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:700;color:var(--text)}
.modal-header .close{color:var(--text2);opacity:1;font-size:18px}
.modal-body{padding:22px}.modal-footer{border-top:1px solid var(--border);padding:14px 22px;background:var(--bg3);border-radius:0 0 14px 14px}
.modal-label{font-size:11px;font-weight:600;color:var(--text2);margin-bottom:6px;display:block;letter-spacing:.3px}
.modal-input{width:100%;padding:9px 12px;background:var(--bg3);border:1px solid var(--border);border-radius:8px;color:var(--text);font-family:'Inter',sans-serif;font-size:13px;outline:none;transition:all .2s}
.modal-input:focus{border-color:rgba(16,217,160,.4);box-shadow:0 0 0 3px rgba(16,217,160,.08)}
.modal-input option{background:var(--bg2)}
.btn-cancel{padding:8px 18px;border-radius:8px;background:var(--bg4);border:1px solid var(--border);color:var(--text2);font-size:13px;font-weight:600;cursor:pointer}
</style>
<div class="page-header">
  <div class="page-header-left">
    <h1><i class="fas fa-users-cog" style="color:var(--green);margin-right:10px;font-size:18px"></i>Central de Governança</h1>
    <p>Gerenciamento de usuários, permissões e auditoria de acessos</p>
  </div>
  <button class="btn-action" data-toggle="modal" data-target="#modalUsuario"><i class="fas fa-user-plus"></i> Novo Usuário</button>
</div>
<div style="display:grid;grid-template-columns:1fr 360px;gap:16px;align-items:start">
  <div class="card">
    <div class="card-header">
      <span class="card-title"><i class="fas fa-users" style="margin-right:7px;color:var(--green)"></i>Usuários e Permissões</span>
      <span class="badge badge-gray">{{ usuarios|length }} usuários</span>
    </div>
    <div style="overflow-x:auto">
      <table class="table-gsg">
        <thead><tr><th>Usuário</th><th>Setor</th><th>Acessos</th><th>Nível</th><th style="text-align:center">Ação</th></tr></thead>
        <tbody>
          {% for user in usuarios %}
          <tr>
            <td><div style="display:flex;align-items:center;gap:10px"><div style="width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,var(--green),var(--green2));display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff;flex-shrink:0">{{ user.nome[0]|upper }}</div><div><div style="font-weight:600;font-size:13px">{{ user.nome }}</div><div style="font-size:11px;color:var(--text3)">{{ user.login }}</div></div></div></td>
            <td style="color:var(--text2)">{{ user.setor }}</td>
            <td>{% if user.permissao_dash %}{% for p in user.permissao_dash.split(',') %}{% if p.strip() %}<span class="perm-badge perm-{{ p.strip() }}">{{ p.strip() }}</span>{% endif %}{% endfor %}{% else %}<span style="font-size:11px;color:var(--text3)">—</span>{% endif %}</td>
            <td>{% if user.nivel_acesso == 99 %}<span class="badge badge-green">Admin</span>{% else %}<span class="badge badge-gray">Operacional</span>{% endif %}</td>
            <td style="text-align:center"><button class="btn-sm-icon" title="Editar" onclick="editarUsuario('{{ user.id }}','{{ user.nome }}','{{ user.login }}','{{ user.setor }}','{{ user.nivel_acesso }}','{{ user.permissao_dash }}')"><i class="fas fa-pen"></i></button></td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
  <div class="card">
    <div class="card-header"><span class="card-title"><i class="fas fa-scroll" style="margin-right:7px;color:var(--warn)"></i>Auditoria de Acessos</span></div>
    <div class="card-body" style="max-height:480px;overflow-y:auto">
      <div class="timeline">
        {% for log in logs %}
        <div class="tl-item {{ log.tipo }}">
          <div class="tl-time">{{ log.hora }}</div>
          <div class="tl-user">{{ log.user }}</div>
          <div class="tl-action">{{ log.acao }}</div>
        </div>
        {% endfor %}
      </div>
    </div>
  </div>
</div>
<div class="modal fade" id="modalUsuario" tabindex="-1" role="dialog">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <form action="/admin/usuarios/salvar" method="POST">
        <div class="modal-header"><h5 class="modal-title">Configurar Usuário</h5><button class="close" type="button" data-dismiss="modal"><i class="fas fa-times"></i></button></div>
        <div class="modal-body">
          <input type="hidden" name="usuario_id" id="edit_id">
          <div style="margin-bottom:14px"><label class="modal-label">Nome Completo</label><input type="text" name="nome" id="edit_nome" class="modal-input" required></div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px">
            <div><label class="modal-label">Login</label><input type="text" name="login" id="edit_login" class="modal-input" required></div>
            <div><label class="modal-label">Senha</label><input type="password" name="senha" class="modal-input" placeholder="Manter atual"></div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px">
            <div><label class="modal-label">Setor</label><input type="text" name="setor" id="edit_setor" class="modal-input"></div>
            <div><label class="modal-label">Nível de Acesso</label><select name="nivel" id="edit_nivel" class="modal-input"><option value="1">Operacional</option><option value="99">Administrador</option></select></div>
          </div>
          <div><label class="modal-label">Permissões (separadas por vírgula)</label><input type="text" name="permissao" id="edit_permissao" class="modal-input" placeholder="Ex: FIN_REC,FIN_PAG,COM,TEC"><div style="font-size:10.5px;color:var(--text3);margin-top:6px">Opções: FIN_REC, FIN_PAG, FIN_CON, COM, TEC, EST</div></div>
        </div>
        <div class="modal-footer"><button class="btn-cancel" type="button" data-dismiss="modal">Cancelar</button><button class="btn-action" type="submit" style="margin-left:8px"><i class="fas fa-floppy-disk"></i> Salvar</button></div>
      </form>
    </div>
  </div>
</div>
<script>
function editarUsuario(id,nome,login,setor,nivel,permissao){
  $('#edit_id').val(id);$('#edit_nome').val(nome);$('#edit_login').val(login);
  $('#edit_setor').val(setor);$('#edit_nivel').val(nivel);$('#edit_permissao').val(permissao);
  $('#modalUsuario').modal('show');
}
</script>
{% endblock %}
PYEOF
echo "  ✅ portal/index.html"

# ════════════════════════════════════════════════════
# RESTART SERVIÇO
# ════════════════════════════════════════════════════
echo ""
echo "🔄 Reiniciando serviço..."
pkill -f "uvicorn app.main:app" 2>/dev/null
sleep 1
cd /opt/automacoes/GSG/gestao/diretoria/dashboards
nohup ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload >> /tmp/gsg_hub.log 2>&1 &
sleep 2
ps aux | grep uvicorn | grep -v grep | grep 8005 && echo "✅ Serviço rodando na porta 8005" || echo "⚠️  Verifique manualmente: ps aux | grep uvicorn"
echo ""
echo "════════════════════════════════════════════"
echo "✅ DEPLOY CONCLUÍDO — acesse gsg.iatechhub.com.br"
echo "════════════════════════════════════════════"
