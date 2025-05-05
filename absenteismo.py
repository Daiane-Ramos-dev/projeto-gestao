import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import seaborn as sns
from data_loader import absent_dados

if "page" not in st.session_state:
    st.session_state.page = "homepage"  # ou qualquer nome padrão

if "username" not in st.session_state or st.session_state.username is None:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.session_state.page = "login"
    st.rerun()

# Função para carregar dados do arquivo Excel
def load_data():
    try:
        base = absent_dados()

        base['DATA'] = pd.to_datetime(base['DATA'], errors='coerce')
        base['HAUSENTES'] = pd.to_numeric(base['HAUSENTES'], errors='coerce')
        base['HBASE'] = pd.to_numeric(base['HBASE'], errors='coerce')

        base['DATA'] = base['DATA'].dt.strftime('%Y-%m-%d')
        base['ANO_MES'] = pd.to_datetime(base['DATA']).dt.to_period('M').astype(str)

        required_columns = ['DATA', 'CHAPA', 'NOME', 'CODIGO', 'SECAO', 'EVENTO', 'HAUSENTES', 'HBASE']
        missing_columns = [col for col in required_columns if col not in base.columns]
        if missing_columns:
            st.error(f"Colunas ausentes: {missing_columns}")
            return pd.DataFrame(), pd.DataFrame()

        df_grouped = base.groupby(['CHAPA', 'NOME', 'SECAO', 'DATA']).agg({
            'HAUSENTES': 'sum',
            'HBASE': 'sum'
        }).reset_index()

        df_grouped['Absenteísmo (%)'] = np.where(
            df_grouped['HBASE'] != 0,
            (df_grouped['HAUSENTES'] / df_grouped['HBASE']) * 100,
            0
        )
        df_grouped['ANO_MES'] = pd.to_datetime(df_grouped['DATA']).dt.to_period('M').astype(str)

        return df_grouped, base

    except FileNotFoundError:
        st.error("Arquivo ABSENT.xlsx não encontrado.")
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")

    return pd.DataFrame(), pd.DataFrame()

