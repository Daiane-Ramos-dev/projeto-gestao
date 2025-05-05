import streamlit as st

def main():
    # Verifica se o usuário está logado
    if 'username' in st.session_state and st.session_state.username:
        # Caso o usuário esteja logado, leva direto para a página da matriz de polivalência
        st.session_state.page = "matriz_polivalencia"
        st.write(f"Bem-vindo(a), {st.session_state.username}!")
        st.write("Você já está logado, redirecionando para a Matriz de Polivalência...")
        st.rerun()  # Garante que a página seja redirecionada imediatamente
        return  # Impede o carregamento do conteúdo da homepage

       
    if st.button("Acessar o Sistema"):
        # Redireciona para a página de login
        st.session_state.page = "login"
        st.rerun()


    
    









