import pandas as pd

ARQUIVO = "data/fipezap-serieshistoricas.xlsx"

CAPITAIS = [
    "Índice FipeZAP", "São Paulo", "Rio de Janeiro", "Belo Horizonte",
    "Porto Alegre", "Curitiba", "Florianópolis", "Salvador", "Fortaleza",
    "Recife", "Brasília", "Goiânia", "Manaus", "Belém", "Natal",
    "João Pessoa", "Maceió", "Aracaju", "Vitória", "Campo Grande", "Cuiabá"
]

def ler_aba(arquivo, cidade):
    df = pd.read_excel(arquivo, sheet_name=cidade, header=None)

    # O arquivo tem 56 colunas. Pegamos só as que interessam:
    # col 1  = Data
    # col 2-6  = Número-Índice de venda (Total, 1D, 2D, 3D, 4D)
    # col 7-11 = Var. mensal % de venda (Total, 1D, 2D, 3D, 4D)
    # col 17-21 = Preço médio R$/m² de venda (Total, 1D, 2D, 3D, 4D)
    colunas_interesse = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 17, 18, 19, 20, 21]
    df = df.iloc[4:, colunas_interesse].copy()  # pula 4 linhas de cabeçalho

    df.columns = [
        "data",
        "idx_total", "idx_1d", "idx_2d", "idx_3d", "idx_4d",
        "var_total", "var_1d", "var_2d", "var_3d", "var_4d",
        "preco_total", "preco_1d", "preco_2d", "preco_3d", "preco_4d"
    ]

    # Filtra só linhas com data válida
    df = df[pd.to_datetime(df["data"], errors="coerce").notna()].copy()
    df["data"] = pd.to_datetime(df["data"])

    # Converte para numérico — '.' vira NaN automaticamente
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["cidade"] = cidade
    df = df.reset_index(drop=True)
    return df[["cidade", "data"] + list(df.columns[1:-1])]


frames = []
for cidade in CAPITAIS:
    try:
        df_cidade = ler_aba(ARQUIVO, cidade)
        frames.append(df_cidade)
        print(f"OK: {cidade}")
    except Exception as e:
        print(f"ERRO em {cidade}: {e}")

df = pd.concat(frames, ignore_index=True)

print(f"\n{'='*50}")
print(f"Dataset final: {df.shape[0]} linhas x {df.shape[1]} colunas")
print(f"Período: {df['data'].min().strftime('%b/%Y')} até {df['data'].max().strftime('%b/%Y')}")
print(f"Cidades: {df['cidade'].nunique()}")
print(f"\nValores nulos por coluna:")
print(df.isnull().sum())
print(f"\nSão Paulo — últimos 3 meses (preço R$/m²):")
sp = df[df["cidade"] == "São Paulo"].tail(3)
print(sp[["data", "preco_1d", "preco_2d", "preco_3d", "preco_4d"]].to_string(index=False))

df.to_csv("data/fipezap_limpo.csv", index=False)
print("\nArquivo salvo: data/fipezap_limpo.csv")