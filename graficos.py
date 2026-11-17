
import matplotlib.pyplot as plt

from problem_solving import analisar_historico


def gerar_graficos(medicoes):

    resultado = analisar_historico(medicoes)

    tempos = resultado["tempos"]
    niveis = resultado["niveis"]
    taxas = resultado["taxas"]

    # GRÁFICO 1: NÍVEL DA ÁGUA

    plt.figure(figsize=(10, 5))

    plt.plot(
        tempos,
        niveis,
        marker="o",
        label="Nível da água"
    )

    plt.axhline(
        y=50,
        linestyle="--",
        label="Limite de atenção"
    )

    plt.axhline(
        y=100,
        linestyle="--",
        label="Limite de alerta"
    )

    plt.title("Evolução do nível da água")
    plt.xlabel("Tempo (minutos)")
    plt.ylabel("Nível (cm)")
    plt.legend()
    plt.grid()

    plt.tight_layout()


    # GRÁFICO 2: TAXA DE VARIAÇÃO

    intervalos = []
    valores_taxas = []
    larguras = []

    for taxa in taxas:

        meio = (taxa["inicio"] + taxa["fim"]) / 2
        duracao = taxa["fim"] - taxa["inicio"]

        intervalos.append(meio)
        valores_taxas.append(taxa["taxa_cm_min"])
        larguras.append(duracao * 0.7)

    plt.figure(figsize=(10, 5))

    plt.bar(
        intervalos,
        valores_taxas,
        width=larguras,
        label="Taxa de variação"
    )

    plt.axhline(y=0, linestyle="--")

    plt.title("Taxa de variação do nível da água")
    plt.xlabel("Tempo (minutos)")
    plt.ylabel("Taxa (cm/min)")
    plt.legend()
    plt.grid(axis="y")

    plt.tight_layout()


    # GRÁFICO 3: EXPOSIÇÃO ACIMA DO ALERTA

    plt.figure(figsize=(10, 5))

    plt.plot(
        tempos,
        niveis,
        marker="o",
        label="Nível da água"
    )

    plt.axhline(
        y=100,
        linestyle="--",
        label="Limite de alerta"
    )

    plt.fill_between(
        tempos,
        niveis,
        100,
        where=[nivel > 100 for nivel in niveis],
        interpolate=True,
        alpha=0.3,
        label="Exposição acima do alerta"
    )

    plt.title("Exposição acima do limite de alerta")
    plt.xlabel("Tempo (minutos)")
    plt.ylabel("Nível (cm)")
    plt.legend()
    plt.grid()

    plt.tight_layout()

    plt.show()
