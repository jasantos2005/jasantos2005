import sqlite3
from admin.service import AdminService

def tem_permissao(usuario_sessao, dash_nome):
    if not usuario_sessao:
        return False
        
    # Pega o nível de qualquer uma das chaves possíveis na sessão
    nivel = usuario_sessao.get("nivel_acesso") or usuario_sessao.get("nivel")
    if nivel == 99:
        return True

    try:
        service = AdminService()
        conn = service._get_connection()
        cursor = conn.cursor()
        # Busca a permissão atualizada direto no banco
        cursor.execute("SELECT permissao_dash FROM usuarios WHERE id = ?", (usuario_sessao.get("id"),))
        res = cursor.fetchone()
        conn.close()

        if res and res[0]:
            # Verifica se 'FIN' está na string 'FIN_REC, FIN_PAG'
            if dash_nome in res[0]:
                return True
    except Exception as e:
        print(f"Erro na validacao: {e}")
    
    return False
