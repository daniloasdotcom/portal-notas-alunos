import streamlit as st
import pandas as pd

# 1. Configuração da página e identidade visual
st.set_page_config(page_title="Portal de Notas", page_icon="🎓", layout="centered")
st.title("📊 Consulta - Notas de Fertilidade do Solo")


# 2. Carregamento e preparação dos dados (com cache para performance)
@st.cache_data
def carregar_dados():
    # Carrega a planilha Excel
    df = pd.read_excel("notas.xlsx")

    # Remove espaços em branco invisíveis do início e fim dos nomes das colunas
    df.columns = df.columns.str.strip()

    # Garante que a coluna Matrícula seja treated como texto puro (evita o .0 no final)
    if 'Matrícula' in df.columns:
        df['Matrícula'] = df['Matrícula'].astype(str).str.strip()

    return df


# Função auxiliar para formatar as notas nas tabelas (previne decimais gigantes e trata vazios)
def formatar_nota(valor):
    if pd.isna(valor) or str(valor).strip() == "":
        return "-"
    return f"{float(valor):.2f}"


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
        prova_corrigida = not pd.isna(row['Prontuação na Prova'])

        # 4. Exibição dos resultados principais (Resumo Geral)
        st.subheader("Resumo Geral")

        # --- SEÇÃO DA PROVA 01 ---
        st.markdown("### 📝 Avaliação 01")
        nota_p1 = row['Prova 01']
        nota_p1_str = f"{float(nota_p1):.2f}" if not pd.isna(nota_p1) else "-"

        col_p1 = st.columns(1)[0]
        col_p1.metric("Nota Final - Prova 01", nota_p1_str)

        st.write("")  # Espaçamento visual

        # --- SEÇÃO DA PROVA 02 ---
        st.markdown("### 📝 Avaliação 02")

        # Armazena a nota de exercícios extras com segurança
        nota_extra = row['Pontuação dos exercícios extras']
        nota_extra_str = f"{float(nota_extra):.2f}" if not pd.isna(nota_extra) else "0.00"

        # Define dinamicamente o que exibir com base no status da correção
        if prova_corrigida:
            st.success("Notas da Prova 02 carregadas com sucesso!")
            nota_prova_str = f"{float(row['Prontuação na Prova']):.2f}"
            nota_total_str = f"{float(row['Pontuação total (Prova + Extra)']):.2f}"

            # Cálculos dinâmicos da soma de pontos por questão (Prova 02)
            total_q1 = pd.to_numeric(row[['Pontuação', 'Pontuação.1', 'Pontuação.2', 'Pontuação.3', 'Pontuação.4']],
                                     errors='coerce').sum()
            total_q2 = pd.to_numeric(
                row[['Item a.1', 'Item b.1', 'Item c.1', 'Item d.1', 'Item e.1', 'Item f', 'Item g']],
                errors='coerce').sum()
            total_q3 = pd.to_numeric(row[['Item a.2', 'Item b.2', 'Item c.2']], errors='coerce').sum()

            nota_q1_str = f"**{total_q1:.2f}** pontos"
            nota_q2_str = f"**{total_q2:.2f}** pontos"
            nota_q3_str = f"**{total_q3:.2f}** pontos"
        else:
            st.warning("⚠️ Sua Prova 02 está em fase de correção. Os dados detalhados serão atualizados em breve.")
            nota_prova_str = "Em correção"
            nota_total_str = "Aguardando"
            nota_q1_str = "*Em correção*"
            nota_q2_str = "*Em correção*"
            nota_q3_str = "*Em correção*"

        col1, col2, col3 = st.columns(3)
        col1.metric("Nota da Prova 02", nota_prova_str)
        col2.metric("Exercícios Extras", nota_extra_str)
        col3.metric("Pontuação Total (Prova + Extra)", nota_total_str)

        st.divider()

        # 5. Exibição do detalhamento estruturado por Questões utilizando Abas
        st.subheader("Detalhamento por Questão (Prova 02)")

        tab1, tab2, tab3 = st.tabs(["Questão 01", "Questão 02", "Questão 03"])

        # --- Painel da Questão 01 ---
        with tab1:
            st.markdown(f"🏅 **Nota total da Questão 01:** {nota_q1_str}")

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

            df_q1["Pontuação Obtida"] = df_q1["Pontuação Obtida"].apply(formatar_nota)
            df_q1["Respostas / Fração"] = df_q1["Respostas / Fração"].fillna("-")

            st.dataframe(
                df_q1,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Item": st.column_config.TextColumn("Item", alignment="center"),
                    "Respostas / Fração": st.column_config.TextColumn("Acertos / Itens", alignment="center"),
                    "Pontuação Obtida": st.column_config.TextColumn("Nota Obtida", alignment="center"),
                }
            )

        # --- Painel da Questão 02 ---
        with tab2:
            st.markdown(f"🏅 **Nota total da Questão 02:** {nota_q2_str}")

            df_q2 = pd.DataFrame({
                "Item": ["a", "b", "c", "d", "e", "f", "g"],
                "Pontuação Obtida": [
                    row['Item a.1'], row['Item b.1'],
                    row['Item c.1'], row['Item d.1'],
                    row['Item e.1'], row['Item f'],
                    row['Item g']
                ]
            })

            df_q2["Pontuação Obtida"] = df_q2["Pontuação Obtida"].apply(formatar_nota)

            st.dataframe(
                df_q2,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Item": st.column_config.TextColumn("Item", alignment="center"),
                    "Pontuação Obtida": st.column_config.TextColumn("Nota Obtida", alignment="center"),
                }
            )

        # --- Painel da Questão 03 ---
        with tab3:
            st.markdown(f"🏅 **Nota total da Questão 03:** {nota_q3_str}")

            df_q3 = pd.DataFrame({
                "Item": ["a", "b", "c"],
                "Pontuação Obtida": [
                    row['Item a.2'], row['Item b.2'],
                    row['Item c.2']
                ]
            })

            df_q3["Pontuação Obtida"] = df_q3["Pontuação Obtida"].apply(formatar_nota)

            st.dataframe(
                df_q3,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Item": st.column_config.TextColumn("Item", alignment="center"),
                    "Pontuação Obtida": st.column_config.TextColumn("Nota Obtida", alignment="center"),
                }
            )
else:
    st.info("Aguardando a seleção de uma matrícula para exibir as notas.")