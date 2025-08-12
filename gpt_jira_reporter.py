# GPT Personalizado para Integração com API do Jira

# Requisitos: pip install -r requirements.txt
# Arquivo: gpt_jira_reporter.py

import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Optional
import streamlit as st
import openai

class JiraGPT:
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

    def search_issues(self, jql: str, fields: Optional[List[str]] = None, max_results: int = 1000) -> List[Dict]:
        url = f"{self.base_url}/rest/api/3/search"
        params = {
            "jql": jql,
            "maxResults": max_results
        }
        if fields:
            params["fields"] = ",".join(fields)
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json().get("issues", [])

    def list_issues_by_status(self, status: str) -> pd.DataFrame:
        jql = f"status = '{status}'"
        issues = self.search_issues(jql, fields=["summary", "assignee", "created"])
        return pd.DataFrame([
            {
                "ID": issue["key"],
                "Resumo": issue["fields"]["summary"],
                "Responsável": issue["fields"].get("assignee", {}).get("displayName", "Não atribuído"),
                "Criado em": issue["fields"]["created"]
            }
            for issue in issues
        ])

    def count_unassigned_issues(self) -> int:
        jql = "assignee IS EMPTY"
        return len(self.search_issues(jql))

    def count_issues_by_assignee(self) -> pd.DataFrame:
        issues = self.search_issues("assignee IS NOT EMPTY", fields=["assignee"])
        counts = {}
        for issue in issues:
            name = issue["fields"]["assignee"]["displayName"]
            counts[name] = counts.get(name, 0) + 1
        return pd.DataFrame(list(counts.items()), columns=["Responsável", "Quantidade de Tickets"])

    def avg_max_open_time_by_user(self) -> pd.DataFrame:
        issues = self.search_issues("statusCategory != Done", fields=["assignee", "created"])
        user_times = defaultdict(list)
        now = datetime.utcnow()
        for issue in issues:
            assignee = issue["fields"].get("assignee")
            if not assignee:
                continue
            name = assignee["displayName"]
            created = datetime.strptime(issue["fields"]["created"], "%Y-%m-%dT%H:%M:%S.%f%z").replace(tzinfo=None)
            open_time = (now - created).total_seconds() / 3600
            user_times[name].append(open_time)
        data = []
        for name, times in user_times.items():
            data.append({
                "Responsável": name,
                "Tempo Médio de Abertura (h)": sum(times) / len(times),
                "Tempo Máximo de Abertura (h)": max(times)
            })
        return pd.DataFrame(data)

    def top_users_with_open_issues(self, top_n=5) -> pd.DataFrame:
        df = self.count_issues_by_assignee()
        return df.sort_values(by="Quantidade de Tickets", ascending=False).head(top_n)

    def custom_report(self, project=None, status=None, assignee=None, priority=None, issue_type=None, created_after=None, created_before=None) -> pd.DataFrame:
        filters = []
        if project:
            filters.append(f"project = '{project}'")
        if status:
            filters.append(f"status = '{status}'")
        if assignee:
            filters.append(f"assignee = '{assignee}'")
        if priority:
            filters.append(f"priority = '{priority}'")
        if issue_type:
            filters.append(f"issuetype = '{issue_type}'")
        if created_after:
            filters.append(f"created >= '{created_after}'")
        if created_before:
            filters.append(f"created <= '{created_before}'")

        jql = " AND ".join(filters)
        issues = self.search_issues(jql, fields=["summary", "assignee", "created", "priority", "issuetype"])
        return pd.DataFrame([
            {
                "ID": issue["key"],
                "Resumo": issue["fields"]["summary"],
                "Responsável": issue["fields"].get("assignee", {}).get("displayName", "Não atribuído"),
                "Criado em": issue["fields"]["created"],
                "Prioridade": issue["fields"].get("priority", {}).get("name", "-"),
                "Tipo": issue["fields"].get("issuetype", {}).get("name", "-")
            }
            for issue in issues
        ])

    def export_to_csv(self, df: pd.DataFrame, filename: str):
        df.to_csv(filename, index=False)

    def export_to_excel(self, df: pd.DataFrame, filename: str):
        df.to_excel(filename, index=False)

    def plot_ticket_distribution(self, df: pd.DataFrame):
        df.plot(kind='bar', x='Responsável', y='Quantidade de Tickets', legend=False)
        plt.title("Distribuição de Tickets por Responsável")
        plt.ylabel("Quantidade")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

# Interface Web com Streamlit (PT/EN)
def main():
    st.set_page_config(page_title="JiraGPT Relatórios", layout="wide")
    st.title("GPT para Jira - Relatórios Inteligentes")
    lang = st.radio("Idioma / Language", ["Português", "English"])

    base_url = st.text_input("Jira URL", "https://suaempresa.atlassian.net")

    # Tenta pegar secrets, senão usa input manual
    api_token = st.secrets["JIRA_API_TOKEN"] if "JIRA_API_TOKEN" in st.secrets else st.text_input("Token de Acesso", type="password")
    gpt_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else st.text_input("OpenAI API Key (opcional)", type="password")

    if st.button("Conectar") and base_url and api_token:
        bot = JiraGPT(base_url, api_token)

        if gpt_key:
            prompt = st.text_input("Comando em linguagem natural")
            if st.button("Interpretar comando") and prompt:
                openai.api_key = gpt_key
                completion = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Você é um assistente que gera JQL para relatórios Jira."},
                        {"role": "user", "content": prompt}
                    ]
                )
                jql = completion.choices[0].message.content.strip()
                st.code(jql, language='sql')
                df = bot.search_issues(jql)
                st.write(pd.DataFrame(df))
                return

        opcao = st.selectbox("Escolha a ação", [
            "Listar tickets por status",
            "Contar tickets por responsável",
            "Tempo médio e máximo de abertura",
            "Top colaboradores com mais tickets abertos",
            "Gerar relatório customizado"
        ])

        if opcao == "Listar tickets por status":
            status = st.text_input("Status do ticket", "To Do")
            df = bot.list_issues_by_status(status)
            st.dataframe(df)

        elif opcao == "Contar tickets por responsável":
            df = bot.count_issues_by_assignee()
            st.dataframe(df)
            bot.plot_ticket_distribution(df)

        elif opcao == "Tempo médio e máximo de abertura":
            df = bot.avg_max_open_time_by_user()
            st.dataframe(df)

        elif opcao == "Top colaboradores com mais tickets abertos":
            n = st.slider("Top N", 1, 10, 5)
            df = bot.top_users_with_open_issues(n)
            st.dataframe(df)

        elif opcao == "Gerar relatório customizado":
            project = st.text_input("Projeto")
            status = st.text_input("Status")
            assignee = st.text_input("Responsável")
            priority = st.text_input("Prioridade")
            issue_type = st.text_input("Tipo de Issue")
            created_after = st.date_input("Criado após")
            created_before = st.date_input("Criado antes")
            df = bot.custom_report(project, status, assignee, priority, issue_type, created_after, created_before)
            st.dataframe(df)

            if st.button("Exportar para CSV"):
                bot.export_to_csv(df, "relatorio.csv")
                st.success("CSV exportado com sucesso!")

            if st.button("Exportar para Excel"):
                bot.export_to_excel(df, "relatorio.xlsx")
                st.success("Excel exportado com sucesso!")

if __name__ == "__main__":
    main()
