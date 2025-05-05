import streamlit as st
import bcrypt
from data_loader import adicionar_usuario, is_usuario_admin, conectar_db

def verificar_usuario_existente(username):
    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT 1 FROM usuarios WHERE nome = ?", (username,))
    resultado = c.fetchone()
    conn.close()
    return resultado is not None

# --- Página de Cadastro ---
# --- Página de Cadastro ---
def cadastro_usuario_page():
    st.title("📝 Cadastro de Novo Usuário")

    with st.form("cadastro_form"):
        nome = st.text_input("Novo usuário")
        senha = st.text_input("Senha", type="password")
        confirmar_senha = st.text_input("Confirme a senha", type="password")
        cadastrar = st.form_submit_button("Cadastrar")

        if cadastrar:
            # Verificando se os campos foram preenchidos e as senhas coincidem
            if not nome or not senha or not confirmar_senha:
                st.warning("Preencha todos os campos.")
            elif senha != confirmar_senha:
                st.warning("As senhas não coincidem. Tente novamente.")
            else:
                try:
                    adicionar_usuario(nome, senha)  # Adicionando usuário
                    st.success("Usuário cadastrado com sucesso!")
                    st.session_state.page = "login"
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao cadastrar o usuário: {e}")



def main():
    st.title("Cadastro de Novo Usuário")

    # Verifica se o usuário logado é admin
    if "username" not in st.session_state or not is_usuario_admin(st.session_state.username):
        st.error("Acesso negado. Apenas administradores podem acessar esta página.")
        st.stop()

    with st.form("cadastro_form"):
        novo_usuario = st.text_input("Nome do novo usuário:")
        senha = st.text_input("Senha inicial", type="password")
        is_admin = st.checkbox("Este usuário será administrador?", value=False)
        submit = st.form_submit_button("Cadastrar")

        if submit:
            if not novo_usuario or not senha:
                st.warning("Preencha todos os campos.")
            elif verificar_usuario_existente(novo_usuario):
                st.warning("Este nome de usuário já existe.")
            else:
                senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
                adicionar_usuario(novo_usuario, senha_hash, is_admin)
                st.success(f"Usuário '{novo_usuario}' cadastrado com sucesso!")

if __name__ == "__main__":
    main()






