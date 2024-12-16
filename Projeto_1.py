from datetime import datetime
import sqlite3
import streamlit as st


class Tarefa:
    def __init__(self, id, nome, descricao, data_limite, prioridade):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.data_limite = data_limite
        self.prioridade = prioridade


class GerenciadorDeTarefas:
    def __init__(self, db_name="tarefas.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.criar_tabela()

    def criar_tabela(self):
        query = '''
                    CREATE TABLE IF NOT EXISTS tarefas(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,    
                    nome TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    data_limite DATE,
                    prioridade TEXT NOT NULL
                    )
                '''
        self.cursor.execute(query)
        self.conn.commit()

    def adicionar_tarefa(self, nome, descricao, data_limite, prioridade):
        query = """
                    INSERT INTO tarefas (nome, descricao, data_limite, prioridade)
                    VALUES (?, ?, ?, ?)                    
            """
        self.cursor.execute(query, (nome, descricao, data_limite, prioridade))
        self.conn.commit()

    def listar_tarefas(self):
        query = '''
                    SELECT * FROM tarefas
                    ORDER BY prioridade DESC
                '''
        self.cursor.execute(query)
        self.conn.commit()
        return [Tarefa(*row) for row in self.cursor.fetchall()]

    def atualizar_tarefas(self, id, nome, descricao, data_limite, prioridade):
        query = '''
                    UPDATE tarefas
                    SET nome = ?,
                        descricao = ?,
                        data_limite = ?,
                        prioridade = ?
                    WHERE id = ?
                '''
        self.cursor.execute(
            query, (nome, descricao, data_limite, prioridade, id))
        self.conn.commit()

    def excluir_tarefa(self, id):
        query = '''
                    DELETE FROM tarefas
                    WHERE id = ?
                '''
        self.cursor.execute(query, (id,))
        self.conn.commit()


db = GerenciadorDeTarefas()


st.title('Gerenciador de Tarefas')

menu = st.sidebar.selectbox("Menu", [
                            "Adicionar Tarefa", "Visualizar Tarefas", "Atualizar Tarefa", "Excluir Tarefa"])

if menu == "Adicionar Tarefa":
    with st.form("form_adicionar"):
        nome = st.text_input("Nome da tarefa")
        descricao = st.text_input("Descrição da tarefa")
        data_limite = st.date_input("Prazo")
        prioridade = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"])
        submit = st.form_submit_button("Adicionar")

        if submit:
            db.adicionar_tarefa(nome, descricao, str(data_limite), prioridade)
            st.success('Tarefa adicionada com sucesso!')

elif menu == "Visualizar Tarefas":
    tarefas = db.listar_tarefas()
    if tarefas:
        for tarefa in tarefas:
            st.write(f"**{tarefa.nome} ('Prioridade: '{tarefa.prioridade})")
            st.write(f"Descrição: {tarefa.descricao} ")
            st.write(f"Prazo: {tarefa.data_limite} ")
            st.write("----------------------------")
    else:
        st.info("Nenhuma tarefa cadastrada.")

elif menu == "Atualizar Tarefa":
    tarefas = db.listar_tarefas()
    if tarefas:
        tarefa_id = st.selectbox("Selecione a tarefa a ser atualizada.", [
                                 tarefa.id for tarefa in tarefas])
        tarefa = next(tarefa for tarefa in tarefas if tarefa.id == tarefa_id)

        with st.form("form_atualizar"):
            nome = st.text_input("Nome da tarefa", value=tarefa.nome)
            descricao = st.text_input(
                "Descrição da tarefa", value=tarefa.descricao)
            data_limite = st.date_input(
                "Prazo: ", value=datetime.strptime(tarefa.data_limite, "%Y-%m-%d"))
            prioridade = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"], index=[
                                      "Alta", "Média", "Baixa"].index(tarefa.prioridade))
            submit = st.form_submit_button("Atualizar")

            if submit:
                db.atualizar_tarefas(
                    tarefa_id, nome, descricao, str(data_limite), prioridade)
                st.success("Tarefa atualizada com sucesso!")
    else:
        st.info("Nenhuma tarefa cadastrada.")


elif menu == "Excluir Tarefa":
    tarefas = db.listar_tarefas()
    if tarefas:
        tarefa_id = st.selectbox("Selecione a tarefa para ser excluída", [
                                 tarefa.id for tarefa in tarefas])
        if st.button("Excluir"):
            db.excluir_tarefa(tarefa_id)
            st.success("Tarefa excluída com sucesso!")
    else:
        st.info("Nenhuma tarefa cadastrada.")
