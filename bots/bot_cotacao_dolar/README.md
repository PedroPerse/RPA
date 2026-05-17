# Bot Cotação Dólar

Automação RPA em Python com Playwright para capturar a cotação do dólar (USD → BRL) via Google.

---

## Estrutura do Projeto

```
bot-cotacao-dolar/
├── main.py                    # Ponto de entrada da automação
├── requirements.txt           # Dependências Python
├── bot/
│   ├── config.py              # Configurações (navegador, URL, timeout)
│   ├── logger.py              # Logger centralizado (console + arquivo)
│   ├── browser.py             # Gerenciador do ciclo de vida do navegador
│   ├── cotacao_bot.py         # Orquestrador principal da automação
│   └── pages/
│       └── google_page.py     # Page Object do Google (busca + captura)
└── logs/
    └── log_cotacao.txt        # Log único acumulativo de todas as execuções
```

---

## Pré-requisitos

- Python 3.10+
- pip

---

## Instalação

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

---

## Como Executar

```bash
python main.py
```

---

## O Que a Automação Faz

1. Carrega as configurações e inicia o logger
2. Abre o navegador Chromium
3. Acessa o Google
4. Aceita os termos de consentimento (se exibido)
5. Pesquisa `cotação dólar hoje`
6. Captura o valor atual (USD → BRL)
7. Captura a variação em relação ao dia anterior
8. Exibe e registra o resultado no log
9. Fecha o navegador

---

## Logs

Cada execução grava no arquivo `logs/log_cotacao.txt` no formato:

```
[2026-05-13 20:33:28] [INFO    ] Iniciando Playwright
[2026-05-13 20:33:32] [INFO    ] Abrindo navegador (Chromium (Chrome))
[2026-05-13 20:33:35] [INFO    ] Aceitando termos de consentimento do Google
[2026-05-13 20:33:36] [INFO    ] Página de resultados carregada
[2026-05-13 20:34:00] [INFO    ] Dólar (USD → BRL): R$ 5,73
[2026-05-13 20:34:00] [INFO    ] Variação (vs. dia anterior): +0,05 (+0,88%)
```

---

## Configurações (`bot/config.py`)

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `browser_type` | `chromium` | Navegador (`chromium`, `firefox`, `webkit`) |
| `headless` | `False` | `True` roda sem abrir janela; `False` abre o navegador visível |
| `search_query` | `cotação dólar hoje` | Termo de pesquisa |
| `timeout` | `30000` | Timeout em ms para elementos da página |
| `log_dir` | `logs` | Pasta do arquivo de log |
