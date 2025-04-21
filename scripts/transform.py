# scripts/transform.py
def transform_data(df):
    # Remover linhas com customerid nulo ou vazio
    df = df.dropna(subset=['CustomerID'])
    df = df[df['CustomerID'] != '']
    
    # Converter tipos
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['CustomerID'] = df['CustomerID'].astype(str)
    df['Quantity'] = df['Quantity'].astype(int)
    df['UnitPrice'] = df['UnitPrice'].astype(float)
    
    # Remover quantidades negativas (devoluções)
    df = df[df['Quantity'] > 0]
    
    # Calcular totalvalue
    df['totalvalue'] = df['Quantity'] * df['UnitPrice']
    
    # Renomear colunas para corresponder ao schema do banco
    df = df.rename(columns={
        'InvoiceNo': 'invoiceno',
        'StockCode': 'stockcode',
        'Description': 'description',
        'Quantity': 'quantity',
        'InvoiceDate': 'invoicedate',
        'UnitPrice': 'unitprice',
        'CustomerID': 'customerid',
        'Country': 'country'
    })
    
    return df
