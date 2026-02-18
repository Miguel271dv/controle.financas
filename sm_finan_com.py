import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Controle Financeiro",
    page_icon="💰",
    layout="wide"
)

# ==============================
# SESSION STATE
# ==============================

if "usuarios" not in st.session_state:
    st.session_state.usuarios = {}

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

# ==============================
# LOGIN / CADASTRO
# ==============================

if st.session_state.usuario_logado is None:

    st.title("💰 Controle Financeiro PRO")
    st.subheader("🔐 Acesse sua conta")

    aba = st.radio("Escolha:", ["Login", "Cadastro"])

    if aba == "Login":

        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if usuario in st.session_state.usuarios:
                if st.session_state.usuarios[usuario]["senha"] == senha:
                    st.session_state.usuario_logado = usuario
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
            else:
                st.error("Usuário não encontrado.")

    else:

        novo_usuario = st.text_input("Novo usuário")
        nova_senha = st.text_input("Nova senha", type="password")

        if st.button("Cadastrar"):

            if novo_usuario in st.session_state.usuarios:
                st.warning("Usuário já existe.")

            elif novo_usuario == "" or nova_senha == "":
                st.warning("Preencha todos os campos.")

            else:
                st.session_state.usuarios[novo_usuario] = {
                    "senha": nova_senha,
                    "movimentacoes": []
                }

                st.session_state.usuario_logado = novo_usuario
                st.rerun()

# ==============================
# SISTEMA PRINCIPAL
# ==============================

else:

    usuario = st.session_state.usuario_logado
    dados = st.session_state.usuarios[usuario]["movimentacoes"]

    st.title("💰 Controle Financeiro PRO")
    st.subheader(f"Bem-vindo, {usuario} 👋")

    if st.button("🚪 Logout"):
        st.session_state.usuario_logado = None
        st.rerun()

    st.divider()

    abas = st.tabs(["📊 Dashboard", "➕ Nova Movimentação", "📋 Histórico"])

    # ==============================
    # DASHBOARD
    # ==============================

    with abas[0]:

        if dados:

            df = pd.DataFrame(dados)

            receitas = df[df["tipo"] == "Receita"]["valor"].sum()
            despesas = df[df["tipo"] == "Despesa"]["valor"].sum()
            saldo = receitas - despesas

            col1, col2, col3 = st.columns(3)

            col1.metric("💵 Receitas", f"R$ {receitas:.2f}")
            col2.metric("💸 Despesas", f"R$ {despesas:.2f}")
            col3.metric("💰 Saldo", f"R$ {saldo:.2f}")

            st.divider()

            st.subheader("📊 Gastos por Categoria")

            despesas_df = df[df["tipo"] == "Despesa"]

            if not despesas_df.empty:
                categoria_total = despesas_df.groupby("categoria")["valor"].sum()
                st.bar_chart(categoria_total)
                st.write("Distribuição em Pizza")
                st.pyplot(categoria_total.plot.pie(autopct='%1.1f%%').figure)
            else:
                st.info("Nenhuma despesa registrada.")

        else:
            st.info("Nenhuma movimentação ainda.")

    # ==============================
    # NOVA MOVIMENTAÇÃO
    # ==============================

    with abas[1]:

        st.subheader("Adicionar Receita ou Despesa")

        tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor", min_value=0.0, format="%.2f")
        categoria = st.selectbox(
            "Categoria",
            ["Salário", "Alimentação", "Transporte", "Lazer", "Contas", "Outros"]
        )

        if st.button("Salvar Movimentação"):

            if descricao and valor > 0:

                dados.append({
                    "tipo": tipo,
                    "descricao": descricao,
                    "valor": valor,
                    "categoria": categoria
                })

                st.success("Movimentação registrada!")
                st.rerun()

            else:
                st.warning("Preencha corretamente.")

    # ==============================
    # HISTÓRICO
    # ==============================

    with abas[2]:

        if dados:

            df = pd.DataFrame(dados)

            filtro_tipo = st.selectbox("Filtrar por tipo", ["Todos", "Receita", "Despesa"])

            if filtro_tipo != "Todos":
                df = df[df["tipo"] == filtro_tipo]

            st.dataframe(df, use_container_width=True)

            st.divider()

            st.subheader("Excluir Movimentação")

            index_para_excluir = st.number_input(
                "Digite o índice da linha para excluir",
                min_value=0,
                max_value=len(dados)-1,
                step=1
            )

            if st.button("Excluir"):
                dados.pop(index_para_excluir)
                st.success("Movimentação excluída.")
                st.rerun()

        else:
            st.info("Nenhuma movimentação registrada.")
