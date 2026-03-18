import psycopg2

conn = psycopg2.connect(
    dbname="loja",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)

# teste de conexão
if  "__main__":
    cur = conn.cursor()    
    cur.execute("SELECT * FROM clientes")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    cur.close()
    conn.close()