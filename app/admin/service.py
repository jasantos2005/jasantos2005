import sqlite3
import csv
import io
from datetime import datetime

class AdminService:
    def __init__(self):
        self.db_path = "/opt/automacoes/GSG/gestao/diretoria/dashboards/app/axiom_core.db"

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def registrar_acao(self, usuario, acao, tipo="info"):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO auditoria (usuario, acao, tipo, data_hora) VALUES (?, ?, ?, ?)",
            (usuario, acao, tipo, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        conn.close()

    def listar_logs(self, limite=20):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT usuario as user, acao, tipo,
            strftime('%d/%m %H:%M', data_hora, 'localtime') as hora
            FROM auditoria ORDER BY id DESC LIMIT ?
        """, (limite,))
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return logs

    # --- VERSÃO 6: BI & ANALYTICS ---
    
    def get_stats_acessos_7_dias(self):
        """ Retorna dados para o gráfico de acessos dos últimos 7 dias """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT strftime('%d/%m', data_hora, 'localtime') as dia, COUNT(*) as total
            FROM auditoria 
            WHERE data_hora >= date('now', '-7 days')
            GROUP BY dia ORDER BY data_hora ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        return {"labels": [r['dia'] for r in rows], "data": [r['total'] for r in rows]}

    def gerar_csv_auditoria(self):
        """ Gera um CSV em memória com todos os logs para exportação """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT data_hora, usuario, acao, tipo FROM auditoria ORDER BY id DESC")
        rows = cursor.fetchall()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Data/Hora', 'Usuário', 'Ação', 'Status']) # Cabeçalho
        for row in rows:
            writer.writerow(list(row))
        
        conn.close()
        return output.getvalue()

    # --- Gestão de Usuários (Mantido) ---
    def listar_usuarios_com_permissoes(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, login, setor, permissao_dash, nivel_acesso FROM usuarios")
        usuarios = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return usuarios

    def cadastrar_usuario(self, nome, login, senha, nivel, setor, permissao_dash=""):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE login = ?", (login,))
        exists = cursor.fetchone()

        if exists:
            if senha and senha.strip() and senha != "...":
                cursor.execute("""
                    UPDATE usuarios SET nome=?, senha_hash=?, nivel_acesso=?, setor=?, permissao_dash=?
                    WHERE login=? """, (nome, senha, nivel, setor, permissao_dash, login))
            else:
                cursor.execute("""
                    UPDATE usuarios SET nome=?, nivel_acesso=?, setor=?, permissao_dash=?
                    WHERE login=? """, (nome, nivel, setor, permissao_dash, login))
            cursor.execute("INSERT INTO auditoria (usuario, acao, tipo, data_hora) VALUES (?, ?, ?, datetime('now'))", ("Sistema", f"Usuário {login} atualizado", "warning"))
        else:
            cursor.execute("""
                INSERT INTO usuarios (nome, login, senha_hash, nivel_acesso, setor, permissao_dash)
                VALUES (?, ?, ?, ?, ?, ?) """, (nome, login, senha, nivel, setor, permissao_dash))
            cursor.execute("INSERT INTO auditoria (usuario, acao, tipo, data_hora) VALUES (?, ?, ?, datetime('now'))", ("Sistema", f"Novo usuário {login} criado", "success"))

        conn.commit()
        conn.close()
        return True
