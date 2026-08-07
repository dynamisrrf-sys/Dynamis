CREATE TABLE Usuario (
    id_usuario SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    tipo_usuario VARCHAR(30) NOT NULL,
    data_cadastro TIMESTAMP NOT NULL
);

CREATE TABLE Estabelecimento (
    id_estabelecimento SERIAL PRIMARY KEY,
    id_usuario INT NOT NULL,
    nome_fantasia VARCHAR(100) NOT NULL,
    cnpj CHAR(18) UNIQUE,
    categoria VARCHAR(50) NOT NULL,
    endereco VARCHAR(255) NOT NULL,
    telefone VARCHAR(20) NOT NULL,

    CONSTRAINT fk_estabelecimento_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES Usuario(id_usuario)
);

CREATE TABLE Alimento (
    id_alimento SERIAL PRIMARY KEY,
    id_estabelecimento INT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    descricao VARCHAR(500),
    quantidade FLOAT NOT NULL,
    unidade VARCHAR(20) NOT NULL,
    validade DATE NOT NULL,
    status VARCHAR(30) NOT NULL,
    foto VARCHAR(255),

    CONSTRAINT fk_alimento_estabelecimento
        FOREIGN KEY (id_estabelecimento)
        REFERENCES Estabelecimento(id_estabelecimento)
);

CREATE TABLE Solicitacao (
    id_solicitacao SERIAL PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_alimento INT NOT NULL,
    data_solicitacao TIMESTAMP NOT NULL,
    status VARCHAR(30) NOT NULL,
    observacao VARCHAR(500),

    CONSTRAINT fk_solicitacao_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES Usuario(id_usuario),

    CONSTRAINT fk_solicitacao_alimento
        FOREIGN KEY (id_alimento)
        REFERENCES Alimento(id_alimento)
);

CREATE TABLE Retirada (
    id_retirada SERIAL PRIMARY KEY,
    id_solicitacao INT NOT NULL,
    data_retirada TIMESTAMP NOT NULL,
    horario TIME NOT NULL,
    confirmado BOOLEAN NOT NULL,

    CONSTRAINT fk_retirada_solicitacao
        FOREIGN KEY (id_solicitacao)
        REFERENCES Solicitacao(id_solicitacao)
);

CREATE TABLE Destinacao (
    id_destinacao SERIAL PRIMARY KEY,
    id_alimento INT NOT NULL,
    tipo_destino VARCHAR(30) NOT NULL,
    data_destino TIMESTAMP NOT NULL,
    observacao VARCHAR(500),

    CONSTRAINT fk_destinacao_alimento
        FOREIGN KEY (id_alimento)
        REFERENCES Alimento(id_alimento)
);

CREATE TABLE Pontuacao (
    id_pontuacao SERIAL PRIMARY KEY,
    id_usuario INT NOT NULL,
    pontos INT NOT NULL,
    nivel VARCHAR(30) NOT NULL,
    ultima_atualizacao TIMESTAMP NOT NULL,

    CONSTRAINT fk_pontuacao_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES Usuario(id_usuario)
);