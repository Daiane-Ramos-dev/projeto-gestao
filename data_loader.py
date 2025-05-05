import streamlit as st
import pandas as pd
import sqlite3
import os
import altair as alt
import bcrypt
from datetime import datetime

# ========================= Funções de carregamento de Excel =========================

@st.cache_data
def absent_dados():
    return pd.read_excel("ABSENT.xlsx")

def turnover_dados():
    return pd.read_excel("turnover.xlsx")

# ========================= Conexão com Banco de Dados =========================
def conectar_db():
    pasta_db = "database"
    if not os.path.exists(pasta_db):
        os.makedirs(pasta_db)  # Cria a pasta se não existir

    db_path = os.path.join(pasta_db, "bancodados.db")
    conn = sqlite3.connect(db_path, timeout=30)
    return conn

# ========================= Criação das Tabelas =========================
def criar_tabelas():
    conn = conectar_db()
    c = conn.cursor()

    # Tabela de funções
    c.execute("""
    CREATE TABLE IF NOT EXISTS funcoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL
    )
    """)

    # Tabela de colaboradores
    c.execute("""
    CREATE TABLE IF NOT EXISTS colaboradores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL
    )
    """)

    # Tabela de habilidades
    c.execute("""
    CREATE TABLE IF NOT EXISTS habilidades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        colaborador_id INTEGER NOT NULL,
        funcao_id INTEGER NOT NULL,
        nivel INTEGER NOT NULL,
        data_atualizacao TEXT NOT NULL,
        FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id),
        FOREIGN KEY (funcao_id) REFERENCES funcoes(id)
    )
    """)

    # Tabela de usuarios (corrigido para usar BLOB e adicionado o campo admin)
    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL,
        senha BLOB NOT NULL,
        admin INTEGER DEFAULT 0,  -- Adicionando a coluna admin
        primeiro_login INTEGER DEFAULT 1
    )
    """)

    conn.commit()
    conn.close()

# ========================= Funções CRUD =========================
def adicionar_funcao_db(funcao):
    conn = conectar_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO funcoes (nome) VALUES (?)", (funcao,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

def remover_restricao_unique():
    conn = conectar_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS colaboradores_novo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL
    )
    """)
    c.execute("INSERT INTO colaboradores_novo (id, nome) SELECT id, nome FROM colaboradores")
    c.execute("DROP TABLE colaboradores")
    c.execute("ALTER TABLE colaboradores_novo RENAME TO colaboradores")

    conn.commit()
    conn.close()

def adicionar_colaborador_db(nome, habilidades):
    conn = conectar_db()
    c = conn.cursor()

    c.execute("INSERT INTO colaboradores (nome) VALUES (?)", (nome,))
    colaborador_id = c.lastrowid
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for funcao, nivel in habilidades.items():
        c.execute("""
        INSERT INTO habilidades (colaborador_id, funcao_id, nivel, data_atualizacao)
        VALUES (?, (SELECT id FROM funcoes WHERE nome = ?), ?, ?)
        """, (colaborador_id, funcao, nivel, data_atual))

    conn.commit()
    conn.close()

def atualizar_colaborador_db(colaborador_id, habilidades):
    conn = conectar_db()
    c = conn.cursor()
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for funcao, nivel in habilidades.items():
        c.execute("""
        INSERT INTO habilidades (colaborador_id, funcao_id, nivel, data_atualizacao)
        VALUES (?, (SELECT id FROM funcoes WHERE nome = ?), ?, ?)
        """, (colaborador_id, funcao, nivel, data_atual))

    conn.commit()
    conn.close()

def excluir_colaborador_db(colaborador_id):
    conn = conectar_db()
    c = conn.cursor()
    c.execute("DELETE FROM habilidades WHERE colaborador_id = ?", (colaborador_id,))
    c.execute("DELETE FROM colaboradores WHERE id = ?", (colaborador_id,))
    conn.commit()
    conn.close()

def get_funcoes():
    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT nome FROM funcoes")
    funcoes = [row[0] for row in c.fetchall()]
    conn.close()
    return funcoes

def get_colaboradores():
    conn = conectar_db()
    c = conn.cursor()
    c.execute("""
    SELECT c.id, c.nome, f.nome, h.nivel 
    FROM colaboradores c
    JOIN habilidades h ON c.id = h.colaborador_id
    JOIN funcoes f ON h.funcao_id = f.id
    """)
    colaboradores = c.fetchall()
    conn.close()
    return colaboradores

def get_historico_habilidades(colaborador_id):
    conn = conectar_db()
    c = conn.cursor()
    c.execute("""
        SELECT f.nome, h.nivel, h.data_atualizacao
        FROM habilidades h
        JOIN funcoes f ON f.id = h.funcao_id
        WHERE h.colaborador_id = ?
        ORDER BY h.data_atualizacao
    """, (colaborador_id,))
    resultado = c.fetchall()
    conn.close()
    return resultado

# Adiciona um novo usuário
def adicionar_usuario(nome, senha, admin=False):
    conn = conectar_db()
    c = conn.cursor()
    try:
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        c.execute("INSERT INTO usuarios (nome, senha, admin, primeiro_login) VALUES (?, ?, ?, ?)", 
                  (nome, senha_hash, 1 if admin else 0, 1))
        conn.commit()
    except sqlite3.IntegrityError:
        st.error("Usuário já existe.")
    finally:
        conn.close()

# Função para verificar se o usuário é admin
def is_usuario_admin(username):
    conn = conectar_db()  # Conectar ao banco de dados
    c = conn.cursor()
    c.execute("SELECT admin FROM usuarios WHERE nome = ?", (username,))
    resultado = c.fetchone()
    conn.close()

    if resultado:
        # Se admin for 1, o usuário é admin
        return resultado[0] == 1
    return False

# Função para verificar se o usuário existe e a senha está correta
def verificar_usuario(nome_usuario, senha):
    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT senha, primeiro_login FROM usuarios WHERE nome = ?", (nome_usuario,))
    usuario = c.fetchone()
    conn.close()

    if usuario and bcrypt.checkpw(senha.encode('utf-8'), usuario[0]):
        return True, usuario[1]  # Retorna se o login foi bem-sucedido e se é o primeiro login
    return False, None


