import sqlite3
import hashlib

# Tenta usar o passlib (padrão FastAPI), se não tiver, usamos um fallback
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    senha_final = pwd_context.hash("sharay")
    metodo = "Bcrypt (Passlib)"
except ImportError:
    # Fallback caso a lib não esteja no venv (menos provável)
    senha_final = hashlib.sha256("sharay".encode()).hexdigest()
    metodo = "SHA256"

db_path = '/opt/automacoes/GSG/gestao/diretoria/dashboards/app/gestao_local.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('UPDATE usuarios SET senha_hash = ? WHERE login = ?', (senha_final, 'master'))

conn.commit()
conn.close()
print(f"\n✅ Senha criptografada com {metodo} aplicada ao usuário MASTER!")
