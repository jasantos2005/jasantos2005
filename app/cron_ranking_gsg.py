"""
cron_ranking_gsg.py — Ranking comercial GSG via Telegram
Envia para TELEGRAM_AILTON (pessoal) por enquanto
"""
import os, sys, requests
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

sys.path.insert(0, '/opt/automacoes/GSG/gestao/diretoria/dashboards')
load_dotenv('/opt/automacoes/GSG/gestao/diretoria/dashboards/app/.env')

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_PESSOAL = os.getenv('TELEGRAM_AILTON')
CHAT_GRUPO   = os.getenv('TELEGRAM_CHAT_ID')
META_DIA = 4

def notificar(msg, chat=None):
    if not TOKEN or not chat:
        return
    try:
        requests.post(
            f'https://api.telegram.org/bot{TOKEN}/sendMessage',
            json={'chat_id': chat, 'text': msg, 'parse_mode': 'Markdown'},
            timeout=10
        )
    except Exception as e:
        print(f'[TELEGRAM] {e}')

def ranking_hoje():
    try:
        import pymysql, pymysql.cursors
        conn = pymysql.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME', 'ixcprovedor'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10
        )
        hoje = date.today().strftime('%Y-%m-%d')
        mes  = date.today().replace(day=1).strftime('%Y-%m-%d')
        cur  = conn.cursor()

        # Ranking do dia
        cur.execute("""
            SELECT v.nome,
                   SUM(cc.status_internet='A')  AS ativados_dia,
                   SUM(cc.status_internet='AA') AS aguard
            FROM ixcprovedor.vendedor v
            JOIN ixcprovedor.cliente_contrato cc ON cc.id_vendedor_ativ = v.id
            WHERE cc.data >= %s
              AND cc.id_vendedor_ativ > 0
              AND cc.id_vendedor_ativ != 29
            GROUP BY v.id, v.nome
            ORDER BY ativados_dia DESC
        """, (hoje,))
        dia = cur.fetchall()

        # Total do mês
        cur.execute("""
            SELECT SUM(cc.status_internet='A') AS total_mes
            FROM ixcprovedor.cliente_contrato cc
            WHERE cc.data >= %s
              AND cc.id_vendedor_ativ > 0
              AND cc.id_vendedor_ativ != 29
        """, (mes,))
        mes_row = cur.fetchone()
        conn.close()
        return dia, int(mes_row['total_mes'] or 0)
    except Exception as e:
        print(f'[RANKING] Erro: {e}')
        return [], 0

def msg_horaria():
    dia, total_mes = ranking_hoje()
    if not dia:
        return None
    hora = datetime.now().strftime('%H:%M')
    data_fmt = date.today().strftime('%d/%m/%Y')
    medalhas = ['🥇','🥈','🥉','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣']
    linhas = [
        f'📊 *Ranking GSG — {data_fmt}*',
        ''
    ]
    total_dia = 0
    for i, v in enumerate(dia):
        nome  = v['nome'].split()[0]
        ativ  = int(v['ativados_dia'] or 0)
        aguard = int(v['aguard'] or 0)
        total_dia += ativ
        med = medalhas[i] if i < len(medalhas) else '▪️'
        barra = '🟩' * min(ativ, META_DIA) + '⬜' * max(0, META_DIA - ativ)
        linhas.append(f'{med} *{nome}* — {ativ} ativ. | {aguard} aguard.')
        linhas.append(f'   {barra}')
    linhas += [
        '',
        f'🎯 Total dia: *{total_dia}* | Mês: *{total_mes}*'
    ]
    return '\n'.join(linhas)

def msg_fechamento():
    dia, total_mes = ranking_hoje()
    if not dia:
        return None
    data_fmt = date.today().strftime('%d/%m/%Y')
    medalhas = ['🥇','🥈','🥉','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣']
    linhas = [
        '━━━━━━━━━━━━━━━━━━━━',
        f'🔔 *FECHAMENTO GSG — {data_fmt}*',
        '━━━━━━━━━━━━━━━━━━━━',
        f'🎯 Meta: *{META_DIA}* ativações/vendedor',
        ''
    ]
    total_dia = 0
    for i, v in enumerate(dia):
        nome  = v['nome'].split()[0]
        ativ  = int(v['ativados_dia'] or 0)
        total_dia += ativ
        med = medalhas[i] if i < len(medalhas) else '▪️'
        pct = int(ativ / META_DIA * 100)
        barra = '🟩' * min(ativ, META_DIA) + '⬜' * max(0, META_DIA - ativ)
        status = '✅ Meta!' if ativ >= META_DIA else ('⚡ Quase!' if ativ >= META_DIA/2 else '❌ Abaixo')
        linhas.append(f'{med} *{nome}* — {status}')
        linhas.append(f'   {barra} {pct}% | {ativ} ativ.')
        linhas.append('')
    linhas += [
        '━━━━━━━━━━━━━━━━━━━━',
        f'📋 Total dia: *{total_dia}* | Mês: *{total_mes}*',
        '━━━━━━━━━━━━━━━━━━━━',
        '',
        '✨ Até amanhã, equipe! 🌙'
    ]
    return '\n'.join(linhas)

if __name__ == '__main__':
    hora = datetime.now().hour
    modo = sys.argv[1] if len(sys.argv) > 1 else 'auto'

    if modo == 'teste':
        msg = msg_horaria()
        if msg:
            notificar(msg, CHAT_PESSOAL)
            print('✅ Mensagem de teste enviada para você')
        else:
            print('⚠️  Sem dados para enviar')
    elif modo == 'fechamento':
        msg = msg_fechamento()
        if msg:
            notificar(msg, CHAT_PESSOAL)
            print('✅ Fechamento enviado para você')
    elif modo == 'grupo':
        msg = msg_horaria()
        if msg:
            notificar(msg, CHAT_GRUPO)
            print('✅ Enviado para o grupo')
    else:
        # Auto — decide pelo horário
        if hora == 18:
            msg = msg_fechamento()
        else:
            msg = msg_horaria()
        if msg:
            notificar(msg, CHAT_PESSOAL)
            print(f'✅ Ranking {hora}h enviado')
