
from datetime import datetime


FORMATO_DATA_HORA = "%d/%m/%Y %H:%M:%S"

LIMITE_ATENCAO = 50
LIMITE_ALERTA = 100


# PREPARAÇÃO DO HISTÓRICO

def preparar_historico(medicoes):

    if not isinstance(medicoes, list) or len(medicoes) < 2:
        raise ValueError("São necessárias pelo menos duas medições.")

    medicoes_ordenadas = sorted(
        medicoes,
        key=lambda item: datetime.strptime(
            item["data_hora"], FORMATO_DATA_HORA
        )
    )

    primeira_data = datetime.strptime(
        medicoes_ordenadas[0]["data_hora"],
        FORMATO_DATA_HORA
    )

    tempos = []
    niveis = []

    for medicao in medicoes_ordenadas:

        data = datetime.strptime(
            medicao["data_hora"],
            FORMATO_DATA_HORA
        )

        nivel = medicao["nivel_cm"]

        if not isinstance(nivel, (int, float)) or isinstance(nivel, bool):
            raise ValueError("Nível inválido.")

        if not 0 <= nivel <= 500:
            raise ValueError("Nível fora dos limites aceitos.")

        tempo = (data - primeira_data).total_seconds() / 60

        if tempos and tempo <= tempos[-1]:
            raise ValueError("Existem horários repetidos ou inválidos.")

        tempos.append(tempo)
        niveis.append(float(nivel))

    return tempos, niveis


# DERIVADAS E TAXAS DE VARIAÇÃO

def calcular_taxas(tempos, niveis):

    taxas = []

    for i in range(len(tempos) - 1):

        variacao_nivel = niveis[i + 1] - niveis[i]
        variacao_tempo = tempos[i + 1] - tempos[i]

        taxa = variacao_nivel / variacao_tempo

        taxas.append({
            "inicio": tempos[i],
            "fim": tempos[i + 1],
            "taxa_cm_min": taxa
        })

    return taxas


# INTERPOLAÇÃO DO NÍVEL

def interpolar_nivel(tempo, tempos, niveis):

    if tempo < tempos[0] or tempo > tempos[-1]:
        raise ValueError("Tempo fora do histórico.")

    for i in range(len(tempos) - 1):

        if tempos[i] <= tempo <= tempos[i + 1]:

            proporcao = (
                (tempo - tempos[i])
                / (tempos[i + 1] - tempos[i])
            )

            return (
                niveis[i]
                + proporcao * (niveis[i + 1] - niveis[i])
            )

    return niveis[-1]


# LIMITES E CRUZAMENTO DE NÍVEIS

def encontrar_cruzamento(limite, tempos, niveis):

    for i in range(len(tempos) - 1):

        nivel1 = niveis[i]
        nivel2 = niveis[i + 1]

        if nivel1 == limite:
            return tempos[i]

        if min(nivel1, nivel2) <= limite <= max(nivel1, nivel2):

            if nivel1 != nivel2:

                proporcao = (limite - nivel1) / (nivel2 - nivel1)

                return (
                    tempos[i]
                    + proporcao * (tempos[i + 1] - tempos[i])
                )

    if niveis[-1] == limite:
        return tempos[-1]

    return None


def analisar_limite(tempo_critico, tempos, niveis):

    intervalo = 0.0001

    if tempo_critico - intervalo < tempos[0]:
        raise ValueError("Não há histórico suficiente à esquerda.")

    if tempo_critico + intervalo > tempos[-1]:
        raise ValueError("Não há histórico suficiente à direita.")

    return {
        "esquerda": interpolar_nivel(
            tempo_critico - intervalo, tempos, niveis
        ),
        "direita": interpolar_nivel(
            tempo_critico + intervalo, tempos, niveis
        ),
        "valor": interpolar_nivel(
            tempo_critico, tempos, niveis
        )
    }


# INTEGRAL DA TAXA DE VARIAÇÃO

def integrar_taxas(taxas):

    acumulado = 0
    resultados = []

    for taxa in taxas:

        duracao = taxa["fim"] - taxa["inicio"]

        variacao = taxa["taxa_cm_min"] * duracao
        acumulado += variacao

        resultados.append({
            "fim": taxa["fim"],
            "acumulado_cm": acumulado
        })

    return resultados, acumulado


# INTEGRAL DE EXPOSIÇÃO ACIMA DO LIMITE DE ALERTA

def integrar_exposicao(tempos, niveis, limite=LIMITE_ALERTA):

    area_total = 0

    for i in range(len(tempos) - 1):

        t1 = tempos[i]
        t2 = tempos[i + 1]

        h1 = niveis[i]
        h2 = niveis[i + 1]

        duracao = t2 - t1

        excesso1 = max(h1 - limite, 0)
        excesso2 = max(h2 - limite, 0)

        if excesso1 > 0 and excesso2 > 0:

            area = (excesso1 + excesso2) * duracao / 2

        elif excesso1 == 0 and excesso2 > 0:

            tempo_acima = duracao * (h2 - limite) / (h2 - h1)
            area = excesso2 * tempo_acima / 2

        elif excesso1 > 0 and excesso2 == 0:

            tempo_acima = duracao * (h1 - limite) / (h1 - h2)
            area = excesso1 * tempo_acima / 2

        else:
            area = 0

        area_total += area

    return area_total


# CLASSIFICAÇÃO DO NÍVEL

def classificar_nivel(nivel):

    if nivel < LIMITE_ATENCAO:
        return "Normal"

    if nivel < LIMITE_ALERTA:
        return "Atenção"

    return "Alerta"


# ANÁLISE COMPLETA DO HISTÓRICO

def analisar_historico(medicoes):

    tempos, niveis = preparar_historico(medicoes)

    taxas = calcular_taxas(tempos, niveis)

    cruzamento_atencao = encontrar_cruzamento(
        LIMITE_ATENCAO, tempos, niveis
    )

    cruzamento_alerta = encontrar_cruzamento(
        LIMITE_ALERTA, tempos, niveis
    )

    integral_taxas, variacao_total = integrar_taxas(taxas)

    exposicao = integrar_exposicao(tempos, niveis)


    limites = {}

    if cruzamento_atencao is not None:
        try:
            limites["atencao"] = analisar_limite(
                cruzamento_atencao, tempos, niveis
            )
        except ValueError:
            limites["atencao"] = None

    if cruzamento_alerta is not None:
        try:
            limites["alerta"] = analisar_limite(
                cruzamento_alerta, tempos, niveis
            )
        except ValueError:
            limites["alerta"] = None

    # CLASSIFICAÇÃO ATUAL E HISTÓRICA

    classificacao_atual = classificar_nivel(niveis[-1])

    ordem_risco = {
        "Normal": 1,
        "Atenção": 2,
        "Alerta": 3
    }

    classificacao_historica = max(
        (classificar_nivel(nivel) for nivel in niveis),
        key=lambda classificacao: ordem_risco[classificacao]
    )

    return {
        "tempos": tempos,
        "niveis": niveis,
        "taxas": taxas,
        "integral_taxas": integral_taxas,
        "variacao_total": variacao_total,
        "exposicao": exposicao,
        "cruzamento_atencao": cruzamento_atencao,
        "cruzamento_alerta": cruzamento_alerta,
        "limites": limites,
        "classificacao_final": classificacao_atual,
        "classificacao_historica": classificacao_historica
    }
