from pipeline.extract import extract_data
from pipeline.transform import transform_data
from pipeline.load import save_transformed_data

def main():
    # 1. Extração
    df_raw = extract_data()

    # 2. Transformação
    df_transformed = transform_data(df_raw)

    # 3. Load
    output_path = 'data/processed/OnlineRetail_transformed.csv'
    save_transformed_data(df_transformed, output_path)

if __name__ == "__main__":
    main()
