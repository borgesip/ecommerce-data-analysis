import psycopg2
from sqlalchemy import create_engine

def create_sales_table(conn):
    create_table_query = """
    DROP TABLE IF EXISTS sales;
    CREATE TABLE sales (
        invoiceno VARCHAR(20),
        stockcode VARCHAR(20),
        description TEXT,
        quantity INT,
        invoicedate TIMESTAMP,
        unitprice FLOAT,
        customerid VARCHAR(20),
        country VARCHAR(50),
        totalvalue FLOAT
    );
    """
    try:
        cur = conn.cursor()
        cur.execute(create_table_query)
        conn.commit()
        cur.close()
        print("Tabela 'sales' recriada com sucesso!")
    except Exception as e:
        print(f"Erro ao criar tabela: {e}")

def load_data(df, database_url):
    try:
        # Conectar e criar tabela
        conn = psycopg2.connect(database_url)
        create_sales_table(conn)
        conn.close()
        
        # Carregar dados
        engine = create_engine(database_url)
        df.to_sql('sales', engine, if_exists='append', index=False, method='multi', chunksize=1000)
        print("Dados carregados com sucesso!")
        
        # Validar
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sales;")
        count = cur.fetchone()[0]
        print(f"Total de registros na tabela 'sales': {count}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")