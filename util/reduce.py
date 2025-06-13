import pandas as pd
import os


arquivos = [
    'G1_1e7_1e1_0_0.csv',
    'G1_1e7_1e2_0_1.csv',
    'G1_1e7_2e0_0_0.csv',
    'G1_1e7_1e2_0_0.csv',
    'G1_1e7_1e2_5_0.csv'
]

entrada_dir = 'data/big'
saida_dir = 'data'

for nome_arquivo in arquivos:
    origem = os.path.join(entrada_dir, nome_arquivo)
    df = pd.read_csv(origem)
    n = int(df.shape[0] * 0.01)
    df = df.head(n)
    
    saida = os.path.join(saida_dir, nome_arquivo)
    df.to_csv(saida, index=False)
    print(f"Salvo: {saida} ({n} linhas)")
