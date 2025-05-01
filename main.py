import streamlit as st
from data_loader import verificar_usuario, adicionar_usuario  # supondo que existam
import base64

# --- Inicialização ---
if "page" not in st.session_state:
    st.session_state.page = "homepage"
if "username" not in st.session_state:
    st.session_state.username = None

# --- Funções auxiliares ---
def image_to_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def logout():
    st.session_state.username = None
    st.session_state.page = "homepage"
    st.rerun()

# --- Homepage ---
def homepage():
    st.title("Homepage")
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown("#### Bem-vindo(a) ao painel de indicadores!")
        if st.button("🚀 Acessar o Sistema"):
            st.session_state.page = "login"
            st.rerun()

    with col2:
        image_base64 = image_to_base64("imagens/Business Plan-cuate.png")
        st.markdown(
            f"""<img src="data:image/png;base64,{image_base64}" style="width: 300px; border-radius: 10px;">""",
            unsafe_allow_html=True
        )

# --- Página de login ---
def login_page():
    st.title("Login")
    with st.form("login_form"):
        nome_usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")

        if submit:
            usuario = verificar_usuario(nome_usuario, senha)
            if usuario:
                st.session_state.username = nome_usuario
                st.session_state.page = "matriz_polivalencia"
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

    if st.button("📋 Não tem conta? Cadastre-se aqui"):
        st.session_state.page = "cadastro"
        st.rerun()




# --- Página de cadastro ---
def cadastro_usuario_page():
    st.title("Cadastro de Novo Usuário")

    with st.form("cadastro_form"):
        nome = st.text_input("Novo usuário")
        senha = st.text_input("Senha", type="password")
        cadastrar = st.form_submit_button("Cadastrar")

        if cadastrar:
            if nome and senha:
                adicionar_usuario(nome, senha)
                st.success("Usuário cadastrado com sucesso!")
                st.session_state.page = "login"
                st.rerun()
            else:
                st.warning("Preencha todos os campos.")

# --- Página interna com menu lateral ---
def sistema():
    st.sidebar.title(f"Bem-vindo, {st.session_state.username}")
    page = st.sidebar.radio("Escolha a página:", [
        "Matriz de Polivalência", "Turnover", "Absenteísmo"
    ])
    st.sidebar.button("🔒 Logout", on_click=logout)

    if page == "Matriz de Polivalência":
        import matriz_polivalencia  # Importa 'matriz_polivalencia.py'
        matriz_polivalencia.main()
    elif page == "Turnover":
        import turnover  # Importa 'turnover.py'
        turnover.main()  # Certifique-se que 'main' está definido em 'turnover.py'
    elif page == "Absenteísmo":
        import absenteismo  # Importa o arquivo 'absenteismo.py'
        absenteismo.main()  # Certifique-se que a função 'main' existe em 'absenteismo.py'

# --- Controle de navegação principal ---
if st.session_state.username:
    sistema()
else:
    if st.session_state.page == "homepage":
        homepage()
    elif st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "cadastro":
        cadastro_usuario_page()








