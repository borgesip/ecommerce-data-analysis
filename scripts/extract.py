import pandas as pd

def extract_data(file_path):
    try:
        df = pd.read_csv(file_path, encoding='ISO-8859-1')
        print(f"Dados extraídos: {df.shape[0]} linhas")
        return df
    except Exception as e:
        print(f"Erro ao extrair dados: {e}")
        raise
