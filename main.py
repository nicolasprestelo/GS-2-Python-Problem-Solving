import json
import math
import os
import tempfile
from datetime import datetime

from problem_solving import analisar_historico
from graficos import gerar_graficos

ARQUIVO_DADOS = "dados_prevIA_Hydro.json"

INTERVALO_MEDICAO_MINUTOS = 5

LIMITE_NORMAL_ATENCAO, LIMITE_ATENCAO_ALERTA = (50, 100)

NIVEL_MINIMO_SENSOR, NIVEL_MAXIMO_SENSOR, VARIACAO_MAXIMA = (0, 500, 100)

FORMATO_DATA_HORA = "%d/%m/%Y %H:%M:%S"

pontos_monitorados = []


def data_hora_valida(data_hora):
    if not isinstance(data_hora, str):
        return False

    try:
        data_convertida = datetime.strptime(data_hora, FORMATO_DATA_HORA)
    except ValueError:
        return False

    return data_convertida.strftime(FORMATO_DATA_HORA) == data_hora


def nivel_numerico_finito(nivel_cm):
    if not isinstance(nivel_cm, (int, float)) or isinstance(nivel_cm, bool):
        return False

    try:
        return math.isfinite(nivel_cm)
    except OverflowError:
        return False


def nivel_valido_para_persistencia(nivel_cm):
    return (
        nivel_numerico_finito(nivel_cm)
        and NIVEL_MINIMO_SENSOR <= nivel_cm <= NIVEL_MAXIMO_SENSOR
    )


def medicao_valida_para_persistencia(medicao):
    if not isinstance(medicao, dict):
        return False

    return (
        nivel_valido_para_persistencia(medicao.get("nivel_cm"))
        and data_hora_valida(medicao.get("data_hora"))
    )


def medicoes_validas_para_persistencia(medicoes):
    if not isinstance(medicoes, list):
        return False

    horarios_registrados = set()

    for medicao in medicoes:
        if not medicao_valida_para_persistencia(medicao):
            return False

        data_hora = medicao["data_hora"]

        if data_hora in horarios_registrados:
            return False

        horarios_registrados.add(data_hora)

    return True


def medicao_utilizavel_na_analise(medicao):
    if not isinstance(medicao, dict):
        return False

    return (
        nivel_numerico_finito(medicao.get("nivel_cm"))
        and data_hora_valida(medicao.get("data_hora"))
    )


def estrutura_dados_valida(pontos):
    if not isinstance(pontos, list):
        return False

    ids_registrados = set()

    for ponto in pontos:
        if not isinstance(ponto, dict):
            return False

        id_ponto = ponto.get("id")

        if (
            not isinstance(id_ponto, int)
            or isinstance(id_ponto, bool)
            or id_ponto <= 0
            or id_ponto in ids_registrados
        ):
            return False

        if not isinstance(ponto.get("nome"), str) or not ponto["nome"].strip():
            return False

        if (
            not isinstance(ponto.get("localizacao"), str)
            or not ponto["localizacao"].strip()
        ):
            return False

        if not medicoes_validas_para_persistencia(ponto.get("medicoes")):
            return False

        ids_registrados.add(id_ponto)

    return True


def carregar_dados(caminho=ARQUIVO_DADOS):
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            pontos = json.load(arquivo)

        if estrutura_dados_valida(pontos):
            return pontos

        print("\nErro: a estrutura ou os dados do arquivo JSON são inválidos.")
        print("O sistema não será iniciado para evitar a perda dos dados.")
        return None
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("\nErro: o arquivo JSON está corrompido ou possui formato inválido.")
        print("O sistema não será iniciado para evitar a perda dos dados.")
        return None
    except UnicodeDecodeError as erro:
        print(f"\nErro ao ler o arquivo de dados: {erro}")
        return None
    except ValueError as erro:
        print(f"\nErro: o arquivo JSON possui dados inválidos: {erro}")
        print("O sistema não será iniciado para evitar a perda dos dados.")
        return None
    except OSError as erro:
        print(f"\nErro ao ler o arquivo de dados: {erro}")
        return None


