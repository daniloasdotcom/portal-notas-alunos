import streamlit as st
import pandas as pd

# 1. Configuração da página e identidade visual
st.set_page_config(page_title="Portal de Notas", page_icon="🎓", layout="centered")
st.title("📊 Consulta de Desempenho")


# 2. Carregamento e preparação dos dados (com cache para performance)
@st.cache_data
def carregar_dados():
    # Carrega a planilha Excel
    df = pd.read_excel("notas.xlsx")

    # Remove espaços em branco invisíveis do início e fim dos nomes das colunas
    df.columns = df.columns.str.strip()

    # Garante que a coluna Matrícula seja tratada como texto puro (evita o .0 no final)
    if 'Matrícula' in df.columns:
        df['Matrícula'] = df['Matrícula'].astype(str).str.strip()

    return df


# Tenta carregar o banco de dados
try:
    df = carregar_dados()
except FileNotFoundError:
    st.error("Arquivo 'notas.xlsx' não encontrado. Verifique se ele está na mesma pasta do seu script 'app.py'.")
    st.stop()

# 3. Interface do usuário - Entrada de dados
st.markdown("Digite o seu número de matrícula abaixo para consultar suas notas individuais.")

matricula_input = st.text_input("Número de Matrícula:", placeholder="Ex: 2023200939")

if st.button("Buscar Notas"):
    if matricula_input:
        # Filtra o banco de dados pela matrícula digitada
        aluno_df = df[df['Matrícula'] == matricula_input]

        if not aluno_df.empty:
            st.success("Aluno encontrado com sucesso!")

            # 4. Exibição dos resultados principais (Resumo Geral)
            st.subheader("Resumo Geral")
            col1, col2, col3 = st.columns(3)

            # Conversão segura para float para evitar erros de dízima na tela
            nota_prova = float(aluno_df.iloc[0]['Prontuação na Prova'])
            nota_extra = float(aluno_df.iloc[0]['Pontuação dos exercícios extras'])
            nota_total = float(aluno_df.iloc[0]['Pontuação total (Prova + Extra)'])

            # O formato :.2f força a exibição de exatamente duas casas decimais
            col1.metric("Nota da Prova", f"{nota_prova:.2f}")
            col2.metric("Exercícios Extras", f"{nota_extra:.2f}")
            col3.metric("Pontuação Total", f"{nota_total:.2f}")

            st.divider()

            # 5. Exibição do detalhamento estruturado por Questões utilizando Abas
            st.subheader("Detalhamento por Questão")

            tab1, tab2, tab3 = st.tabs(["Questão 01", "Questão 02", "Questão 03"])

            # --- Painel da Questão 01 (Itens a até e + Pontuações) ---
            with tab1:
                df_q1 = pd.DataFrame({
                    "Item": ["a", "b", "c", "d", "e"],
                    "Respostas / Fração": [
                        aluno_df.iloc[0]['Item a'], aluno_df.iloc[0]['Item b'],
                        aluno_df.iloc[0]['Item c'], aluno_df.iloc[0]['Item d'],
                        aluno_df.iloc[0]['Item e']
                    ],
                    "Pontuação Obtida": [
                        aluno_df.iloc[0]['Pontuação'], aluno_df.iloc[0]['Pontuação.1'],
                        aluno_df.iloc[0]['Pontuação.2'], aluno_df.iloc[0]['Pontuação.3'],
                        aluno_df.iloc[0]['Pontuação.4']
                    ]
                })
                st.dataframe(df_q1, use_container_width=True, hide_index=True)

            # --- Painel da Questão 02 (Itens a até g) ---
            with tab2:
                df_q2 = pd.DataFrame({
                    "Item": ["a", "b", "c", "d", "e", "f", "g"],
                    "Pontuação Obtida": [
                        aluno_df.iloc[0]['Item a.1'], aluno_df.iloc[0]['Item b.1'],
                        aluno_df.iloc[0]['Item c.1'], aluno_df.iloc[0]['Item d.1'],
                        aluno_df.iloc[0]['Item e.1'], aluno_df.iloc[0]['Item f'],
                        aluno_df.iloc[0]['Item g']
                    ]
                })
                st.dataframe(df_q2, use_container_width=True, hide_index=True)

            # --- Painel da Questão 03 (Itens a até c) ---
            with tab3:
                df_q3 = pd.DataFrame({
                    "Item": ["a", "b", "c"],
                    "Pontuação Obtida": [
                        aluno_df.iloc[0]['Item a.2'], aluno_df.iloc[0]['Item b.2'],
                        aluno_df.iloc[0]['Item c.2']
                    ]
                })
                st.dataframe(df_q3, use_container_width=True, hide_index=True)

        else:
            st.warning("Matrícula não encontrada. Verifique se você digitou corretamente.")
    else:
        st.info("Por favor, insira uma matrícula antes de buscar.")