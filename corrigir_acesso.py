import sqlite3
import bcrypt

db = '/opt/automacoes/GSG/gestao/diretoria/dashboards/app/axiom_core.db'

try:
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    
    # Gera o hash da senha 'sharay'
    hash_senha = bcrypt.hashpw('sharay'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # 1. Ajustar colunas nas duas tabelas possíveis
    for tabela in ['usuarios', 'users']:
        # Criar tabelas se não existirem
        if tabela == 'usuarios':
            cursor.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, login TEXT)')
        else:
            cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)')

        # Adicionar colunas necessárias ignorando erros se já existirem
        colunas = ['nome', 'password_hash', 'senha_hash', 'nivel_acesso', 'username', 'login']
        for col in colunas:
            try:
                cursor.execute(f'ALTER TABLE {tabela} ADD COLUMN {col} TEXT')
            except:
                pass

    # 2. Inserir o Master com ID 1 na tabela 'usuarios'
    cursor.execute('''
        INSERT OR REPLACE INTO usuarios (id, login, nome, senha_hash, password_hash, nivel_acesso)
        VALUES (1, 'master', 'Ailton ADM', ?, ?, 1)
    ''', (hash_senha, hash_senha))

    # 3. Inserir o Master com ID 1 na tabela 'users'
    cursor.execute('''
        INSERT OR REPLACE INTO users (id, username, nome, senha_hash, password_hash, nivel_acesso)
        VALUES (1, 'master', 'Ailton ADM', ?, ?, 1)
    ''', (hash_senha, hash_senha))

    conn.commit()
    print("\n✅ Sucesso! Master (ID 1) sincronizado em todas as tabelas.")
    print("🔑 Login: master | Senha: sharay")

except Exception as e:
    print(f"\n❌ Erro ao processar banco: {e}")
finally:
    if 'conn' in locals():
        conn.close()