def salvar_dados(pontos, caminho=ARQUIVO_DADOS):
    if not estrutura_dados_valida(pontos):
        print("\nErro ao salvar os dados: a estrutura dos dados é inválida.")
        return False

    nome_temporario = None

    try:
        caminho_absoluto = os.path.abspath(caminho)
        diretorio = os.path.dirname(caminho_absoluto)
        descritor, nome_temporario = tempfile.mkstemp(
            prefix="dados_prevIA_Hydro_",
            suffix=".tmp",
            dir=diretorio
        )

        with os.fdopen(descritor, "w", encoding="utf-8") as arquivo:
            json.dump(
                pontos,
                arquivo,
                ensure_ascii=False,
                indent=4,
                allow_nan=False
            )
            arquivo.flush()
            os.fsync(arquivo.fileno())

        os.replace(nome_temporario, caminho_absoluto)
        nome_temporario = None
        return True
    except (OSError, TypeError, ValueError) as erro:
        print(f"\nErro ao salvar os dados: {erro}")
        return False
    finally:
        if nome_temporario is not None:
            try:
                os.remove(nome_temporario)
            except OSError:
                pass


def obter_proximo_id(pontos):
    maior_id = 0

    for ponto in pontos:
        if ponto["id"] > maior_id:
            maior_id = ponto["id"]

    return maior_id + 1


def exibir_menu():
    print("\n--- PrevIA Hydro: Monitoramento Preventivo de Enchentes ---")
    print("1 - Cadastrar ponto monitorado")
    print("2 - Registrar medição do nível da água")
    print("3 - Consultar pontos e medições")
    print("4 - Analisar situação de um ponto")
    print("5 - Identificar possíveis falhas de sensor")
    print("6 - Análise matemática e gráficos")
    print("0 - Sair")


def listar_pontos_resumidos(pontos):
    for ponto in pontos:
        print(f"ID {ponto['id']} - {ponto['nome']} ({ponto['localizacao']})")


def buscar_ponto_por_id(pontos, id_ponto):
    for ponto in pontos:
        if ponto["id"] == id_ponto:
            return ponto

    return None


def selecionar_ponto(pontos):
    if not pontos:
        print("\nNão há pontos monitorados cadastrados.")
        return None

    print("\nPontos disponíveis:")
    listar_pontos_resumidos(pontos)

    while True:
        try:
            id_ponto = int(input("Digite o ID do ponto: "))
            ponto = buscar_ponto_por_id(pontos, id_ponto)

            if ponto is not None:
                return ponto

            print("Ponto não encontrado. Digite um ID da lista.")
        except ValueError:
            print("Entrada inválida. Digite apenas o número do ID.")


def obter_nivel_agua():
    while True:
        try:
            texto_nivel = input("Digite o nível da água em centímetros: ").strip()
            nivel_cm = float(texto_nivel.replace(",", "."))

            if not math.isfinite(nivel_cm):
                print("Entrada inválida. Digite um número finito.")
            elif nivel_cm < NIVEL_MINIMO_SENSOR or nivel_cm > NIVEL_MAXIMO_SENSOR:
                print(
                    f"O nível deve estar entre {NIVEL_MINIMO_SENSOR} e "
                    f"{NIVEL_MAXIMO_SENSOR} cm."
                )
            else:
                return nivel_cm
        except ValueError:
            print("Entrada inválida. Digite um número, como 45 ou 45,5.")


def gerar_data_hora():
    return datetime.now().strftime(FORMATO_DATA_HORA)


def cadastrar_ponto(pontos):
    print("\n--- Cadastro de ponto monitorado ---")

    while True:
        nome = input("Digite o nome do ponto: ").strip()

        if nome:
            break

        print("O nome do ponto não pode ficar vazio.")

    while True:
        localizacao = input("Digite a localização do ponto: ").strip()

        if localizacao:
            break

        print("A localização do ponto não pode ficar vazia.")

    novo_ponto = {
        "id": obter_proximo_id(pontos),
        "nome": nome,
        "localizacao": localizacao,
        "medicoes": []
    }
    pontos_candidatos = pontos + [novo_ponto]

    if salvar_dados(pontos_candidatos):
        pontos.append(novo_ponto)
        print(f"\nPonto '{nome}' cadastrado e salvo com sucesso!")
    else:
        print(f"\nNão foi possível cadastrar o ponto '{nome}'.")


