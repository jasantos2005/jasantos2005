-- 1. Tabela de Setores (Gerência, Financeiro, Operacional)
CREATE TABLE IF NOT EXISTS setores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE
);

-- 2. Tabela de Usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    login VARCHAR(50) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    id_setor INT,
    status ENUM('ativo', 'inativo') DEFAULT 'ativo',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_setor) REFERENCES setores(id)
);

-- 3. Tabela de Permissões (IDs dos Dashboards/Módulos)
-- Aqui você cadastra, por exemplo: ID 1 = Contas a Receber, ID 2 = Contas a Pagar
CREATE TABLE IF NOT EXISTS permissoes_disponiveis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_modulo VARCHAR(100) NOT NULL,
    descricao VARCHAR(255)
);

-- 4. Tabela de Vínculo (Controle de IDs por Usuário)
-- Esta tabela define quais IDs de permissão cada usuário possui
CREATE TABLE IF NOT EXISTS usuario_permissoes (
    id_usuario INT,
    id_permissao INT,
    PRIMARY KEY (id_usuario, id_permissao),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (id_permissao) REFERENCES permissoes_disponiveis(id) ON DELETE CASCADE
);

-- 5. Inserção de Dados Iniciais de Teste
INSERT INTO setores (nome) VALUES ('GERÊNCIA'), ('FINANCEIRO'), ('OPERACIONAL');

INSERT INTO permissoes_disponiveis (nome_modulo, descricao) 
VALUES ('FIN_REC', 'Acesso ao Contas a Receber'), 
       ('FIN_PAG', 'Acesso ao Contas a Pagar');
