import streamlit as st
from data_loader import adicionar_usuario  # Função para adicionar um novo usuário

def main():
    st.title("Cadastro de Novo Usuário")

    with st.form("cadastro_form"):
        nome = st.text_input("Nome de usuário")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Cadastrar")

        if submit:
            if nome and senha:
                adicionar_usuario(nome, senha)  # Função para cadastrar o usuário
                st.success(f"Usuário '{nome}' cadastrado com sucesso!")
                st.session_state.page = "login"  # Após o cadastro, redireciona para a página de login
                st.experimental_rerun()  # Atualiza a página para ir para o login
            else:
                st.warning("Por favor, preencha todos os campos.")