def classificar_nivel(nivel_cm):
    if not nivel_valido_para_persistencia(nivel_cm):
        return None

    if nivel_cm < LIMITE_NORMAL_ATENCAO:
        return "Normal"
    elif nivel_cm < LIMITE_ATENCAO_ALERTA:
        return "Atenção"
    else:
        return "Alerta"


def ordenar_medicoes_por_data(medicoes):
    if not medicoes_validas_para_persistencia(medicoes):
        return None

    return sorted(
        medicoes,
        key=lambda medicao: datetime.strptime(medicao["data_hora"], FORMATO_DATA_HORA)
    )


def calcular_velocidade_elevacao(medicao_anterior, medicao_atual):
    if medicao_anterior is None:
        return None

    if (
        not medicao_utilizavel_na_analise(medicao_anterior)
        or not medicao_utilizavel_na_analise(medicao_atual)
    ):
        return None

    data_anterior = datetime.strptime(medicao_anterior["data_hora"], FORMATO_DATA_HORA)
    data_atual = datetime.strptime(medicao_atual["data_hora"], FORMATO_DATA_HORA)
    intervalo_minutos = (data_atual - data_anterior).total_seconds() / 60

    if intervalo_minutos <= 0:
        return None

    diferenca_nivel = medicao_atual["nivel_cm"] - medicao_anterior["nivel_cm"]
    return diferenca_nivel / intervalo_minutos


def identificar_motivos_falha(medicao, medicao_anterior):
    motivos = []

    if not medicao_utilizavel_na_analise(medicao):
        motivos.append(
            "A medição atual possui dados inválidos e não pode ser utilizada na análise."
        )
        return motivos

    nivel_cm = medicao["nivel_cm"]

    if nivel_cm < NIVEL_MINIMO_SENSOR:
        motivos.append("A leitura possui nível abaixo de 0 cm.")

    if nivel_cm > NIVEL_MAXIMO_SENSOR:
        motivos.append("A leitura está acima de 500 cm.")

    if medicao_anterior is None:
        return motivos

    if not medicao_utilizavel_na_analise(medicao_anterior):
        motivos.append(
            "A medição anterior possui dados inválidos e não pode ser utilizada na análise."
        )
        return motivos

    variacao = abs(nivel_cm - medicao_anterior["nivel_cm"])

    if variacao > VARIACAO_MAXIMA:
        motivos.append("A variação em relação à medição anterior é maior que 100 cm.")

    return motivos



def registrar_medicao(pontos):
    print("\n--- Registro de medição ---")
    ponto = selecionar_ponto(pontos)

    if ponto is None:
        return

    if not medicoes_validas_para_persistencia(ponto.get("medicoes")):
        print("\nNão foi possível registrar a medição porque o histórico possui dados inválidos.")
        return

    # VERIFICAÇÃO DO INTERVALO ENTRE MEDIÇÕES

    medicoes_ordenadas = ordenar_medicoes_por_data(ponto["medicoes"])

    if medicoes_ordenadas is None:
        print("\nNão foi possível analisar o histórico.")
        return

    if medicoes_ordenadas:
        ultima_medicao = medicoes_ordenadas[-1]

        horario_anterior = datetime.strptime(
            ultima_medicao["data_hora"],
            FORMATO_DATA_HORA
        )

        horario_atual = datetime.now()

        intervalo_real = (
            horario_atual - horario_anterior
        ).total_seconds() / 60

        if intervalo_real < 0:
            print("\nO horário do computador é anterior à última medição.")
            print("Verifique a data e a hora do sistema.")
            return

        if intervalo_real < INTERVALO_MEDICAO_MINUTOS:
            tempo_restante = INTERVALO_MEDICAO_MINUTOS - intervalo_real

            print(
                f"\nAguarde aproximadamente {tempo_restante:.1f} "
                "minutos para registrar a próxima medição."
            )
            return

    # REGISTRO DA NOVA MEDIÇÃO

    nivel_cm = obter_nivel_agua()

    nova_medicao = {
        "nivel_cm": nivel_cm,
        "data_hora": gerar_data_hora()
    }

    for medicao in ponto["medicoes"]:
        if medicao["data_hora"] == nova_medicao["data_hora"]:
            print("\nJá existe uma medição registrada para este ponto nesse horário.")
            return

    medicoes_candidatas = ponto["medicoes"] + [nova_medicao]
    medicoes_ordenadas = ordenar_medicoes_por_data(medicoes_candidatas)

    if medicoes_ordenadas is None:
        print("\nNão foi possível registrar a medição porque o histórico possui dados inválidos.")
        return

    medicao_anterior = None

    for indice, medicao in enumerate(medicoes_ordenadas):
        if medicao is nova_medicao:
            if indice > 0:
                medicao_anterior = medicoes_ordenadas[indice - 1]
            break

    ponto_candidato = ponto.copy()
    ponto_candidato["medicoes"] = medicoes_candidatas
    pontos_candidatos = []

    for ponto_atual in pontos:
        if ponto_atual is ponto:
            pontos_candidatos.append(ponto_candidato)
        else:
            pontos_candidatos.append(ponto_atual)

    if salvar_dados(pontos_candidatos):
        ponto["medicoes"].append(nova_medicao)
        print("\nMedição registrada e salva com sucesso!")
    else:
        print("\nNão foi possível registrar a medição.")
        return

    motivos = identificar_motivos_falha(nova_medicao, medicao_anterior)

    if motivos:
        print("Possível falha de sensor identificada:")

        for motivo in motivos:
            print(f"- {motivo}")