def main():
    st.title("📊 Dashboard de Absenteísmo")
    st.markdown("<hr><br>", unsafe_allow_html=True)

    df_grouped, df_original = load_data()
    if df_grouped.empty:
        st.error("Erro ao carregar os dados.")
        return

    # Filtro único: por Ano-Mês
    month_filter = st.multiselect(
        "📅 Selecione o Ano-Mês:",
        options=sorted(df_grouped['ANO_MES'].unique()),
        default=sorted(df_grouped['ANO_MES'].unique())
    )

    # Aplicar filtro
    filtered_data = df_grouped[df_grouped['ANO_MES'].isin(month_filter)]

    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.subheader("📌 Estatísticas Gerais")

    # Cálculos
    total_hausentes = filtered_data['HAUSENTES'].sum()
    total_hbase = filtered_data['HBASE'].sum()
    total_absenteismo = (total_hausentes / total_hbase) * 100 if total_hbase != 0 else 0

    def formatar_horas(horas_decimais):
        horas = int(horas_decimais)
        minutos = int(round((horas_decimais - horas) * 60))
        return f"{horas:02d}:{minutos:02d}"

    total_hausentes_formatado = formatar_horas(total_hausentes)

    # Layout dos cards
    _, col1, col2, _ = st.columns([1, 2, 2, 1])
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
            title="Horas Ausentes",
            title_color="#28a745",
            value=f"{total_hausentes_formatado} h",
            value_color="#28a745"
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(card_css.format(
            bg_color="#f8d7da",
            title="Absenteísmo",
            title_color="#dc3545",
            value=f"{total_absenteismo:.2f}%",
            value_color="#dc3545"
        ), unsafe_allow_html=True)

    st.markdown("<br><hr>", unsafe_allow_html=True)

    # Gráfico: Evolução Mensal do Absenteísmo
    st.subheader("📊 Evolução Mensal: Horas Ausentes x Absenteísmo")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Agrupamento por mês
    mensal = filtered_data.groupby('ANO_MES').agg({
        'HAUSENTES': 'sum',
        'HBASE': 'sum'
    }).reset_index()

    mensal['Absenteísmo (%)'] = np.where(
        mensal['HBASE'] != 0,
        (mensal['HAUSENTES'] / mensal['HBASE']) * 100,
        0
    )

    # Converter ANO_MES para datetime (ordenar corretamente)
    mensal['ANO_MES'] = pd.to_datetime(mensal['ANO_MES'])
    mensal = mensal.sort_values('ANO_MES')
    mensal['ANO_MES_STR'] = mensal['ANO_MES'].dt.strftime('%Y-%m')

    # Gráfico de barras: HAUSENTES
    barras = alt.Chart(mensal).mark_bar(color="#6c757d").encode(
        x=alt.X('ANO_MES_STR:N', title='Ano-Mês'),
        y=alt.Y('HAUSENTES:Q', title='Horas Ausentes'),
        tooltip=['ANO_MES_STR', 'HAUSENTES']
    )

    # Gráfico de linha: Absenteísmo (%)
    linha = alt.Chart(mensal).mark_line(color='#007bff', strokeWidth=3).encode(
        x='ANO_MES_STR:N',
        y=alt.Y('Absenteísmo (%):Q', title='% de Absenteísmo'),
        tooltip=['ANO_MES_STR', 'Absenteísmo (%)']
    )

    # Eixos combinados
    eixo_y_esquerdo = alt.Axis(title='Horas Ausentes')
    eixo_y_direito = alt.Axis(title='% Absenteísmo', orient='right')

    # Combinar os dois gráficos
    combinado = alt.layer(barras, linha).resolve_scale(
        y='independent'
    ).properties(
        width=700,
        height=400
    )

    st.altair_chart(combinado, use_container_width=True)

    st.markdown("<br><hr>", unsafe_allow_html=True)

    st.subheader("👤 Evolução do Absenteísmo por Funcionário")

    # Criar nomes completos com NOME primeiro para ordenar alfabeticamente
    df_grouped['FUNCIONARIO'] = df_grouped['NOME'] + " - " + df_grouped['CHAPA'].astype(str)

    # Filtro de funcionário (ordenado por nome)
    sorted_funcionarios = sorted(df_grouped['FUNCIONARIO'].unique(), key=lambda x: x.lower())

    selected_funcionarios = st.multiselect(
        "Selecione Funcionários:",
        options=sorted_funcionarios,
        default=sorted_funcionarios
)

    # Filtrar dados de acordo com a seleção de funcionários e meses
    dados_filtrados_func = df_grouped[
        (df_grouped['FUNCIONARIO'].isin(selected_funcionarios)) &
        (df_grouped['ANO_MES'].isin(month_filter))
    ]

    # Agrupar por ANO_MES e FUNCIONARIO
    absenteismo_funcionario = dados_filtrados_func.groupby(['ANO_MES', 'FUNCIONARIO']).agg({
        'HAUSENTES': 'sum',
        'HBASE': 'sum'
    }).reset_index()

    # Calcular Absenteísmo (%)
    absenteismo_funcionario['Absenteísmo (%)'] = np.where(
        absenteismo_funcionario['HBASE'] != 0,
        (absenteismo_funcionario['HAUSENTES'] / absenteismo_funcionario['HBASE']) * 100,
        0
    )

    # Gráfico: Barras para HAUSENTES e Linha para Absenteísmo (%)
    base = alt.Chart(absenteismo_funcionario).encode(
        x=alt.X('ANO_MES:N', title='Mês', sort=month_filter),
        y=alt.Y('HAUSENTES:Q', title='Horas Ausentes'),
        tooltip=['ANO_MES', 'FUNCIONARIO', 'HAUSENTES', 'Absenteísmo (%)']
    )

    # Barras com uma cor fixa
    barras = base.mark_bar(color="#6c757d").encode(  # cor fixa (cinza, por exemplo)
        tooltip=['ANO_MES', 'FUNCIONARIO', 'HAUSENTES', 'Absenteísmo (%)']
    )

    # Linha para Absenteísmo com cor fixa
    linha = base.mark_line(color='#007bff', strokeWidth=3).encode(
        y=alt.Y('Absenteísmo (%):Q', title='% Absenteísmo', axis=alt.Axis(grid=False))
    )

    # Combinar barras e linha no gráfico
    grafico = alt.layer(barras, linha).resolve_scale(
        y='independent'  # Eixos independentes para a barra e linha
    ).properties(
        width=700,
        height=400
    )

    st.altair_chart(grafico, use_container_width=True)


if __name__ == "__main__":
   main()







