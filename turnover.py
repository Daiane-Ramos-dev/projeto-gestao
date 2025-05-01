import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Carregar os dados com cache moderno
@st.cache_data
def load_data():
    return pd.read_excel('turnover.xlsx')

# Função de cálculo de turnover
def calcular_turnover(df, ano=None, mes=None):
    df = df[df['CODSITUACAO'] != "I"]
    df = df[df['MOTIVO_DEMISSAO'] != "Término do Contrato de Estágio"]
    df['DATAADMISSAO'] = pd.to_datetime(df['DATAADMISSAO'], errors='coerce')
    df['DATADEMISSAO'] = pd.to_datetime(df['DATADEMISSAO'], errors='coerce')

    # Inicializando os totais
    n_admissoes_total = 0
    n_demissoes_total = 0
    n_ativos_total = 0
    turnover_por_mes = {}

    # Verificando se meses são múltiplos ou um único mês
    if isinstance(mes, list):
        # Calcular para todos os meses selecionados
        for m in mes:
            data_inicio = pd.to_datetime(f"{ano}-{m:02d}-01")
            data_fim = data_inicio + pd.DateOffset(months=1)

            admissoes = df[(df['DATAADMISSAO'] >= data_inicio) & (df['DATAADMISSAO'] < data_fim)]
            demissoes = df[(df['DATADEMISSAO'] >= data_inicio) & (df['DATADEMISSAO'] < data_fim)]
            ativos = df[
                (df['DATAADMISSAO'] <= data_fim) &
                ((df['DATADEMISSAO'].isna()) | (df['DATADEMISSAO'] >= data_fim))
            ]

            n_admissoes_total += admissoes.shape[0]
            n_demissoes_total += demissoes.shape[0]
            n_ativos_total += ativos.shape[0]

            # Calculando o turnover por mês
            if n_ativos_total > 0:
                turnover_mes = ((n_admissoes_total + n_demissoes_total) / 2) / n_ativos_total * 100
            else:
                turnover_mes = 0

            turnover_por_mes[m] = turnover_mes
    else:
        # Caso tenha sido selecionado apenas um mês
        m = mes
        data_inicio = pd.to_datetime(f"{ano}-{m:02d}-01")
        data_fim = data_inicio + pd.DateOffset(months=1)

        admissoes = df[(df['DATAADMISSAO'] >= data_inicio) & (df['DATAADMISSAO'] < data_fim)]
        demissoes = df[(df['DATADEMISSAO'] >= data_inicio) & (df['DATADEMISSAO'] < data_fim)]
        ativos = df[
            (df['DATAADMISSAO'] <= data_fim) &
            ((df['DATADEMISSAO'].isna()) | (df['DATADEMISSAO'] >= data_fim))
        ]

        n_admissoes_total += admissoes.shape[0]
        n_demissoes_total += demissoes.shape[0]
        n_ativos_total += ativos.shape[0]

        # Calculando o turnover
        if n_ativos_total > 0:
            turnover = ((n_admissoes_total + n_demissoes_total) / 2) / n_ativos_total * 100
        else:
            turnover = 0

        turnover_por_mes[m] = turnover

    return turnover_por_mes, n_ativos_total, n_admissoes_total, n_demissoes_total

# Função principal para Streamlit
def main():
    df = load_data()

    st.title('👥Cálculo de Turnover')
    st.markdown("<hr>", unsafe_allow_html=True)

    # Filtro de Seções
    secao_selecionada = st.multiselect(
        'Selecione as Seções',
        options=df['SECAO'].unique(),
        default=df['SECAO'].unique()  # Definindo o valor padrão como todas as seções
    )

    # Filtro de Ano
    anos_disponiveis = pd.to_datetime(df[['DATAADMISSAO', 'DATADEMISSAO']].stack(), errors='coerce').dt.year.dropna().unique()
    ano_maximo = max(anos_disponiveis)
    ano_selecionado = st.selectbox(
        'Selecione o Ano',
        options=sorted(anos_disponiveis),
        index=list(sorted(anos_disponiveis)).index(ano_maximo)
    )

    # Filtro de Mês(es)
    meses_selecionados = st.multiselect(
        'Selecione os Meses',
        options=range(1, 13),
        default=range(1, 13)
    )

    # Verifica se algum mês foi selecionado
    if not meses_selecionados:
        st.warning("Por favor, selecione ao menos um mês para exibir os dados.")
        return

    # Filtrando o DataFrame com base na seção, ano e meses selecionados
    df_filtrado = df[df['SECAO'].isin(secao_selecionada)]

    # Calcular o turnover
    turnover_por_mes, n_ativos, n_admissoes, n_demissoes = calcular_turnover(df_filtrado, ano=ano_selecionado, mes=meses_selecionados)

    # Exibir resultados dependendo do número de meses selecionados
    if len(meses_selecionados) == 1:
        # Exibir os cards se apenas um mês for selecionado
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
                value=f"{n_admissoes}",
                value_color="#17a2b8"
            ), unsafe_allow_html=True)

        with col3:
            st.markdown(card_css.format(
                bg_color="#e9f7ef",
                title="Demissões",
                title_color="#ffc107",
                value=f"{n_demissoes}",
                value_color="#ffc107"
            ), unsafe_allow_html=True)

        with col4:
            st.markdown(card_css.format(
                bg_color="#f8d7da",
                title="Turnover",
                title_color="#dc3545",
                value=f"{turnover_por_mes[meses_selecionados[0]]:.2f}%",
                value_color="#dc3545"
            ), unsafe_allow_html=True)

    else:
        # Estilo para gráficos no tema Dark
        sns.set(style="darkgrid", palette="deep")
        
        # Exibir gráfico de barras sem grades
        data = []
        for m in meses_selecionados:
            data_inicio = pd.to_datetime(f"{ano_selecionado}-{m:02d}-01")
            data_fim = data_inicio + pd.DateOffset(months=1)

            # Agrupando dados por mês
            df_mes = df_filtrado[(df_filtrado['DATAADMISSAO'] <= data_fim) & 
                                 ((df_filtrado['DATADEMISSAO'].isna()) | (df_filtrado['DATADEMISSAO'] >= data_fim))]
            n_ativos_mes = df_mes.shape[0]
            turnover_mes = turnover_por_mes[m]
            data.append([data_inicio.strftime("%b %Y"), n_ativos_mes, turnover_mes])

        df_mes = pd.DataFrame(data, columns=["Mês", "Ativos", "Turnover"])

        # Plotando o gráfico de barras com estilo para tema dark
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x="Mês", y="Turnover", data=df_mes, ax=ax, palette="coolwarm_r")

        # Remover a grade e bordas
        ax.grid(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

        # Remover o eixo Y
        ax.set_ylabel('')

        # Customizar os rótulos e título
        ax.set_title(f"Turnover (%) por Mês", fontsize=16, color="white")
        #ax.set_xlabel("Mês", fontsize=12, color="white")
        ax.tick_params(axis='x', rotation=45, labelcolor="white")
        #ax.tick_params(axis='y', labelcolor="white")
        ax.set_facecolor("#2d2d2d")
        fig.patch.set_facecolor("#2d2d2d")

        # Adicionar valores nas barras (Turnover (%))
        for p in ax.patches:
            ax.annotate(f'{p.get_height():.2f}%', (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', fontsize=10, color='white', xytext=(0, 7),
                        textcoords='offset points')

        st.pyplot(fig)

if __name__ == "__main__":
    main()



























