-- ============================================
-- TABELA: ESTABELECIMENTO
-- ============================================

CREATE TABLE estabelecimento (
    id_estabelecimento INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    razao_social VARCHAR(150) NOT NULL,
    cnpj CHAR(14) NOT NULL UNIQUE,
    tipo_estabelecimento VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    endereco VARCHAR(150) NOT NULL,
    complemento VARCHAR(100),
    bairro VARCHAR(80),
    cidade VARCHAR(80) NOT NULL,
    cep CHAR(8),
    responsavel VARCHAR(100) NOT NULL,
    status_cadastro BOOLEAN NOT NULL DEFAULT TRUE,
    data_cadastro DATE NOT NULL
);


-- ============================================
-- TABELA: CONSUMIDOR
-- ============================================

CREATE TABLE consumidor (
    id_consumidor INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    cpf CHAR(11) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    endereco VARCHAR(150),
    cidade VARCHAR(80),
    cep CHAR(8),
    data_cadastro DATE NOT NULL
);


-- ============================================
-- TABELA: INSTITUICAO
-- ============================================

CREATE TABLE instituicao (
    id_instituicao INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    cnpj CHAR(14) UNIQUE,
    responsavel VARCHAR(100),
    telefone VARCHAR(20),
    email VARCHAR(100),
    endereco VARCHAR(150),
    cidade VARCHAR(80),
    status BOOLEAN DEFAULT TRUE
);


-- ============================================
-- TABELA: EXCEDENTE
-- ============================================

CREATE TABLE excedente (
    id_excedente INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_estabelecimento INT NOT NULL,
    nome_alimento VARCHAR(120) NOT NULL,
    categoria_alimento VARCHAR(60),
    descricao TEXT,
    quantidade DECIMAL(10,2) NOT NULL,
    unidade_medida VARCHAR(20) NOT NULL,
    data_producao DATE,
    validade DATE NOT NULL,
    condicao_alimento VARCHAR(50),
    temperatura_conservacao DECIMAL(5,2),
    embalagem VARCHAR(60),
    data_publicacao TIMESTAMP NOT NULL,
    horario_disponibilidade TIMESTAMP,
    urgencia VARCHAR(20),
    destino VARCHAR(30),
    status VARCHAR(30) DEFAULT 'Disponível',
    observacoes TEXT,

    CONSTRAINT fk_excedente_estabelecimento
        FOREIGN KEY (id_estabelecimento)
        REFERENCES estabelecimento(id_estabelecimento)
);


-- ============================================
-- TABELA: CLASSIFICACAO
-- ============================================

CREATE TABLE classificacao (
    id_classificacao INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_excedente INT NOT NULL,
    aptidao_consumo BOOLEAN NOT NULL,
    destino VARCHAR(30) NOT NULL,
    prioridade VARCHAR(20),
    justificativa TEXT,
    data_classificacao TIMESTAMP NOT NULL,
    responsavel_classificacao VARCHAR(100),
    observacoes TEXT,

    CONSTRAINT fk_classificacao_excedente
        FOREIGN KEY (id_excedente)
        REFERENCES excedente(id_excedente)
);


-- ============================================
-- TABELA: OFERTA
-- ============================================

CREATE TABLE oferta (
    id_oferta INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_excedente INT NOT NULL,
    id_estabelecimento INT NOT NULL,

    nome_oferta VARCHAR(120) NOT NULL,
    descricao TEXT,

    quantidade_disponivel DECIMAL(10,2) NOT NULL,

    preco_original DECIMAL(10,2),
    preco_desconto DECIMAL(10,2),

    percentual_desconto DECIMAL(5,2),

    data_inicio DATE,
    data_fim DATE,

    horario_inicio_retirada TIME,
    horario_fim_retirada TIME,

    localizacao_retirada VARCHAR(150),

    status VARCHAR(30) DEFAULT 'Ativa',

    CONSTRAINT fk_oferta_excedente
        FOREIGN KEY (id_excedente)
        REFERENCES excedente(id_excedente),

    CONSTRAINT fk_oferta_estabelecimento
        FOREIGN KEY (id_estabelecimento)
        REFERENCES estabelecimento(id_estabelecimento)
);


-- ============================================
-- TABELA: RESERVA
-- ============================================

CREATE TABLE reserva (
    id_reserva INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id_consumidor INT NOT NULL,
    id_oferta INT NOT NULL,

    quantidade DECIMAL(10,2) NOT NULL,

    valor_unitario DECIMAL(10,2),
    valor_total DECIMAL(10,2),

    data_reserva DATE NOT NULL,
    horario_reserva TIME,

    horario_retirada TIME,

    codigo_retirada VARCHAR(30) UNIQUE,

    status VARCHAR(30) DEFAULT 'Reservada',

    data_cancelamento DATE,

    motivo_cancelamento TEXT,

    confirmacao_retirada BOOLEAN DEFAULT FALSE,

    CONSTRAINT fk_reserva_consumidor
        FOREIGN KEY (id_consumidor)
        REFERENCES consumidor(id_consumidor),

    CONSTRAINT fk_reserva_oferta
        FOREIGN KEY (id_oferta)
        REFERENCES oferta(id_oferta)
);


-- ============================================
-- TABELA: DOACAO
-- ============================================

CREATE TABLE doacao (
    id_doacao INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id_excedente INT NOT NULL,
    id_estabelecimento INT NOT NULL,
    id_instituicao INT NOT NULL,

    alimento VARCHAR(120),

    quantidade DECIMAL(10,2),

    unidade_medida VARCHAR(20),

    condicao_alimento VARCHAR(50),

    validade DATE,

    data_disponibilizacao DATE,

    data_aceite DATE,

    data_retirada DATE,

    data_entrega DATE,

    responsavel_retirada VARCHAR(100),

    status VARCHAR(30) DEFAULT 'Pendente',

    CONSTRAINT fk_doacao_excedente
        FOREIGN KEY (id_excedente)
        REFERENCES excedente(id_excedente),

    CONSTRAINT fk_doacao_estabelecimento
        FOREIGN KEY (id_estabelecimento)
        REFERENCES estabelecimento(id_estabelecimento),

    CONSTRAINT fk_doacao_instituicao
        FOREIGN KEY (id_instituicao)
        REFERENCES instituicao(id_instituicao)
);


-- ============================================
-- TABELA: DESCARTE
-- ============================================

CREATE TABLE descarte (
    id_descarte INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    id_excedente INT NOT NULL,

    destino VARCHAR(80) NOT NULL,

    motivo TEXT,

    data_descarte TIMESTAMP NOT NULL,

    responsavel VARCHAR(100),

    observacoes TEXT,

    CONSTRAINT fk_descarte_excedente
        FOREIGN KEY (id_excedente)
        REFERENCES excedente(id_excedente)
);


-- ============================================
-- FIM DO SCRIPT
-- ============================================
