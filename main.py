import streamlit as st
import base64
from data_loader import verificar_usuario, adicionar_usuario  # supondo que existam

# --- Configuração da Página ---
st.set_page_config(
    page_title="Gestão de Indicadores",
    layout="centered",  # use "wide" se quiser ocupar toda a largura no desktop
    initial_sidebar_state="collapsed"  # esconde o menu lateral no celular
)

# --- Estilos Personalizados (CSS) ---
st.markdown("""
    <style>
        input, button, .stTextInput > div > div > input {
            font-size: 16px !important;
        }
        .stButton>button {
            padding: 0.5em 1em;
            font-size: 16px;
        }
        img {
            max-width: 100%;
            height: auto;
        }
    </style>
""", unsafe_allow_html=True)

# --- Inicialização de Estado ---
if "page" not in st.session_state:
    st.session_state.page = "homepage"
if "username" not in st.session_state:
    st.session_state.username = None

# --- Funções Auxiliares ---
def image_to_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def logout():
    st.session_state.username = None
    st.session_state.page = "homepage"
    st.rerun()

# --- Página Inicial ---
def homepage():
    st.title("Painel de Indicadores 📊")
    st.markdown("#### Bem-vindo(a)! Acompanhe os principais indicadores da sua equipe.")

    st.image("imagens/Business Plan-cuate.png", width=300)

    if st.button("🚀 Acessar o Sistema"):
        st.session_state.page = "login"
        st.rerun()

# --- Página de Login ---
def login_page():
    st.title("🔐 Login")

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

# --- Página de Cadastro ---
def cadastro_usuario_page():
    st.title("📝 Cadastro de Novo Usuário")

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

# --- Sistema com Sidebar ---
def sistema():
    st.sidebar.title(f"👤 Bem-vindo, {st.session_state.username}")
    page = st.sidebar.radio("Escolha a página:", [
        "Matriz de Polivalência", "Turnover", "Absenteísmo"
    ])
    st.sidebar.button("🔒 Logout", on_click=logout)

    if page == "Matriz de Polivalência":
        import matriz_polivalencia
        matriz_polivalencia.main()
    elif page == "Turnover":
        import turnover
        turnover.main()
    elif page == "Absenteísmo":
        import absenteismo
        absenteismo.main()

# --- Controle de Navegação ---
if st.session_state.username:
    sistema()
else:
    if st.session_state.page == "homepage":
        homepage()
    elif st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "cadastro":
        cadastro_usuario_page()









