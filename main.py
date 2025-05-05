import streamlit as st
from data_loader import is_usuario_admin
from data_loader import verificar_usuario, adicionar_usuario  # Certifique-se que verificar_usuario retorna (bool, primeiro_login)

# --- Configuração da Página ---
st.set_page_config(
    page_title="Gestão de Indicadores",
    layout="centered",  # Use "wide" se quiser ocupar toda a largura no desktop
    initial_sidebar_state="collapsed"  # Esconde o menu lateral no celular
)

# --- Inicialização de Estado ---
if "page" not in st.session_state:
    st.session_state.page = "homepage"
if "username" not in st.session_state:
    st.session_state.username = None

# --- Funções Auxiliares ---
def logout():
    st.session_state.username = None
    st.session_state.page = "homepage"
    st.rerun()

# --- Página Inicial ---
def homepage():
    st.title("Painel de Indicadores 📊")
    st.markdown("#### Acompanhe os principais indicadores da sua equipe.")
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
            sucesso, primeiro_login = verificar_usuario(nome_usuario, senha)
            if sucesso:
                st.session_state.username = nome_usuario
                if primeiro_login == 1:
                    st.session_state.page = "trocar_senha"
                else:
                    st.session_state.page = "matriz_polivalencia"
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

    if "username" in st.session_state:
        if is_usuario_admin(st.session_state.username):
            if st.button("📋 Gerenciar Usuários (Cadastro)"):
                st.session_state.page = "cadastro"
                st.rerun()
        #else:
            st.warning("Você não tem permissão para cadastrar usuários.")
    else:
        st.warning("Por favor, faça login primeiro.")

# --- Página de Cadastro ---
def cadastro_usuario_page():
    st.title("📝 Cadastro de Novo Usuário")

    with st.form("cadastro_form"):
        nome = st.text_input("Novo usuário")
        senha = st.text_input("Senha", type="password")
        confirmar_senha = st.text_input("Confirme a senha", type="password")
        cadastrar = st.form_submit_button("Cadastrar")

        if cadastrar:
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

# --- Sistema com Sidebar ---
def sistema():
    st.sidebar.title(f"👤 Bem-vindo, {st.session_state.username}")
    page = st.sidebar.radio("Escolha a página:", [
        "Matriz de Polivalência", "Turnover", "Absenteísmo"
    ])
    if st.sidebar.button("🔒 Logout"):
        logout()
        st.rerun()

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