def consultar_pontos_e_medicoes(pontos):
    print("\n--- Consulta de pontos e medições ---")

    if not pontos:
        print("Nenhum ponto monitorado foi cadastrado.")
        return

    for ponto in pontos:
        print(f"\nID: {ponto['id']}")
        print(f"Nome: {ponto['nome']}")
        print(f"Localização: {ponto['localizacao']}")

        if not ponto["medicoes"]:
            print("Medições: nenhuma medição registrada.")
            continue

        print("Medições:")
        medicao_anterior = None
        medicoes_ordenadas = ordenar_medicoes_por_data(ponto["medicoes"])

        if medicoes_ordenadas is None:
            print("Não foi possível consultar as medições porque há dados inválidos.")
            continue

        for medicao in medicoes_ordenadas:
            categoria = classificar_nivel(medicao["nivel_cm"])
            print(
                f"- {medicao['data_hora']} | "
                f"Nível: {medicao['nivel_cm']:.2f} cm | "
                f"Situação: {categoria}"
            )

            motivos = identificar_motivos_falha(medicao, medicao_anterior)
            if motivos:
                print("  Possível falha: " + " ".join(motivos))

            medicao_anterior = medicao


def analisar_situacao_ponto(pontos):
    print("\n--- Análise da situação do ponto ---")
    ponto = selecionar_ponto(pontos)

    if ponto is None:
        return

    if not ponto["medicoes"]:
        print("Esse ponto ainda não possui medições para análise.")
        return

    medicoes_ordenadas = ordenar_medicoes_por_data(ponto["medicoes"])

    if medicoes_ordenadas is None:
        print("Não foi possível analisar o ponto porque há dados inválidos nas medições.")
        return

    medicao_atual = medicoes_ordenadas[-1]
    medicao_anterior = None

    if len(medicoes_ordenadas) >= 2:
        medicao_anterior = medicoes_ordenadas[-2]

    categoria = classificar_nivel(medicao_atual["nivel_cm"])
    print(f"\nPonto: {ponto['nome']}")
    print(f"Última medição: {medicao_atual['data_hora']}")
    print(f"Nível atual: {medicao_atual['nivel_cm']:.2f} cm")
    print(f"Situação: {categoria}")

    velocidade = calcular_velocidade_elevacao(medicao_anterior, medicao_atual)

    if velocidade is None:
        print("Velocidade de elevação: não foi possível calcular.")
        print("São necessárias duas medições em horários diferentes.")
    else:
        print(f"Velocidade de elevação: {velocidade:.2f} cm por minuto")

    motivos = identificar_motivos_falha(medicao_atual, medicao_anterior)

    if motivos:
        print("Possível falha de sensor:")
        for motivo in motivos:
            print(f"- {motivo}")
    else:
        print("Nenhuma possível falha foi identificada na última medição.")


