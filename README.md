# DataBrain

Projeto em Python que usa LLM para transformar perguntas em linguagem natural em consultas SQL e depois interpretar os resultados de um banco PostgreSQL.

Esse repositório faz parte do conteúdo do meu canal no YouTube. A ideia é evoluir o projeto aos poucos, registrar melhorias em vídeo.

## O que o projeto faz

Hoje o fluxo principal funciona assim:

1. O usuário digita uma pergunta sobre vendas.
2. Um modelo da Groq gera a consulta SQL com base no contexto do banco.
3. A aplicação executa a query no PostgreSQL.
4. Outro passo com LLM transforma os dados em uma resposta mais amigável.
<br>

Fluxo do projeto:
<br>

<img width="1890" height="870" alt="Captura de tela 2026-04-01 105843" src="https://github.com/user-attachments/assets/59eb4d06-2a56-4c55-9a4d-84febc27485e" />


## Estrutura atual

`app/llm.py`
Script principal com:
- conexão com o banco PostgreSQL;
- geração de SQL via LLM;
- execução da consulta;
- análise final dos resultados.

`app/tabelas.md`
Documentação do contexto analítico do banco, incluindo:
- tabelas;
- relacionamentos;
- regras de negócio;
- interpretações semânticas para as perguntas.

`docker-compose.yml`
Subida rápida de um PostgreSQL local para desenvolvimento.

## Tecnologias

- Python 3.12+
- Groq API
- PostgreSQL
- Docker Compose
- `uv` para gerenciamento de dependências

## Como rodar o projeto

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd databrain
```

### 2. Criar o arquivo de ambiente

Use o arquivo de exemplo como base:

```bash
cp .env.example .env
```

Depois preencha sua chave da Groq no arquivo `.env`.

### 3. Instalar as dependências

Se você usa `uv`:

```bash
uv sync
```

Ou, se preferir `pip`:

```bash
pip install -e .
```

### 4. Subir o PostgreSQL com Docker

```bash
docker compose up -d
```

### 5. Executar a aplicação

```bash
uv run python app/llm.py
```

## Banco de dados

O projeto foi pensado para um cenário simples de vendas com as tabelas:

- `clientes`
- `vendedores`
- `produtos`
- `vendas`

O contexto usado pelo modelo está documentado em `app/tabelas.md`.

## Exemplo de uso

Perguntas que combinam com o projeto:

- `Qual foi o faturamento total por mês?`
- `Quais produtos mais venderam em quantidade?`
- `Quem são os vendedores com maior faturamento?`
- `Qual categoria teve a maior margem estimada?`

## Próximos passos

Algumas melhorias naturais para as próximas versões:

- mover toda a configuração do banco para variáveis de ambiente;
- validar e sanitizar melhor o SQL gerado pelo modelo;
- criar seeds para popular o banco com dados de exemplo;
- adicionar interface web ou API;
- melhorar logs, tratamento de erros e testes;
- separar melhor os agentes e prompts.

## Aviso importante

No estado atual, a conexão com o banco está parcialmente fixa no código e a aplicação ainda pode ser melhorada em segurança, validação e organização. Isso faz parte da proposta do projeto: ir evoluindo publicamente a cada nova versão.
