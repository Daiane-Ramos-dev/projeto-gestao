import streamlit as st
import pandas as pd
import sqlite3
import os
import altair as alt
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

    # NOVA TABELA: Usuários
    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL
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
def adicionar_usuario(nome, senha):
    conn = conectar_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO usuarios (nome, senha) VALUES (?, ?)", (nome, senha))
        conn.commit()
    except sqlite3.IntegrityError:
        st.error("Usuário já existe.")
    finally:
        conn.close()

# Verifica login
def verificar_usuario(nome, senha):
    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE nome = ? AND senha = ?", (nome, senha))
    usuario = c.fetchone()
    conn.close()
    return usuario

# ========================= Streamlit UI =========================
def adicionar_funcao():
    st.header("Adicionar Funções")
    funcao = st.text_input("Nome da Função")
    if st.button("Adicionar Função"):
        if funcao:
            adicionar_funcao_db(funcao)
            st.success(f"Função '{funcao}' adicionada com sucesso!")
        else:
            st.warning("Digite o nome da função.")

def adicionar_colaborador():
    st.header("Adicionar/Atualizar Colaboradores e Habilidades")

    colaboradores = get_colaboradores()

    if colaboradores:
        colaborador_selecionado = st.selectbox("Selecione um Colaborador para Atualizar ou Excluir",
                                               options=[colaborador[1] for colaborador in colaboradores])

        if colaborador_selecionado:
            funcoes = get_funcoes()
            habilidades = {}

            for f in funcoes:
                nivel_atual = next((nivel for colaborador_id, nome, funcao, nivel in colaboradores
                                    if nome == colaborador_selecionado and funcao == f), None)
                habilidades[f] = nivel_atual if nivel_atual is not None else 0

            for f in funcoes:
                habilidades[f] = st.selectbox(f"Nível em '{f}' (0-5)", options=[0, 1, 2, 3, 4, 5],
                                              index=habilidades[f], key=f"{colaborador_selecionado}_{f}")

            if st.button(f"Atualizar Colaborador '{colaborador_selecionado}'"):
                colaborador_id = next((id for id, nome, *_ in colaboradores if nome == colaborador_selecionado), None)
                if colaborador_id:
                    atualizar_colaborador_db(colaborador_id, habilidades)
                    st.success(f"Colaborador '{colaborador_selecionado}' atualizado com sucesso!")

            if st.button(f"Excluir Colaborador '{colaborador_selecionado}'"):
                colaborador_id = next((id for id, nome, *_ in colaboradores if nome == colaborador_selecionado), None)
                if colaborador_id:
                    excluir_colaborador_db(colaborador_id)
                    st.success(f"Colaborador '{colaborador_selecionado}' excluído com sucesso!")
    else:
        st.warning("Nenhum colaborador encontrado. Adicione um colaborador primeiro.")

    novo_colaborador = st.text_input("Nome do Novo Colaborador")

    if novo_colaborador:
        funcoes = get_funcoes()
        habilidades = {}
        for f in funcoes:
            nivel = st.selectbox(f"Nível em '{f}' (0-5)", options=[0, 1, 2, 3, 4, 5], key=f"{novo_colaborador}_{f}")
            habilidades[f] = nivel

        if st.button("Adicionar Novo Colaborador"):
            adicionar_colaborador_db(novo_colaborador, habilidades)
            st.success(f"Colaborador '{novo_colaborador}' adicionado com sucesso!")

def exibir_matriz():
    colaboradores = get_colaboradores()

    if colaboradores:
        st.header("Matriz de Polivalência")

        data = {"nome": [], "função": [], "nível": []}
        for colaborador_id, nome, funcao, nivel in colaboradores:
            data["nome"].append(nome)
            data["função"].append(funcao)
            data["nível"].append(nivel)

        df = pd.DataFrame(data)
        st.dataframe(df)

        df_melted = df.melt(id_vars=["nome"], var_name="Função", value_name="Nível")

        st.header("Gráfico por Função")
        chart = alt.Chart(df_melted).mark_bar().encode(
            x=alt.X("nome:N", title="Colaborador"),
            y=alt.Y("Nível:Q", title="Nível de Habilidade"),
            color="nome:N",
            tooltip=["nome:N", "Função:N", "Nível:Q"]
        ).properties(
            width=200,
            height=300
        ).facet(
            column="Função:N"
        )
        st.altair_chart(chart, use_container_width=True)

    

# ========================= Streamlit Principal =========================
def main():
    st.title("Matriz de Polivalência")
    criar_tabelas()
    remover_restricao_unique()
    adicionar_funcao()
    adicionar_colaborador()
    exibir_matriz()

if __name__ == "__main__":
    main()
