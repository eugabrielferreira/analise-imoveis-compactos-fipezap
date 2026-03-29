import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ── Configuração visual ──────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "#f8f8f8",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "white",
    "grid.linewidth": 1.2,
    "font.family": "sans-serif",
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.titlepad": 12,
})

CORES = {
    "1D": "#E63946",   # vermelho
    "2D": "#457B9D",   # azul
    "3D": "#2A9D8F",   # verde
    "4D": "#F4A261",   # laranja
}

# ── Carrega o dataset limpo ──────────────────────────────────────────────────
df = pd.read_csv("data/fipezap_limpo.csv", parse_dates=["data"])

# Filtra apenas São Paulo para análises detalhadas
sp = df[df["cidade"] == "São Paulo"].copy()

# Remove meses sem dados por dormitório
sp_completo = sp.dropna(subset=["preco_1d", "preco_2d", "preco_3d", "preco_4d"])

print(f"São Paulo: {len(sp_completo)} meses com dados completos por dormitório")
print(f"Período: {sp_completo['data'].min().strftime('%b/%Y')} → {sp_completo['data'].max().strftime('%b/%Y')}\n")

# ── Gráfico 1 ────────────────────────────────────────────────────────────────
# Evolução do preço médio por m² em SP por número de dormitórios
fig, ax = plt.subplots(figsize=(12, 5))

for tipo, col, label in [
    ("1D", "preco_1d", "1 dormitório"),
    ("2D", "preco_2d", "2 dormitórios"),
    ("3D", "preco_3d", "3 dormitórios"),
    ("4D", "preco_4d", "4+ dormitórios"),
]:
    ax.plot(sp_completo["data"], sp_completo[col],
            color=CORES[tipo], linewidth=2, label=label)

ax.set_title("Imóveis de 1 dormitório lideram o preço por m² em São Paulo desde 2019\n"
             "Preço médio de venda (R$/m²) por tipologia — Jan/2013 a Fev/2026")
ax.set_ylabel("R$/m²")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R${x:,.0f}"))
ax.legend(loc="upper left", framealpha=0.9)
ax.set_xlabel("")

plt.tight_layout()
plt.savefig("data/grafico1_evolucao_sp.png", dpi=150, bbox_inches="tight")
plt.close()
print("Gráfico 1 salvo.")

# ── Gráfico 2 ────────────────────────────────────────────────────────────────
# Diferença percentual do preço/m² de 1D em relação a 2D (base)
sp_completo = sp_completo.copy()
sp_completo["premium_1d_vs_2d"] = (sp_completo["preco_1d"] / sp_completo["preco_2d"] - 1) * 100
sp_completo["premium_4d_vs_2d"] = (sp_completo["preco_4d"] / sp_completo["preco_2d"] - 1) * 100

fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(sp_completo["data"], sp_completo["premium_1d_vs_2d"],
        color=CORES["1D"], linewidth=2, label="1 dorm. vs 2 dorm.")
ax.plot(sp_completo["data"], sp_completo["premium_4d_vs_2d"],
        color=CORES["4D"], linewidth=2, label="4+ dorm. vs 2 dorm.")
ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")

ax.set_title("O prêmio por m² do imóvel compacto cresceu 40 pontos percentuais em 10 anos\n"
             "São Paulo — diferença % do preço/m² em relação a imóveis de 2 dormitórios")
ax.set_ylabel("Diferença (%)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:+.0f}%"))
ax.legend(framealpha=0.9)

plt.tight_layout()
plt.savefig("data/grafico2_premium_sp.png", dpi=150, bbox_inches="tight")
plt.close()
print("Gráfico 2 salvo.")

# ── Gráfico 3 ────────────────────────────────────────────────────────────────
# Comparativo entre capitais: preço/m² de 1D vs 4D no último mês disponível
ultimo_mes = df["data"].max()
df_recente = df[df["data"] == ultimo_mes].dropna(subset=["preco_1d", "preco_4d"])
df_recente = df_recente[df_recente["cidade"] != "Índice FipeZAP"].copy()
df_recente["razao_1d_4d"] = df_recente["preco_1d"] / df_recente["preco_4d"]
df_recente = df_recente.sort_values("razao_1d_4d", ascending=True)

fig, ax = plt.subplots(figsize=(10, 7))

cores_barras = ["#E63946" if r >= 1 else "#457B9D" for r in df_recente["razao_1d_4d"]]
bars = ax.barh(df_recente["cidade"], df_recente["razao_1d_4d"], color=cores_barras, edgecolor="white")
ax.axvline(1.0, color="gray", linewidth=1.2, linestyle="--", label="Paridade (1D = 4D por m²)")

ax.set_title(f"Em quais capitais o imóvel compacto é mais caro por m²?\n"
             f"Razão preço/m² (1 dorm. ÷ 4+ dorm.) — {ultimo_mes.strftime('%b/%Y')}")
ax.set_xlabel("Razão (> 1 = 1D mais caro por m²)")
ax.legend()

for bar, val in zip(bars, df_recente["razao_1d_4d"]):
    ax.text(val + 0.01, bar.get_y() + bar.get_height()/2,
            f"{val:.2f}x", va="center", fontsize=9)

plt.tight_layout()
plt.savefig("data/grafico3_capitais_razao.png", dpi=150, bbox_inches="tight")
plt.close()
print("Gráfico 3 salvo.")

# ── Gráfico 4 ────────────────────────────────────────────────────────────────
# Valorização acumulada desde 2019 por tipologia — São Paulo
sp_2019 = sp_completo[sp_completo["data"] >= "2019-01-01"].copy()
base = sp_2019[sp_2019["data"] == sp_2019["data"].min()].iloc[0]

for col in ["preco_1d", "preco_2d", "preco_3d", "preco_4d"]:
    sp_2019[f"val_{col}"] = (sp_2019[col] / base[col] - 1) * 100

fig, ax = plt.subplots(figsize=(12, 5))

for tipo, col, label in [
    ("1D", "val_preco_1d", "1 dormitório"),
    ("2D", "val_preco_2d", "2 dormitórios"),
    ("3D", "val_preco_3d", "3 dormitórios"),
    ("4D", "val_preco_4d", "4+ dormitórios"),
]:
    ax.plot(sp_2019["data"], sp_2019[col],
            color=CORES[tipo], linewidth=2, label=label)

val_final = {
    "1D": sp_2019["val_preco_1d"].iloc[-1],
    "2D": sp_2019["val_preco_2d"].iloc[-1],
    "3D": sp_2019["val_preco_3d"].iloc[-1],
    "4D": sp_2019["val_preco_4d"].iloc[-1],
}
for tipo, val in val_final.items():
    print(f"  Valorização desde Jan/2019 — {tipo}: +{val:.1f}%")

ax.set_title("Desde 2019, imóveis de 1 dormitório valorizaram mais que todos os outros tipos\n"
             "São Paulo — valorização acumulada do preço/m² por tipologia (base = Jan/2019)")
ax.set_ylabel("Valorização acumulada (%)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:+.0f}%"))
ax.legend(loc="upper left", framealpha=0.9)

plt.tight_layout()
plt.savefig("data/grafico4_valorizacao_2019.png", dpi=150, bbox_inches="tight")
plt.close()
print("Gráfico 4 salvo.")

print("\nTodos os gráficos salvos na pasta data/")
print("Arquivos: grafico1_evolucao_sp.png, grafico2_premium_sp.png,")
print("          grafico3_capitais_razao.png, grafico4_valorizacao_2019.png")