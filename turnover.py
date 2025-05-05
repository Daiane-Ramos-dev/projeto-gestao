import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

@st.cache_data
def load_data():
    return pd.read_excel('turnover.xlsx')

def calcular_turnover(df, ano=None, mes=None):
    df = df[df['CODSITUACAO'] != "I"]
    df = df[df['MOTIVO_DEMISSAO'] != "Término do Contrato de Estágio"]
    df['DATAADMISSAO'] = pd.to_datetime(df['DATAADMISSAO'], errors='coerce')
    df['DATADEMISSAO'] = pd.to_datetime(df['DATADEMISSAO'], errors='coerce')

    turnover_por_mes = {}

    for m in mes:
        data_inicio = pd.to_datetime(f"{ano}-{m:02d}-01")
        data_fim = data_inicio + pd.DateOffset(months=1)

        admissoes = df[(df['DATAADMISSAO'] >= data_inicio) & (df['DATAADMISSAO'] < data_fim)]
        demissoes = df[(df['DATADEMISSAO'] >= data_inicio) & (df['DATADEMISSAO'] < data_fim)]
        ativos = df[
            (df['DATAADMISSAO'] <= data_fim) &
            ((df['DATADEMISSAO'].isna()) | (df['DATADEMISSAO'] >= data_fim))
        ]

        n_admissoes = admissoes.shape[0]
        n_demissoes = demissoes.shape[0]
        n_ativos = ativos.shape[0]

        if n_ativos > 0:
            turnover_mes = ((n_admissoes + n_demissoes) / 2) / n_ativos * 100
        else:
            turnover_mes = 0

        turnover_por_mes[m] = {
            'turnover': turnover_mes,
            'ativos': n_ativos,
            'admissoes': n_admissoes,
            'demissoes': n_demissoes
        }

    return turnover_por_mes

def main():
    df = load_data()

    st.title('👥 Cálculo de Turnover')
    st.markdown("<hr>", unsafe_allow_html=True)

    df['DATAADMISSAO'] = pd.to_datetime(df['DATAADMISSAO'], errors='coerce')
    df['DATADEMISSAO'] = pd.to_datetime(df['DATADEMISSAO'], errors='coerce')

    secao_selecionada = st.multiselect(
        'Selecione as Seções',
        options=df['SECAO'].unique(),
        default=df['SECAO'].unique()
    )

    anos_disponiveis = pd.to_datetime(df[['DATAADMISSAO', 'DATADEMISSAO']].stack(), errors='coerce').dt.year.dropna().unique()
    ano_maximo = max(anos_disponiveis)
    ano_selecionado = st.selectbox(
        'Selecione o Ano',
        options=sorted(anos_disponiveis),
        index=list(sorted(anos_disponiveis)).index(ano_maximo)
    )

    # Define os meses válidos até o mês atual se o ano for o ano atual
    mes_atual = datetime.today().month
    ano_atual = datetime.today().year
    meses_disponiveis = list(range(1, 13 if ano_selecionado < ano_atual else mes_atual + 1))

    meses_selecionados = st.multiselect(
        'Selecione os Meses',
        options=meses_disponiveis,
        default=meses_disponiveis,
        format_func=lambda x: datetime(1900, x, 1).strftime('%B').capitalize()
    )

    if not meses_selecionados:
        st.warning("Por favor, selecione ao menos um mês.")
        return

    df_filtrado = df[df['SECAO'].isin(secao_selecionada)]

    turnover_dict = calcular_turnover(df_filtrado, ano=ano_selecionado, mes=meses_selecionados)

    if len(meses_selecionados) == 1:
        mes = meses_selecionados[0]
        dados = turnover_dict.get(mes, {'ativos': 0, 'admissoes': 0, 'demissoes': 0, 'turnover': 0})

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
            st.markdown(card_css.format(bg_color="#e9f7ef", title="Ativos", title_color="#28a745", value=dados['ativos'], value_color="#28a745"), unsafe_allow_html=True)
        with col2:
            st.markdown(card_css.format(bg_color="#e9f7ef", title="Admissões", title_color="#17a2b8", value=dados['admissoes'], value_color="#17a2b8"), unsafe_allow_html=True)
        with col3:
            st.markdown(card_css.format(bg_color="#e9f7ef", title="Demissões", title_color="#ffc107", value=dados['demissoes'], value_color="#ffc107"), unsafe_allow_html=True)
        with col4:
            st.markdown(card_css.format(bg_color="#f8d7da", title="Turnover", title_color="#dc3545", value=f"{dados['turnover']:.2f}%", value_color="#dc3545"), unsafe_allow_html=True)

    else:
        sns.set(style="darkgrid", palette="deep")
        data = []
        for m in meses_selecionados:
            dados = turnover_dict.get(m, {'ativos': 0, 'turnover': 0})
            mes_nome = datetime(ano_selecionado, m, 1).strftime('%b %Y')
            data.append([mes_nome, dados['ativos'], dados['turnover']])

        df_mes = pd.DataFrame(data, columns=["Mês", "Ativos", "Turnover"])

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x="Mês", y="Turnover", data=df_mes, ax=ax, palette="coolwarm_r")

        ax.grid(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.set_ylabel('')
        ax.set_title(f"Turnover (%) por Mês", fontsize=16, color="white")
        ax.tick_params(axis='x', rotation=45, labelcolor="white")
        ax.set_facecolor("#2d2d2d")
        fig.patch.set_facecolor("#2d2d2d")

        for p in ax.patches:
            ax.annotate(f'{p.get_height():.2f}%', (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', fontsize=10, color='white', xytext=(0, 7),
                        textcoords='offset points')

        st.pyplot(fig)

if __name__ == "__main__":
    main()





























