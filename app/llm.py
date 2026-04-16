# Importações de bibliotecas necessárias
from groq import Groq
import os
from dotenv import load_dotenv
import psycopg2

# Carrega as variáveis de ambiente e inicializa o cliente Groq
load_dotenv()
client = Groq(api_key=os.getenv("groq_api_key"))

# Função para consultar o banco de dados PostgreSQL
def consulta_banco(sql):
    conn = psycopg2.connect(
        dbname="loja",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# Contexto detalhado do banco de dados para o modelo de linguagem
contexto = '''Este banco representa um cenário simples de vendas.

Entidades principais:
- `clientes`: armazena dados cadastrais dos clientes.
- `vendedores`: armazena dados dos vendedores.
- `produtos`: armazena catálogo de produtos e preços.
- `vendas`: registra transações de venda, ligando cliente, vendedor e produto.

Relacionamentos:
- Uma venda pertence a um cliente por `vendas.idcliente -> clientes.idcliente`.
- Uma venda pertence a um vendedor por `vendas.idvendedor -> vendedores.idvendedor`.
- Uma venda pertence a um produto por `vendas.idproduto -> produtos.idproduto`.
- A tabela `vendas` é a tabela fato principal do modelo.

Grão da tabela `vendas`:
- Cada linha representa a venda de um único produto para um cliente, realizada por um vendedor, em uma data específica.
- Como existe apenas `idproduto` por linha, uma venda não representa um pedido com múltiplos itens; cada registro é um item vendido.

Regras implícitas importantes:
- `valor_total` tende a representar `quantidade * preco_venda`, mas o valor gravado na venda deve ser tratado como valor oficial da transação.
- `preco_custo` e `preco_venda` ficam em `produtos` e podem ser usados para cálculo de margem.
- `cpf`, `cep` e `telefone` são armazenados como texto, não como número.
- `estado` usa sigla de UF com 2 caracteres.
- Não há constraints visíveis de unicidade para `cpf` e `email`.
- Não há tabela de estoque, pagamento, devolução ou status de venda.

#### Dicionário de dados

##### Tabela `clientes`

Descrição:
Cadastro de clientes que realizam compras.

Campos:
- `idcliente` (`SERIAL`, chave primária): identificador único do cliente.
- `nome` (`VARCHAR(100)`): nome completo do cliente.
- `data_nascimento` (`DATE`): data de nascimento.
- `cpf` (`VARCHAR(14)`): CPF no formato `000.000.000-00`.
- `email` (`VARCHAR(150)`): e-mail do cliente.
- `telefone` (`VARCHAR(20)`): telefone de contato.
- `endereco` (`VARCHAR(150)`): logradouro e número.
- `bairro` (`VARCHAR(100)`): bairro do cliente.
- `cidade` (`VARCHAR(100)`): cidade do cliente.
- `estado` (`CHAR(2)`): unidade federativa, por exemplo `SP`, `RJ`, `MG`.
- `cep` (`VARCHAR(9)`): CEP no formato `00000-000`.

Uso analítico comum:
- identificar perfil cadastral e geográfico dos clientes;
- segmentar clientes por cidade, estado ou faixa etária;
- relacionar clientes com histórico de compras.

##### Tabela `vendedores`

Descrição:
Cadastro dos vendedores responsáveis pelas vendas.

Campos:
- `idvendedor` (`SERIAL`, chave primária): identificador único do vendedor.
- `nome` (`VARCHAR(100)`): nome do vendedor.
- `data_admissao` (`DATE`): data de entrada na empresa.
- `email` (`VARCHAR(150)`): e-mail corporativo ou de contato.

Uso analítico comum:
- medir volume vendido por vendedor;
- acompanhar desempenho individual ao longo do tempo;
- analisar produtividade por tempo de casa.

##### Tabela `produtos`

Descrição:
Catálogo de produtos comercializados.

Campos:
- `idproduto` (`SERIAL`, chave primária): identificador único do produto.
- `descricao` (`VARCHAR(150)`): nome ou descrição comercial do produto.
- `categoria` (`VARCHAR(100)`): categoria do produto.
- `preco_custo` (`NUMERIC(10,2)`): custo unitário do produto.
- `preco_venda` (`NUMERIC(10,2)`): preço unitário de venda.

Uso analítico comum:
- analisar mix de produtos e categorias;
- calcular faturamento por produto;
- estimar margem bruta com base em custo e preço de venda.

##### Tabela `vendas`

Descrição:
Tabela transacional que registra as vendas realizadas.

Campos:
- `idvenda` (`SERIAL`, chave primária): identificador único do registro de venda.
- `idcliente` (`INT`, chave estrangeira): referência para `clientes.idcliente`.
- `idvendedor` (`INT`, chave estrangeira): referência para `vendedores.idvendedor`.
- `idproduto` (`INT`, chave estrangeira): referência para `produtos.idproduto`.
- `quantidade` (`INT`): quantidade vendida do produto.
- `valor_total` (`NUMERIC(12,2)`): valor total da transação registrada na linha.
- `data_venda` (`DATE`): data em que a venda ocorreu.

Uso analítico comum:
- calcular faturamento por período;
- medir quantidade vendida por produto e categoria;
- cruzar desempenho de vendedores com perfil de clientes;
- analisar ticket por venda, cliente ou produto.

#### Interpretação semântica para consultas de LLM

Mapeamentos de negócio úteis:
- "faturamento" normalmente significa `SUM(vendas.valor_total)`.
- "quantidade vendida" normalmente significa `SUM(vendas.quantidade)`.
- "número de vendas" normalmente significa `COUNT(*)` na tabela `vendas`.
- "clientes que mais compraram" pode significar maior `SUM(valor_total)` ou maior `SUM(quantidade)`; o critério deve ser explicitado.
- "produto mais vendido" pode significar maior quantidade ou maior faturamento; o critério deve ser explicitado.
- "margem" pode ser estimada como `valor_total - (quantidade * preco_custo)` ao juntar `vendas` com `produtos`.

Junções padrão:
- `vendas` + `clientes`: análises por perfil e localização do cliente.
- `vendas` + `vendedores`: análises de desempenho comercial.
- `vendas` + `produtos`: análises por produto, categoria, preço e margem.

Limitações relevantes para interpretação:
- Não existe separação entre cabeçalho de pedido e itens de pedido.
- Não existe histórico de alteração de preço.
- Não existe cancelamento, desconto, forma de pagamento ou comissão.
- Não existe quantidade em estoque.
'''

# Função para gerar consulta SQL a partir de pergunta em linguagem natural usando o modelo de linguagem
def agente_dba(pergunta):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": f'''Você é uma analista especializado em gerar consultas SQL a partir de perguntas em linguagem natural. Você tem acesso a um banco de dados de vendas com as seguintes tabelas {contexto}.

            Dada a pergunta: {pergunta}, gere a consulta SQL correspondente. 
            Certifique-se de usar as junções corretas entre as tabelas.
            Responda apenas com a consulta SQL, sem explicações ou texto adicional.
            Nunca responda com explicações ou texto adicional, apenas a consulta SQL.
            ''',
            }
        ],
    )

    return completion.choices[0].message.content 



# Função para analisar os dados retornados do banco de dados e responder à pergunta original usando o modelo de linguagem
def agente_analista(pergunta, dados):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": f'''Você é um analista especializado em interpretar dados de uma loja de varejo.

            Dado a seguinte pergunta: {pergunta} e os dados {dados}, responda com uma análise suscinta, clara e objetiva.
            1 - Exiba os dados em formato de tabela, se possível, para facilitar a leitura.
            2 - Descreva os insights mais relevantes de forma direta, sem rodeios.
            3 - Seja direto e evite explicações desnecessárias.
            ''',
            }
        ],
        
    )

    return completion.choices[0].message.content


# Função para realizar a classificação da interação do usuario
def agente_roteamento(pergunta):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": f''' Você é um agente especializado em categorizar conversas. Seu trabalho é receber uma interação e definir se ela deve ser categorizada como chat ou query.
                
                1 - Interações como saudações você poder categorizar como *chat* e responder.
                2 - Interações que sugiram analises de dados ou consultas a banco de dados você deve categorizar como *query*
                3 - Responda apenas 1 palavra, chat ou query
                4 - Não coloque comentarios ou frases além da palavra de classificação
                           
                Essa é a interação: {pergunta}
            ''',
            }
        ],
        
    )

    return completion.choices[0].message.content


# Função para limpar a consulta SQL gerada, removendo quebras de linha, acentos e caracteres indesejados
def limpa_sql(sql):
    return sql.replace("\n", " ").replace("```", "").replace("sql", "").replace(";", "").replace("'", "").strip()



# Loop principal para interação com o usuário, onde ele pode fazer perguntas e receber respostas baseadas nos dados do banco
if __name__ == "__main__":
    pergunta = ""
    while pergunta.lower() != "sair":
        print("__________________________________________________________________________________________________") 
        print("\n#### Bem-vindo ao sistema de consulta de vendas! Digite 'sair' para encerrar. ####") 
        pergunta = input("\nDigite sua pergunta: ")

        if pergunta == "sair".lower():
            print("Valeu, até a proxima!")
            break
        
        classicacao = agente_roteamento(pergunta)
        print(f"\nClassificação: {classicacao}")
        
        if classicacao != "query":
            continue
        
        sql = agente_dba(pergunta)
        print(f"\nConsulta SQL gerada: \n {sql}")
        
        sql_limpo = limpa_sql(sql)
         
        print("__________________________________________________________________________________________________") 
        dados = consulta_banco(sql_limpo)
        print("\nResposta do banco de dados:\n")    
        for linha in dados:
            print(linha)
            
        print("__________________________________________________________________________________________________")    
        analise = agente_analista(pergunta, dados)
        print("\nAnálise dos dados:\n")
        print(analise)

