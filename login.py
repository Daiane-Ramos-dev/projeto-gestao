import bcrypt
import streamlit as st
from data_loader import verificar_usuario  # Certifique-se que essa retorna (bool, primeiro_login)
from data_loader import conectar_db

# Página de Login
def main():
    if 'username' in st.session_state and st.session_state.username:
        st.session_state.page = "matriz_polivalencia"
        return

    st.title("Login")
    with st.form("login_form"):
        nome_usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")

        if submit:
            if not nome_usuario or not senha:
                st.error("Usuário ou senha não podem estar vazios.")
            else:
                sucesso, primeiro_login = verificar_usuario(nome_usuario, senha)

                if sucesso:
                    st.session_state.username = nome_usuario
                    if primeiro_login == 1:  # Se for o primeiro login
                        st.session_state.page = "trocar_senha"
                    else:
                        st.session_state.page = "matriz_polivalencia"
                    st.success("Login realizado com sucesso!")
                    st.experimental_rerun()  # Usar experimental_rerun para redirecionamento
                else:
                    st.error("Usuário não encontrado ou senha incorreta.")

# Página de troca de senha
def trocar_senha_page():
    st.title("Trocar Senha")

    nova_senha = st.text_input("Nova senha", type="password")
    confirmar = st.text_input("Confirme a nova senha", type="password")

    if st.button("Salvar"):
        if nova_senha == confirmar and nova_senha.strip() != "":
            # Atualiza a senha no banco de dados
            conn = conectar_db()
            c = conn.cursor()
            nova_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt())
            c.execute(""" 
                UPDATE usuarios 
                SET senha = ?, primeiro_login = 0 
                WHERE nome = ? 
            """, (nova_hash, st.session_state.username))
            conn.commit()
            conn.close()

            st.success("Senha atualizada com sucesso!")
            st.session_state.page = "matriz_polivalencia"
            st.experimental_rerun()  # Usar experimental_rerun para redirecionamento
        else:
            st.error("As senhas não coincidem ou estão em branco.")

# Fluxo principal com controle de páginas
def controle_pagina():
    if 'page' not in st.session_state:
        st.session_state.page = "login"

    if st.session_state.page == "login":
        main()
    elif st.session_state.page == "trocar_senha":
        trocar_senha_page()
    elif st.session_state.page == "matriz_polivalencia":
        # Aqui você pode adicionar o conteúdo da página da Matriz de Polivalência.
        st.title("Matriz de Polivalência")
        st.write("Bem-vindo à Matriz de Polivalência!")

# Chamada da função de controle
if __name__ == "__main__":
    controle_pagina()












