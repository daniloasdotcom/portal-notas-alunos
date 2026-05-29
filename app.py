import streamlit as st
import pandas as pd

# 1. Configuração da página e identidade visual
st.set_page_config(page_title="Portal de Notas", page_icon="🎓", layout="centered")
st.title("📊 Consulta - Notas de Fertilidade do Solo")


# 2. Carregamento e preparação dos dados (com cache para performance)
@st.cache_data
def carregar_dados():
    # Carrega a planilha
    df = pd.read_excel("notas.xlsx")

    # Remove espaços em branco invisíveis do início e fim dos nomes das colunas
    df.columns = df.columns.str.strip()

    # Garante que a coluna Matrícula seja tratada como texto puro
    if 'Matrícula' in df.columns:
        df['Matrícula'] = df['Matrícula'].astype(str).str.strip()

    return df


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

# 3. Interface do usuário
st.markdown("Clique no campo abaixo e digite o seu número de matrícula para consultar suas notas.")

lista_matriculas = sorted(df['Matrícula'].dropna().unique())
opcoes_selectbox = ["Selecione uma matrícula..."] + lista_matriculas

matricula_selecionada = st.selectbox(
    "Número de Matrícula:",
    options=opcoes_selectbox,
    index=0
)

if matricula_selecionada != "Selecione uma matrícula...":
    aluno_df = df[df['Matrícula'] == matricula_selecionada]

    if not aluno_df.empty:
        row = aluno_df.iloc[0]
        prova_corrigida = not pd.isna(row['Prontuação na Prova'])

        st.subheader("Resumo Geral")

        # --- SEÇÃO DA PROVA 01 ---
        st.markdown("### 📝 Avaliação 01")
        nota_p1 = row['Prova 01']

        # Variáveis numéricas para o gráfico posterior
        nota_p1_num = float(nota_p1) if not pd.isna(nota_p1) else 0.0
        nota_p1_str = f"{nota_p1_num:.2f}" if not pd.isna(nota_p1) else "-"

        col_p1 = st.columns(1)[0]
        col_p1.metric("Nota Final - Prova 01", nota_p1_str)

        st.write("")

        # --- SEÇÃO DA PROVA 02 ---
        st.markdown("### 📝 Avaliação 02")

        nota_extra = row['Pontuação dos exercícios extras']
        nota_extra_str = f"{float(nota_extra):.2f}" if not pd.isna(nota_extra) else "0.00"

        nota_p2_num = 0.0  # Inicializa como 0 para caso não tenha sido corrigida

        if prova_corrigida:
            st.success("Notas da Prova 02 carregadas com sucesso!")
            nota_p2_num = float(row['Prontuação na Prova'])
            nota_prova_str = f"{nota_p2_num:.2f}"
            nota_total_str = f"{float(row['Pontuação total (Prova + Extra)']):.2f}"

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
        col1.metric("Nota da Prova 02", nota_prova_str,
                    delta=f"{nota_p2_num - nota_p1_num:.2f}" if prova_corrigida and not pd.isna(nota_p1) else None)
        col2.metric("Exercícios Extras", nota_extra_str)
        col3.metric("Pontuação Total (Prova + Extra)", nota_total_str)

        st.divider()

        # --- NOVO: GRÁFICO DE EVOLUÇÃO ---
        st.subheader("📈 Evolução de Desempenho")

        # Cria um mini DataFrame apenas com as notas para o gráfico
        df_grafico = pd.DataFrame({
            "Avaliação": ["Prova 01", "Prova 02"],
            "Nota": [nota_p1_num, nota_p2_num]
        })
        # Configura a coluna Avaliação como índice para o Streamlit entender o Eixo X
        df_grafico.set_index("Avaliação", inplace=True)

        # Exibe o gráfico de barras
        st.bar_chart(df_grafico, color="#1f77b4")

        st.divider()

        # 5. Exibição do detalhamento estruturado por Questões utilizando Abas
        st.subheader("Detalhamento por Questão (Prova 02)")

        tab1, tab2, tab3 = st.tabs(["Questão 01", "Questão 02", "Questão 03"])

        with tab1:
            st.markdown(f"🏅 **Nota total da Questão 01:** {nota_q1_str}")
            df_q1 = pd.DataFrame({
                "Item": ["a", "b", "c", "d", "e"],
                "Respostas / Fração": [row['Item a'], row['Item b'], row['Item c'], row['Item d'], row['Item e']],
                "Pontuação Obtida": [row['Pontuação'], row['Pontuação.1'], row['Pontuação.2'], row['Pontuação.3'],
                                     row['Pontuação.4']]
            })
            df_q1["Pontuação Obtida"] = df_q1["Pontuação Obtida"].apply(formatar_nota)
            df_q1["Respostas / Fração"] = df_q1["Respostas / Fração"].fillna("-")
            st.dataframe(df_q1, use_container_width=True, hide_index=True,
                         column_config={"Item": st.column_config.TextColumn("Item", alignment="center"),
                                        "Respostas / Fração": st.column_config.TextColumn("Acertos / Itens",
                                                                                          alignment="center"),
                                        "Pontuação Obtida": st.column_config.TextColumn("Nota Obtida",
                                                                                        alignment="center")})

        with tab2:
            st.markdown(f"🏅 **Nota total da Questão 02:** {nota_q2_str}")
            df_q2 = pd.DataFrame({
                "Item": ["a", "b", "c", "d", "e", "f", "g"],
                "Pontuação Obtida": [row['Item a.1'], row['Item b.1'], row['Item c.1'], row['Item d.1'],
                                     row['Item e.1'], row['Item f'], row['Item g']]
            })
            df_q2["Pontuação Obtida"] = df_q2["Pontuação Obtida"].apply(formatar_nota)
            st.dataframe(df_q2, use_container_width=True, hide_index=True,
                         column_config={"Item": st.column_config.TextColumn("Item", alignment="center"),
                                        "Pontuação Obtida": st.column_config.TextColumn("Nota Obtida",
                                                                                        alignment="center")})

        with tab3:
            st.markdown(f"🏅 **Nota total da Questão 03:** {nota_q3_str}")
            df_q3 = pd.DataFrame({
                "Item": ["a", "b", "c"],
                "Pontuação Obtida": [row['Item a.2'], row['Item b.2'], row['Item c.2']]
            })
            df_q3["Pontuação Obtida"] = df_q3["Pontuação Obtida"].apply(formatar_nota)
            st.dataframe(df_q3, use_container_width=True, hide_index=True,
                         column_config={"Item": st.column_config.TextColumn("Item", alignment="center"),
                                        "Pontuação Obtida": st.column_config.TextColumn("Nota Obtida",
                                                                                        alignment="center")})

else:
    st.info("Aguardando a seleção de uma matrícula para exibir as notas.")