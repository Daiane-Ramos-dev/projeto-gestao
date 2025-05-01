import streamlit as st

def main():
    # Verifica se o usuário está logado
    if 'username' in st.session_state and st.session_state.username:
        st.session_state.page = "matriz_polivalencia"
        return  # Impede que o conteúdo da homepage seja carregado

    st.title("Homepage")
    if st.button("Acessar o Sistema"):
        st.session_state.page = "login"
        st.rerun()
    
    









