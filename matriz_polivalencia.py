import streamlit as st
import pandas as pd
import altair as alt
from data_loader import (
    adicionar_funcao_db,
    adicionar_colaborador_db,
    get_funcoes,
    get_colaboradores,
    criar_tabelas,
    atualizar_colaborador_db,
    excluir_colaborador_db,
    get_historico_habilidades
)

# Estilo CSS para melhor legibilidade em dispositivos móveis
st.markdown("""
    <style>
        input, select, button {
            font-size: 16px !important;
        }
        .stSelectbox > div > div {
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "homepage"

if "username" not in st.session_state or st.session_state.username is None:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.session_state.page = "login"
    st.rerun()

def adicionar_funcao():
    with st.expander("➕ Adicionar Funções"):
        funcao = st.text_input("Nome da Função")
        if st.button("Adicionar Função"):
            if funcao:
                adicionar_funcao_db(funcao)
                st.success(f"Função '{funcao}' adicionada com sucesso!")
            else:
                st.warning("Digite o nome da função.")

def adicionar_colaborador():
    with st.expander("👥 Adicionar/Atualizar Colaboradores"):
        funcoes = get_funcoes()
        if not funcoes:
            st.warning("Adicione pelo menos uma função antes.")
            return

        colaboradores_unicos = {
            colaborador[0]: colaborador[1]
            for colaborador in get_colaboradores()
        }

        opcoes_colaboradores = ["Adicionar Novo Colaborador"] + [
            f"{id} - {nome}" for id, nome in sorted(colaboradores_unicos.items(), key=lambda item: item[1].lower())
        ]

        colaborador_selecionado = st.selectbox("Selecione um colaborador", opcoes_colaboradores)
        habilidades = {}

        if colaborador_selecionado != "Adicionar Novo Colaborador":
            colaborador_id = int(colaborador_selecionado.split(" - ")[0])
            colaborador_nome = colaboradores_unicos[colaborador_id]

            for f in funcoes:
                nivel = next((n for id, _, funcao, n in get_colaboradores()
                              if id == colaborador_id and funcao == f), 0)
                habilidades[f] = st.selectbox(f"{f} (0-5)", [0,1,2,3,4, 5], index=nivel, key=f"{colaborador_id}_{f}")

            if st.button(f"Atualizar {colaborador_nome}"):
                atualizar_colaborador_db(colaborador_id, habilidades)
                st.success("Atualizado com sucesso!")

            if st.button(f"Excluir {colaborador_nome}"):
                excluir_colaborador_db(colaborador_id)
                st.success("Excluído com sucesso!")
        else:
            nome_colaborador = st.text_input("Nome do Novo Colaborador")
            if nome_colaborador:
                for f in funcoes:
                    habilidades[f] = st.selectbox(f"{f} (0-5)", [0,1,2,3,4,5], key=f"{nome_colaborador}_{f}")
                if st.button("Adicionar Colaborador"):
                    adicionar_colaborador_db(nome_colaborador, habilidades)
                    st.success("Colaborador adicionado com sucesso!")

def exibir_matriz():
    colaboradores = get_colaboradores()

    if colaboradores:
        #st.header("Matriz de Polivalência") #Ocultar o Titulo da Matriz
        
        data = {"ID": [], "nome": []}
        funcoes = get_funcoes()
        
        for f in funcoes:
            data[f] = []

        for colaborador_id, colaborador_nome, funcao_nome, nivel in colaboradores:
            if colaborador_id not in data["ID"]:
                data["ID"].append(colaborador_id)
                data["nome"].append(colaborador_nome)
                for f in funcoes:
                    data[f].append(0)

            idx = data["ID"].index(colaborador_id)
            data[funcao_nome][idx] = nivel

        df = pd.DataFrame(data)

        # Melhorias no estilo da tabela
        st.markdown("""
        <style>
            table {
                width: 100%; 
                table-layout: fixed; 
                border-collapse: collapse;
            }
            table th {
                transform: rotate(270deg); 
                white-space: nowrap; 
                text-align: center; 
                padding: 10px 5px; 
                height: 200px; 
                width: 80px; 
                justify-content: center; 
                align-items: flex-end; 
                line-height: 1.2; 
                background-color: #f4f4f4;
                border: 1px solid #ddd;
            }
            table td {
                padding: 8px; 
                text-align: center;
                border: 1px solid #ddd;
            }
            table tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            table tr:hover {
                background-color: #f1f1f1;
            }
        </style>
        """, unsafe_allow_html=True)

        #st.dataframe(df, use_container_width=True, hide_index=True) #Ocultar minha Tabela Matriz Polivalência da exibição

        df_melted = df.melt(id_vars=["ID", "nome"], var_name="Função", value_name="Nível")

        st.markdown("<hr><br>", unsafe_allow_html=True)

        # Gráfico por Função
        df_melted = df.melt(id_vars=["ID", "nome"], var_name="Função", value_name="Nível")  # Incluindo ID no gráfico

        st.header("Gráfico por Função")

        # Filtro de função
        funcoes_unicas = df_melted["Função"].unique().tolist()
        funcoes_selecionadas = st.multiselect(
            "Filtrar Funções",
            options=funcoes_unicas,
            default=funcoes_unicas
        )

        # Aplica o filtro
        df_filtrado = df_melted[df_melted["Função"].isin(funcoes_selecionadas)].copy()
        df_filtrado["Nível_Base"] = 0  # Início das barras

        # Gráficos individuais por função
        for funcao in funcoes_selecionadas:
            df_funcao = df_filtrado[df_filtrado["Função"] == funcao].copy()
            df_funcao["Nível_Base"] = 0

            chart = alt.Chart(df_funcao).mark_bar().encode(
                y=alt.Y(
                    "nome:N",
                    title=None,
                    sort=alt.EncodingSortField(field="nome", order="ascending"),
                    axis=alt.Axis(labelAngle=0, labelLimit=350, labelPadding=12)
                    
                ),
                x=alt.X(
                    "Nível:Q",
                    title="Nível de Habilidade",
                    scale=alt.Scale(domain=[0, 4.5]),
                    axis=alt.Axis(values=[0, 1, 2, 3, 4])
                ),
                x2="Nível_Base:Q",
                color=alt.Color("Função:N", legend=None),
                tooltip=["ID:N", "nome:N", "Função:N", "Nível:Q"]
            ).properties(
                width=500,
                height=450,
                title=funcao  # Título centralizado acima do gráfico
            )

            st.altair_chart(chart, use_container_width=True)

        st.markdown("<br><hr>", unsafe_allow_html=True)

        # Gráfico por Colaborador
        st.header("Gráfico por Colaborador")

        # Filtro para selecionar um colaborador
        colaboradores_unicos = sorted(df["nome"].unique())
        colaborador_selecionado = st.selectbox("Selecione um colaborador", colaboradores_unicos)
        # Espaçamento visual extra (2 quebras de linha)
        st.markdown("###  ")

        # Filtrar os dados para o colaborador selecionado
        df_colaborador = df[df["nome"] == colaborador_selecionado]
        df_colaborador_melted = df_colaborador.melt(id_vars=["ID", "nome"], var_name="Função", value_name="Nível")

        # Ordenar funções pelas mais fortes (nível decrescente)
        df_colaborador_melted = df_colaborador_melted.sort_values("Nível", ascending=False)

        # Nível base flexível (começando em 0 para garantir início da barra)
        df_colaborador_melted["Nível_Base"] = 0

        # Gráfico do colaborador específico com barras horizontais
        chart_colaborador = alt.Chart(df_colaborador_melted).mark_bar().encode(
            y=alt.Y(
                "Função:N",
                title="Função",
                sort="ascending",
                axis=alt.Axis(labelAngle=0, labelLimit=230, labelPadding=12)
            ),
            x=alt.X(
                "Nível:Q",
                title="Nível de Habilidade",
                scale=alt.Scale(domain=[0, 4.5]),  # Agora começa em 0 de verdade
                axis=alt.Axis(values=[0, 1, 2, 3, 4])
            ),
            x2="Nível_Base:Q",
            color=alt.Color("Função:N", legend=None),
            tooltip=["nome:N", "Função:N", "Nível:Q"]
        ).properties(
            width=500,
            height=400,
            title=f'Habilidades de {colaborador_selecionado}'
        )

        st.altair_chart(chart_colaborador, use_container_width=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        
        # Gráfico de Evolução Temporal
        st.header("Evolução Temporal do Colaborador")
        nomes = sorted(list(set(row[1] for row in colaboradores)))
        nome_selecionado = st.selectbox("Escolha um colaborador para ver evolução", nomes)

        if nome_selecionado:
            colaborador_id = next((id for id, nome, *_ in colaboradores if nome == nome_selecionado), None)
            historico = get_historico_habilidades(colaborador_id)
            
            if historico:
                df_hist = pd.DataFrame(historico, columns=["Função", "Nível", "Data"])
                
                # Converte a coluna "Data" para datetime
                df_hist["Data"] = pd.to_datetime(df_hist["Data"])

                # Remove a parte da hora, deixando apenas a data (sem repetições no eixo X)
                df_hist["Data"] = df_hist["Data"].dt.date  # Extrai apenas a data sem a hora

                # Agrupar por Função e Data, pegando a última alteração do dia
                df_hist = df_hist.groupby(["Função", "Data"]).last().reset_index()  # Pega a última modificação por dia
                
                # Ordena por Data para garantir que a sequência temporal esteja correta
                df_hist = df_hist.sort_values(by="Data")

                # Propaga o nível para o próximo dia se a data de hoje for a próxima
                df_hist["Nível"] = df_hist.groupby("Função")["Nível"].fillna(method='ffill')
                
                # Garantir que a coluna Data seja formatada como string no formato "dd/mm/yyyy"
                df_hist["DataFormatada"] = df_hist["Data"].apply(lambda x: x.strftime("%d/%m/%Y"))
                
                # Ordenação das datas como string para o eixo X
                chart_hist = alt.Chart(df_hist).mark_line(point=True).encode(
                    x=alt.X("DataFormatada:N", title="Data", sort=df_hist["DataFormatada"].unique().tolist(),
                            axis=alt.Axis(labelAngle=0)),  # Definindo a rotação das etiquetas como 0 (horizontal)
                    y=alt.Y("Nível:Q", scale=alt.Scale(domain=[0, 4.5]),
                            axis=alt.Axis(values=[0, 1, 2, 3, 4])),
                    color=alt.Color("Função:N", legend=alt.Legend(labelFontSize=8)),
                    tooltip=["Função:N", "Nível:Q", "DataFormatada:N"]  # Usamos 'DataFormatada:N' para garantir que ele seja tratado como categoria
                ).properties(width=700, height=400, title=f'Evolução Temporal de {nome_selecionado}')
                
                st.altair_chart(chart_hist, use_container_width=True)
            else:
                st.info("Este colaborador ainda não tem histórico registrado.")
        else:
            st.warning("Nenhum colaborador encontrado.")


# Função principal
def main():
    st.title("📈Matriz de Polivalência")
    criar_tabelas()  # Criar as tabelas no banco de dados caso não existam
    adicionar_funcao()
    adicionar_colaborador()
    exibir_matriz()

if __name__ == "__main__":
    main()