def analisar_problem_solving(pontos):

    print("\n--- Análise matemática do prevIA Hydro ---")

    ponto = selecionar_ponto(pontos)

    if ponto is None:
        return

    medicoes = ponto["medicoes"]

    if len(medicoes) < 2:
        print("São necessárias pelo menos duas medições.")
        return

    try:
        resultado = analisar_historico(medicoes)

        print(f"\nPonto: {ponto['nome']}")

        print("\n--- TAXAS DE VARIAÇÃO ---")

        for taxa in resultado["taxas"]:
            print(
                f"Intervalo: {taxa['inicio']:.2f} a "
                f"{taxa['fim']:.2f} minutos"
            )
            print(f"Taxa: {taxa['taxa_cm_min']:.2f} cm/min")

        print("\n--- ANÁLISE DOS LIMITES ---")

        print(
            "Cruzamento de atenção:",
            resultado["cruzamento_atencao"],
            "minutos"
        )

        print(
            "Cruzamento de alerta:",
            resultado["cruzamento_alerta"],
            "minutos"
        )

        print("\n--- INTEGRAIS ---")

        print(
            "Variação líquida:",
            resultado["variacao_total"],
            "cm"
        )

        print(
            "Exposição acima do alerta:",
            resultado["exposicao"],
            "cm.min"
        )

        print("\n--- CLASSIFICAÇÃO DE RISCO ---")

        print("Situação atual:", resultado["classificacao_final"])

        print(
            "Maior risco registrado no histórico:",
            resultado["classificacao_historica"]
        )

        opcao_grafico = input(
            "\nDeseja visualizar os gráficos? (s/n): "
        ).strip().lower()

        if opcao_grafico == "s":
            gerar_graficos(medicoes)

    except (ValueError, KeyError, TypeError) as erro:
        print(f"\nNão foi possível realizar a análise: {erro}")


def identificar_falhas_sensores(pontos):
    print("\n--- Identificação de possíveis falhas de sensor ---")

    if not pontos:
        print("Nenhum ponto monitorado foi cadastrado.")
        return

    falha_encontrada = False

    for ponto in pontos:
        medicao_anterior = None
        medicoes_ordenadas = ordenar_medicoes_por_data(ponto["medicoes"])

        if medicoes_ordenadas is None:
            falha_encontrada = True
            print(f"\nPonto: {ponto['nome']}")
            print("Dados inválidos nas medições. A análise não pôde ser realizada.")
            continue

        for medicao in medicoes_ordenadas:
            motivos = identificar_motivos_falha(medicao, medicao_anterior)

            if motivos:
                falha_encontrada = True
                print(f"\nPonto: {ponto['nome']}")
                print(f"Data e hora: {medicao['data_hora']}")
                print(f"Nível: {medicao['nivel_cm']:.2f} cm")
                print("Motivos:")

                for motivo in motivos:
                    print(f"- {motivo}")

            medicao_anterior = medicao

    if not falha_encontrada:
        print("Nenhuma possível falha de sensor foi identificada.")


def obter_opcao():
    while True:
        try:
            opcao = int(input("\nDigite a opção desejada: "))

            if 0 <= opcao <= 6:
                return opcao

            print("Opção inválida. Digite um número de 0 a 6.")
        except ValueError:
            print("Entrada inválida. Digite apenas números.")


def executar_sistema(pontos):
    while True:
        exibir_menu()
        opcao = obter_opcao()

        match opcao:
            case 1:
                cadastrar_ponto(pontos)
            case 2:
                registrar_medicao(pontos)
            case 3:
                consultar_pontos_e_medicoes(pontos)
            case 4:
                analisar_situacao_ponto(pontos)
            case 5:
                identificar_falhas_sensores(pontos)
            case 6:
                analisar_problem_solving(pontos)
            case 0:
                print("\nEncerrando o sistema PrevIA Hydro. Até logo!")
                break


if __name__ == "__main__":
    dados_carregados = carregar_dados()

    if dados_carregados is not None:
        pontos_monitorados = dados_carregados
        executar_sistema(pontos_monitorados)


print("Pasta de execução:", os.getcwd())
print("Arquivos encontrados:", os.listdir())