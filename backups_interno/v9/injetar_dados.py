import mysql.connector
from app.config import settings

def criar_e_injetar():
    try:
        conn = mysql.connector.connect(
            host=settings.DB_HOST,
            user=settings.DB_USER,
            password=settings.DB_PASS,
            database=settings.DB_NAME,
            port=settings.DB_PORT
        )
        cursor = conn.cursor()
        print("Conectado ao banco. Criando tabelas...")

        # 1. Criação das Tabelas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS setores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(50) NOT NULL UNIQUE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                login VARCHAR(50) NOT NULL UNIQUE,
                senha_hash VARCHAR(255) NOT NULL,
                id_setor INT,
                status ENUM('ativo', 'inativo') DEFAULT 'ativo',
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS permissoes_disponiveis (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome_modulo VARCHAR(100) NOT NULL,
                descricao VARCHAR(255)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuario_permissoes (
                id_usuario INT,
                id_permissao INT,
                PRIMARY KEY (id_usuario, id_permissao)
            )
        """)

        # 2. Inserção dos Dados Iniciais
        print("Inserindo dados iniciais...")
        cursor.execute("INSERT IGNORE INTO setores (id, nome) VALUES (1, 'GERÊNCIA'), (2, 'FINANCEIRO'), (3, 'OPERACIONAL')")
        cursor.execute("INSERT IGNORE INTO permissoes_disponiveis (id, nome_modulo) VALUES (1, 'FIN_REC'), (2, 'FIN_PAG')")
        cursor.execute("""
            INSERT IGNORE INTO usuarios (id, nome, login, senha_hash, id_setor) 
            VALUES (1, 'Gerente Geral', 'gerente', '240be518ebb872a617e83d17d0c3ec1818e18336110a1314d101d0ec619077a8', 1)
        """)
        cursor.execute("INSERT IGNORE INTO usuario_permissoes (id_usuario, id_permissao) VALUES (1, 1), (1, 2)")

        conn.commit()
        print("✅ Tabelas criadas e dados inseridos com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    criar_e_injetar()
