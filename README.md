# GPT Jira Reporter

Um assistente GPT integrado à API do Jira que gera relatórios operacionais em tempo real ou assíncronos, com interface web e suporte a comandos em linguagem natural.

## 🚀 Funcionalidades

- Conexão com instância Jira via token de acesso
- Consultas dinâmicas com filtros por projeto, status, responsável, tipo e data
- Relatórios exportáveis em CSV e Excel
- Visualizações em gráfico de tickets por responsável
- Suporte multilíngue (PT/EN)
- Interpretação de linguagem natural com GPT-4 (opcional)

## 📦 Instalação

```bash
git clone https://github.com/seuusuario/gpt-jira-reporter.git
cd gpt-jira-reporter
pip install -r requirements.txt
```

## ▶️ Execução

```bash
streamlit run gpt_jira_reporter.py
```

## 🧠 Modo de uso com linguagem natural (opcional)

Informe sua **OpenAI API Key** para digitar comandos como:

- "Quantos tickets estão abertos no projeto XYZ?"
- "Listar tarefas do tipo Bug abertas em julho com prioridade Alta."

## 🔐 Requisitos

- Token de acesso do Jira (API Token)
- URL da sua instância (ex: `https://suaempresa.atlassian.net`)
- (Opcional) Chave da API da OpenAI

## 🐳 Deploy com Docker

```bash
docker build -t jira-gpt .
docker run -p 8501:8501 jira-gpt
```

## 📝 Licença

MIT
