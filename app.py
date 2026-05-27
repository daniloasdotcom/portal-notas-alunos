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

# 3. Interface do usuário - Campo de Autocomplete (Selectbox com busca)
st.markdown("Clique no campo abaixo e digite o seu número de matrícula para consultar suas notas.")

# Criamos uma lista ordenada com todas as matrículas únicas do banco de dados
lista_matriculas = sorted(df['Matrícula'].dropna().unique())

# Adicionamos uma opção neutra no início para o app abrir "vazio"
opcoes_selectbox = ["Selecione uma matrícula..."] + lista_matriculas

matricula_selecionada = st.selectbox(
    "Número de Matrícula:",
    options=opcoes_selectbox,
    index=0  # Começa apontando para "Selecione uma matrícula..."
)

# O código agora executa automaticamente assim que uma matrícula válida é escolhida
if matricula_selecionada != "Selecione uma matrícula...":
    # Filtra o banco de dados pela matrícula selecionada
    aluno_df = df[df['Matrícula'] == matricula_selecionada]

    if not aluno_df.empty:
        row = aluno_df.iloc[0]

        # Verifica se a prova já foi corrigida (se o campo não está vazio)
        # Nota: Mantido o nome original da coluna 'Prontuação na Prova' conforme a planilha
        prova_corrigida = not pd.isna(row['Prontuação na Prova'])

        # 4. Exibição dos resultados principais (Resumo Geral)
        st.subheader("Resumo Geral")

        # Armazena a nota de exercícios extras com segurança
        nota_extra = row['Pontuação dos exercícios extras']
        nota_extra_str = f"{float(nota_extra):.2f}" if not pd.isna(nota_extra) else "0.00"

        # Define dinamicamente o que exibir com base no status da correção
        if prova_corrigida:
            st.success("Notas encontradas com sucesso!")
            nota_prova_str = f"{float(row['Prontuação na Prova']):.2f}"
            nota_total_str = f"{float(row['Pontuação total (Prova + Extra)']):.2f}"
        else:
            st.warning("⚠️ Sua prova está em fase de correção. Os dados detalhados serão atualizados em breve.")
            nota_prova_str = "Em correção"
            nota_total_str = "Aguardando"

        col1, col2, col3 = st.columns(3)
        col1.metric("Nota da Prova", nota_prova_str)
        col2.metric("Exercícios Extras", nota_extra_str)
        col3.metric("Pontuação Total", nota_total_str)

        st.divider()

        # 5. Exibição do detalhamento estruturado por Questões utilizando Abas
        st.subheader("Detalhamento por Questão")

        tab1, tab2, tab3 = st.tabs(["Questão 01", "Questão 02", "Questão 03"])

        # --- Painel da Questão 01 (Itens a até e + Pontuações) ---
        with tab1:
            df_q1 = pd.DataFrame({
                "Item": ["a", "b", "c", "d", "e"],
                "Respostas / Fração": [
                    row['Item a'], row['Item b'],
                    row['Item c'], row['Item d'],
                    row['Item e']
                ],
                "Pontuação Obtida": [
                    row['Pontuação'], row['Pontuação.1'],
                    row['Pontuação.2'], row['Pontuação.3'],
                    row['Pontuação.4']
                ]
            })

            # Exibição com tratamento de vazios, centralização e novos cabeçalhos
            st.dataframe(
                df_q1.fillna("-"),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Item": st.column_config.TextColumn("Item", alignment="center"),
                    "Respostas / Fração": st.column_config.TextColumn("Acertos / Itens", alignment="center"),
                    "Pontuação Obtida": st.column_config.TextColumn("Nota Obtida", alignment="center"),
                }
            )

        # --- Painel da Questão 02 (Itens a até g) ---
        with tab2:
            df_q2 = pd.DataFrame({
                "Item": ["a", "b", "c", "d", "e", "f", "g"],
                "Pontuação Obtida": [
                    row['Item a.1'], row['Item b.1'],
                    row['Item c.1'], row['Item d.1'],
                    row['Item e.1'], row['Item f'],
                    row['Item g']
                ]
            })

            st.dataframe(
                df_q2.fillna("-"),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Item": st.column_config.TextColumn("Item", alignment="center"),
                    "Pontuação Obtida": st.column_config.TextColumn("Nota Obtida", alignment="center"),
                }
            )

        # --- Painel da Questão 03 (Itens a até c) ---
        with tab3:
            df_q3 = pd.DataFrame({
                "Item": ["a", "b", "c"],
                "Pontuação Obtida": [
                    row['Item a.2'], row['Item b.2'],
                    row['Item c.2']
                ]
            })

            st.dataframe(
                df_q3.fillna("-"),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Item": st.column_config.TextColumn("Item", alignment="center"),
                    "Pontuação Obtida": st.column_config.TextColumn("Nota Obtida", alignment="center"),
                }
            )
else:
    # Mensagem discreta enquanto nenhum aluno foi selecionado
    st.info("Aguardando a seleção de uma matrícula para exibir as notas.")