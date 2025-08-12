# 📘 API_REFERENCE.md

Documentação técnica da integração entre o GPT Jira Reporter e a API do Jira.

---

## 🔐 Autenticação

O app utiliza **token de API (API Token)** da Atlassian, fornecido pelo usuário na interface Streamlit.

- O token deve ser gerado em: [https://id.atlassian.com/manage/api-tokens](https://id.atlassian.com/manage/api-tokens)
- É usado no header das requisições:
  ```
  Authorization: Bearer <API_TOKEN>
  ```

---

## 🌐 Endpoints Utilizados

O app usa os endpoints REST da **Jira Cloud API v3**.

### 🔍 Buscar issues (filtro dinâmico)

```
GET /rest/api/3/search
```

Usado para:

- Buscar tickets por status, prioridade, tipo, projeto, responsável, etc.
- Aceita JQL dinâmico gerado por filtros ou via GPT-4

Exemplo de JQL:
```sql
project = ABC AND status = "To Do" AND assignee IS NOT EMPTY
```

---

### 👤 Assignee (usuário responsável)

A API retorna o campo:

```json
"assignee": {
  "displayName": "João Silva",
  ...
}
```

---

### 🗂️ Campos recuperados por padrão

Ao fazer `search_issues()`, os seguintes campos são requisitados:
- `summary`
- `created`
- `assignee`
- `priority`
- `issuetype`

---

## 🤖 GPT-4 + Linguagem Natural

Caso o usuário insira um comando em linguagem natural, o app utiliza a API da OpenAI para gerar a JQL correspondente:

Exemplo:
- **Input:** `"Listar bugs abertos com prioridade alta criados em julho"`
- **Prompt enviado ao GPT:**  
  ```
  Você é um assistente que gera JQL para relatórios Jira. Converta este comando em JQL:
  "Listar bugs abertos com prioridade alta criados em julho"
  ```

- **Resposta esperada:**
  ```sql
  issuetype = Bug AND status != Done AND priority = High AND created >= "2025-07-01" AND created <= "2025-07-31"
  ```

---

## ⚠️ Limitações da API

- O endpoint `/search` retorna no máximo 1000 resultados por padrão
- O campo `created` vem em ISO 8601 (UTC)
- Alguns campos podem variar de nome em projetos personalizados
- A API exige permissões adequadas para o token fornecido

---

## 🧪 Testes recomendados

- Token inválido → erro 401
- JQL inválido → erro 400 com mensagem descritiva
- Projetos privados exigem que o token tenha acesso explícito

---

