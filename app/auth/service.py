import sqlite3
import hashlib

class AuthService:
    def __init__(self):
        # O login agora consulta o banco local onde você cadastrou o Luciano
        self.db_path = "/opt/automacoes/GSG/gestao/diretoria/dashboards/app/gestao_local.db"

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def verificar_login(self, login, senha_plana):
        """Verifica credenciais e carrega os IDs de permissão"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Transforma a senha em hash para comparar com o banco
        senha_hash = hashlib.sha256(senha_plana.encode()).hexdigest()

        try:
            # Busca o usuário no SQLite local
            cursor.execute(
                "SELECT id, nome, login, id_setor FROM usuarios WHERE login = ? AND senha_hash = ?",
                (login, senha_hash)
            )
            user = cursor.fetchone()

            if user:
                user_id = user[0]
                # Busca os IDs que você clicou e salvou na tela admin
                cursor.execute("SELECT id_permissao FROM usuario_permissoes WHERE id_usuario = ?", (user_id,))
                permissoes = [p[0] for p in cursor.fetchall()]

                return {
                    "id": user_id,
                    "nome": user[1],
                    "login": user[2],
                    "id_setor": user[3],
                    "permissoes": permissoes # Agora o login leva os IDs 1, 2, etc.
                }
            return None
        finally:
            conn.close()
