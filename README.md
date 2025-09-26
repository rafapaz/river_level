# Sistema de Previsão de Nível de Rio

Este sistema utiliza Machine Learning para prever o nível de um rio com base em dados históricos.

## Arquivos

- `train_script.py` - Script para treinar o modelo de ML
- `predict_script.py` - Script para fazer previsões usando o modelo treinado
- `river_scraper.py` - Script para coletar dados de níveis de rios
- `requirements_file.txt` - Dependências Python necessárias
- `dados_nivel_rios_itacoatiara.json` - Dados históricos de nível do rio

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements_file.txt
```

## Coleta de Dados

### Script de Coleta (`river_scraper.py`)

Este script permite coletar dados históricos de níveis de rios a partir do site ProAmanaus.

#### Uso

```bash
python river_scraper.py <nome_do_rio> [--ano-inicio ANO] [--ano-fim ANO]
```

**Parâmetros obrigatórios:**
- `nome_do_rio`: Nome do rio para extrair os dados (ex: Itacoatiara, Manaus)

**Parâmetros opcionais:**
- `--ano-inicio`: Ano inicial para coleta (padrão: 2005)
- `--ano-fim`: Ano final para coleta (padrão: 2025)

**Exemplos:**
```bash
python river_scraper.py Itacoatiara
python river_scraper.py Manaus --ano-inicio 2020 --ano-fim 2023
```

#### Funcionamento

O script realiza as seguintes operações:
1. Faz requisições POST para o site ProAmanaus para cada mês do período especificado
2. Extrai os dados do rio especificado do HTML retornado
3. Organiza os dados em formato JSON com ano, mês e valores diários
4. Salva os dados em um arquivo JSON com o nome `dados_nivel_rio_[nome_do_rio].json`

#### Saída

O arquivo de saída segue o mesmo formato JSON usado pelo sistema de previsão:
```json
[
  {
    "ano": 2020,
    "mes": 1,
    "data": [1.5, 1.6, 1.7, ...]
  },
  ...
]
```

## Uso

### 1. Treinamento do Modelo

Execute o script de treinamento:
```bash
python train_script.py <arquivo_dados.json>
```

**Parâmetros obrigatórios:**
- `<arquivo_dados.json>`: Caminho para o arquivo JSON contendo os dados históricos de nível do rio

**Exemplo:**
```bash
python train_script.py dados_nivel_rios_itacoatiara.json
```

Este script irá:
- Carregar os dados do arquivo fornecido
- Processar e preparar os dados para ML
- Treinar um modelo Random Forest
- Avaliar a performance do modelo
- Salvar o modelo treinado como `modelo_nivel_rio.pkl`
- Gerar gráficos de avaliação (`model_evaluation.png`)

### 2. Fazendo Previsões

Use o script de previsão de duas formas:
```bash
python predict_script.py <ano> <mes> <dia>    # Prevê nível para um dia específico
python predict_script.py <ano> <mes>          # Prevê níveis para todos os dias do mês
```

**Exemplos:**
```bash
python predict_script.py 2025 8 15     # Prevê nível para 15 de agosto de 2025
python predict_script.py 2024 12 31    # Prevê nível para 31 de dezembro de 2024
python predict_script.py 2025 8        # Prevê níveis para todos os dias de agosto de 2025
python predict_script.py 2023 6        # Prevê níveis para todos os dias de junho de 2023
```

**Comportamento para previsão mensal:**
- Se o mês solicitado for o mês atual, as previsões começam do dia atual até o final do mês
- Se for outro mês, as previsões são feitas do dia 1 até o último dia do mês

**Opções disponíveis:**
- `--model, -m`: Especifica caminho do modelo (padrão: modelo_nivel_rio.pkl)
- `--verbose, -v`: Mostra informações detalhadas
- `--help, -h`: Exibe ajuda

**Exemplo com opções:**
```bash
python predict_script.py 2025 8 15 --verbose
python predict_script.py 2025 8 -m meu_modelo.pkl
```

## Funcionalidades

### Script de Treinamento (`train_script.py`)
- Processamento inteligente de datas e sazonalidade
- Validação cruzada para avaliação do modelo
- Métricas detalhadas (MAE, RMSE, R²)
- Visualizações da performance
- Features engineering com componentes sazonais

### Script de Previsão (`predict_script.py`)
- Validação de datas
- Previsão para um dia específico ou para um mês inteiro
- Interpretação do nível previsto
- Informações contextuais (estação do ano, dia da semana)
- Interface amigável com emojis e formatação
- Modo verbose para debugging

### Script de Coleta de Dados (`river_scraper.py`)
- Coleta de dados históricos de níveis de rios do site ProAmanaus
- Suporte para diferentes rios (Itacoatiara, Manaus, etc.)
- Personalização do período de coleta (ano inicial e final)
- Tratamento de erros e tentativas de reconexão
- Exportação dos dados em formato JSON compatível com o sistema de previsão

## Interpretação dos Resultados

O sistema classifica os níveis em:
- **Muito Baixo** (< 2m): ⚠️
- **Baixo** (2-5m): 📉
- **Normal** (5-8m): ✅
- **Alto** (8-12m): 📈
- **Muito Alto** (> 12m): 🚨

## Características Técnicas

- **Algoritmo**: Random Forest Regressor
- **Features**: Ano, mês, dia, componentes sazonais
- **Validação**: Split 80/20 treino/teste
- **Métricas**: MAE, RMSE, R²
- **Sazonalidade**: Componentes seno/cosseno para capturar ciclos anuais e mensais

## Limitações

- Previsões para anos muito distantes podem ter menor precisão
- O modelo assume continuidade dos padrões históricos
- Eventos extremos não previstos pelos dados históricos podem não ser bem capturados

## Formato dos Dados

Os dados devem estar no formato JSON:
```json
[
  {
    "ano": 2020,
    "mes": 1,
    "data": [1.5, 1.6, 1.7, ...]
  },
  ...
]
```

Onde `data` é um array com o nível do rio para cada dia do mês (em metros).