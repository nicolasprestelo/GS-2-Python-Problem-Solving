# prevIA Hydro
## Documentação técnica — Python e Problem Solving

**Projeto acadêmico | FIAP | 2026**

**Integrantes:**  
Murillo Serrano - 569296
Nicolas Prestelo - 570785
Jonathan Josué - 569810

---

# ENTREGA DE PYTHON

## 1. Apresentação do projeto

O prevIA Hydro é um protótipo acadêmico desenvolvido para monitorar níveis de água e identificar possíveis situações de atenção relacionadas a enchentes. A aplicação em Python permite cadastrar pontos de monitoramento, registrar medições, consultar históricos, classificar níveis e analisar possíveis inconsistências nos dados.

O sistema utiliza parâmetros ilustrativos para classificar os níveis de água. Portanto, não deve ser considerado uma ferramenta oficial de previsão ou alerta de enchentes.

## 2. Objetivos

- Desenvolver uma aplicação de terminal para gerenciar pontos de monitoramento.
- Registrar e consultar medições de nível da água.
- Armazenar os dados para que permaneçam disponíveis após o encerramento do programa.
- Classificar os níveis em Normal, Atenção e Alerta.
- Calcular a variação do nível entre medições.
- Identificar possíveis inconsistências nos registros.

## 3. Tecnologias e recursos utilizados

- **Python:** implementação da lógica, validações, processamento e cálculos.
- **JSON:** persistência dos pontos monitorados e respectivos históricos.
- **Matplotlib:** geração dos gráficos da análise matemática.
- **Datetime:** interpretação e comparação de datas e horários.

## 4. Organização dos arquivos

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Menu, fluxo principal, cadastro, medições, consultas e integração dos módulos. |
| `problem_solving.py` | Preparação do histórico e cálculos matemáticos. |
| `graficos.py` | Geração dos gráficos com Matplotlib. |
| `dados_prevIA_Hydro.json` | Armazenamento persistente dos pontos e medições. |

## 5. Funcionalidades do sistema

### 5.1 Cadastro de pontos monitorados

Permite cadastrar um ponto informando seu nome e sua localização. O sistema atribui um identificador ao ponto e mantém uma lista dos pontos cadastrados.

### 5.2 Registro de medições

Permite registrar o nível da água em centímetros para um ponto existente. Cada registro contém o valor medido e a data e o horário correspondentes.

O sistema valida os valores informados, considerando o intervalo de 0 a 500 cm. Também foi configurado um intervalo mínimo de cinco minutos entre registros manuais consecutivos no mesmo ponto. Esse controle impede novos registros antes do período definido, mas não agenda nem executa uma coleta automática.

### 5.3 Consulta de pontos e históricos

Apresenta os pontos cadastrados e suas medições em ordem cronológica, permitindo consultar a evolução dos níveis registrados.

### 5.4 Análise da situação de um ponto

Utiliza a medição mais recente para apresentar o nível atual, sua classificação e a taxa média de variação em relação à medição anterior, quando houver dados suficientes.

### 5.5 Identificação de possíveis inconsistências

O sistema verifica condições que podem indicar dados inválidos ou leituras atípicas, incluindo:

- Nível abaixo do mínimo definido;
- Nível acima do máximo definido;
- Dados inválidos na medição atual ou anterior;
- Variação absoluta superior a 100 cm entre medições consecutivas.

A variação superior a 100 cm é um critério simplificado do protótipo. Ela sinaliza uma possível inconsistência, mas não comprova defeito físico do sensor.

### 5.6 Análise matemática e gráficos

A opção de análise matemática utiliza o histórico do ponto selecionado e chama os módulos responsáveis pelos cálculos e pela geração dos gráficos. São apresentados os resultados das taxas, dos cruzamentos dos limites, das integrais e das classificações atual e histórica.

## 6. Classificação dos níveis

Foram definidos os seguintes parâmetros ilustrativos:

| Nível registrado | Classificação |
|---|---|
| Menor que 50 cm | Normal |
| De 50 cm até menos de 100 cm | Atenção |
| Igual ou superior a 100 cm | Alerta |

Os valores são parâmetros de demonstração adotados no protótipo. Não representam limites oficiais de segurança ou critérios de órgãos de monitoramento.

## 7. Persistência dos dados em JSON

Os dados são armazenados no arquivo `dados_prevIA_Hydro.json`. Cada ponto contém:

- `id`: identificador do ponto;
- `nome`: nome cadastrado;
- `localizacao`: localização informada;
- `medicoes`: lista de medições associadas.

Cada medição contém:

- `nivel_cm`: nível da água em centímetros;
- `data_hora`: data e horário do registro.

O programa carrega os dados ao iniciar e os salva após as operações que alteram o cadastro ou o histórico. A implementação também realiza validações da estrutura e utiliza gravação por arquivo temporário antes de substituir o arquivo principal, reduzindo o risco de perda de dados durante o salvamento.

## 8. Validações e testes realizados

Foram executados testes com diferentes cenários, incluindo:

- Histórico com níveis crescentes;
- Histórico com níveis decrescentes;
- Histórico sem cruzamento dos limites;
- Intervalos variáveis entre medições;
- Histórico com apenas uma medição;
- Nível negativo;
- Horários duplicados;
- Integração da análise matemática ao menu;
- Exibição dos gráficos;
- Carregamento dos dados após reiniciar o programa.

Os cenários descritos foram utilizados para verificar o comportamento das funções e a integração dos módulos. Os resultados finais devem ser conferidos na versão do código que será entregue.

## 9. Como executar

É necessário ter Python instalado e a biblioteca Matplotlib disponível no ambiente.

Com os arquivos do projeto organizados conforme a estrutura apresentada, execute no terminal:

```bash
python main.py
```

O menu será exibido no terminal e permitirá acessar as funcionalidades disponíveis.

## 10. Limitações da implementação

O sistema é um protótipo acadêmico. Os limites de classificação e os critérios de identificação de possíveis inconsistências são parâmetros simplificados, não validados para uso operacional.

O intervalo de cinco minutos controla o registro manual, mas não implementa agendamento automático de medições. A aplicação Python também funciona de maneira independente da interface web; não há, nesta versão, integração em tempo real entre Python e React.

---

