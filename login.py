import streamlit as st
from data_loader import verificar_usuario  # Supondo que você tenha essa função de verificação

def main():
    # Se o usuário já estiver logado, redireciona automaticamente
    if 'username' in st.session_state and st.session_state.username:
        st.session_state.page = "matriz_polivalencia"
        return  # Impede que o conteúdo da página de login seja carregado

    st.title("Login")
    with st.form("login_form"):
        nome_usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")

        if submit:
            usuario = verificar_usuario(nome_usuario, senha)
            if usuario:
                st.session_state.username = nome_usuario
                st.success("Login realizado com sucesso!")
                st.session_state.page = "matriz_polivalencia"  # Redireciona após login
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")











