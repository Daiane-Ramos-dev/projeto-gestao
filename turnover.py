import streamlit as st
import pandas as pd

if "page" not in st.session_state:
    st.session_state.page = "homepage"  # ou qualquer nome padrão

if "username" not in st.session_state or st.session_state.username is None:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.session_state.page = "login"
    st.rerun()

# Carregar o dataframe
@st.cache
def load_data():
    return pd.read_excel('turnover.xlsx')

# Função de cálculo de turnover
def calcular_turnover(df, ano=None, mes=None):
    # Excluir funcionários com CODSITUACAO igual a "I"
    df = df[df['CODSITUACAO'] != "I"]

    # Remover demissões desconsideradas
    df = df[df['MOTIVO_DEMISSAO'] != "Término do Contrato de Estágio"]

    # Garantir conversão correta para datas
    df['DATAADMISSAO'] = pd.to_datetime(df['DATAADMISSAO'], errors='coerce')
    df['DATADEMISSAO'] = pd.to_datetime(df['DATADEMISSAO'], errors='coerce')

    # Inicializando as variáveis de turnover para soma
    turnover_total = 0
    n_admissoes_total = 0
    n_demissoes_total = 0
    n_ativos_total = 0

    # Caso mes seja uma lista de múltiplos meses
    if isinstance(mes, list):
        for m in mes:
            # Definindo o início e fim do mês
            data_inicio = pd.to_datetime(f"{ano}-{m:02d}-01")
            data_fim = data_inicio + pd.DateOffset(months=1)

            # Admissões no mês
            admissoes = df[(df['DATAADMISSAO'] >= data_inicio) & (df['DATAADMISSAO'] < data_fim)]

            # Demissões no mês
            demissoes = df[(df['DATADEMISSAO'] >= data_inicio) & (df['DATADEMISSAO'] < data_fim)]

            # Funcionários ativos no mês
            ativos = df[
                (df['DATAADMISSAO'] <= data_fim) &  # Admitidos até o final do mês
                ((df['DATADEMISSAO'].isna()) | (df['DATADEMISSAO'] >= data_fim))  # Sem data de demissão ou com data posterior ao final do mês
            ]

            # Agregando os resultados dos meses
            n_admissoes_total += admissoes.shape[0]
            n_demissoes_total += demissoes.shape[0]
            n_ativos_total += ativos.shape[0]

        # Calculando turnover com base na soma dos valores
        if n_ativos_total > 0:
            turnover = ((n_admissoes_total + n_demissoes_total) / 2) / n_ativos_total * 100
        else:
            turnover = 0
    else:
        # Caso tenha sido selecionado apenas um mês
        data_inicio = pd.to_datetime(f"{ano}-{mes:02d}-01")
        data_fim = data_inicio + pd.DateOffset(months=1)

        # Admissões no mês
        admissoes = df[(df['DATAADMISSAO'] >= data_inicio) & (df['DATAADMISSAO'] < data_fim)]

        # Demissões no mês
        demissoes = df[(df['DATADEMISSAO'] >= data_inicio) & (df['DATADEMISSAO'] < data_fim)]

        # Funcionários ativos no mês
        ativos = df[
            (df['DATAADMISSAO'] <= data_fim) &  # Admitidos até o final do mês
            ((df['DATADEMISSAO'].isna()) | (df['DATADEMISSAO'] >= data_fim))  # Sem data de demissão ou com data posterior ao final do mês
        ]

        # Número de funcionários ativos
        n_admissoes = admissoes.shape[0]
        n_demissoes = demissoes.shape[0]
        n_ativos = ativos.shape[0]

        # Calcular turnover para um único mês
        if n_ativos > 0:
            turnover = ((n_admissoes + n_demissoes) / 2) / n_ativos * 100
        else:
            turnover = 0

    return turnover, n_admissoes_total, n_demissoes_total, n_ativos_total

# Função principal para mostrar os filtros e resultados no Streamlit
def main():
    # Carregando os dados
    df = load_data()

    # Filtros
    st.title('👥Cálculo de Turnover')
    st.markdown("<hr>", unsafe_allow_html=True)

    # Filtro para SECAO com múltiplas seleções
    secao_selecionada = st.multiselect(
        'Selecione as Seções',
        options=df['SECAO'].unique(),
        default=df['SECAO'].unique()  # Definindo o valor padrão como todas as seções
    )

    # Obter o último ano disponível com base nas colunas DATAADMISSAO e DATADEMISSAO
    anos_disponiveis = pd.to_datetime(df[['DATAADMISSAO', 'DATADEMISSAO']].stack(), errors='coerce').dt.year.unique()
    ano_maximo = max(anos_disponiveis)

    # Filtro para Ano com o último ano disponível como padrão
    ano_selecionado = st.selectbox(
        'Selecione o Ano',
        options=sorted(anos_disponiveis),
        index=list(sorted(anos_disponiveis)).index(ano_maximo)  # Definindo o último ano como padrão
    )

    # Filtro para Mês com múltiplas seleções
    meses_selecionados = st.multiselect(
        'Selecione os Meses',
        options=range(1, 13),
        default=range(1, 13)  # Definindo o valor padrão como todos os meses
    )

    # Filtrando o DataFrame com base na seção, ano e meses selecionados
    df_filtrado = df[df['SECAO'].isin(secao_selecionada)]

    # Calcular o turnover (agora com meses múltiplos)
    turnover, admissoes, demissoes, n_ativos = calcular_turnover(df_filtrado, ano=ano_selecionado, mes=meses_selecionados)

    # Mostrar resultados principais em cards
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    card_css = """
    <div style="
        background-color:{bg_color};
        border-radius: 12px;
        height: 100px;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    ">
        <div style="text-align: center;">
            <p style='margin: 0; font-size: 16px; color: {title_color}; font-weight: 600;'>{title}</p>
            <p style='margin: 5px 0 0 0; font-size: 28px; color: {value_color}; font-weight: bold;'>{value}</p>
        </div>
    </div>
    """

    with col1:
        st.markdown(card_css.format(
            bg_color="#e9f7ef",
            title="Ativos",
            title_color="#28a745",
            value=f"{n_ativos}",
            value_color="#28a745"
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(card_css.format(
            bg_color="#e9f7ef",
            title="Admissões",
            title_color="#17a2b8",
            value=f"{admissoes}",
            value_color="#17a2b8"
        ), unsafe_allow_html=True)

    with col3:
        st.markdown(card_css.format(
            bg_color="#e9f7ef",
            title="Demissões",
            title_color="#ffc107",
            value=f"{demissoes}",
            value_color="#ffc107"
        ), unsafe_allow_html=True)

    with col4:
        st.markdown(card_css.format(
            bg_color="#f8d7da",
            title="Turnover",
            title_color="#dc3545",
            value=f"{turnover:.2f}%",
            value_color="#dc3545"
        ), unsafe_allow_html=True)

if __name__ == "__main__":
    main()





















