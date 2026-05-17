# Bot Verificação CNPJ

Automação RPA em Python para consulta de CNPJs via API pública da Receita Federal, com interface gráfica para entrada dos dados e exportação dos resultados em `.txt`.

---

## O Que a Automação Faz

1. Abre uma janela para o usuário informar os CNPJs (digitando ou carregando um arquivo)
2. Valida cada CNPJ pelo dígito verificador antes de consultar
3. Consulta a API da Receita Federal (ReceitaWS com fallback para BrasilAPI)
4. Exibe o resumo no terminal
5. Salva o resultado completo em `resultados/resultado_cnpj_YYYYMMDD_HHMMSS.txt`

Sem navegador. Sem CAPTCHA. Sem interação manual.

---

## Pré-requisitos

- Python 3.10+
- pip
- Conexão com a internet

---

## Instalação

```bash
# 1. Clone ou baixe o repositório
# 2. Acesse a pasta do bot
cd bots/bot_verifica_cnpj

# 3. Instale as dependências
python -m pip install -r requirements.txt
```

---

## Como Executar

```bash
python main.py
```

Ou pelo **VS Code**: selecione **"Bot Verifica CNPJ"** no dropdown de debug e pressione `F5`.

---

## Como Usar

### Digitando CNPJs manualmente

1. Informe um CNPJ por linha na área de texto (com ou sem formatação)
2. Clique em **Executar Consulta**

```
33.000.167/0001-01
47.960.950/0001-21
53113791000122
```

### Carregando de arquivo

Clique em **Carregar arquivo** — formatos suportados:

| Formato | Descrição |
|---|---|
| `.txt` | Um CNPJ por linha |
| `.xlsx` | CNPJs na primeira coluna da planilha |
| `.csv` | Um CNPJ por linha |

> CNPJs inválidos são automaticamente ignorados antes da consulta.

---

## Resultado

Os dados são salvos em `resultados/resultado_cnpj_YYYYMMDD_HHMMSS.txt`:

```
BOT VERIFICAÇÃO CNPJ — 17/05/2026 às 00:06:41
================================================================================

[1/3] CNPJ: 33.000.167/0001-01
--------------------------------------------------------------------------------
  CNPJ                               : 33000167000101
  Razão Social                       : PETROLEO BRASILEIRO S A PETROBRAS
  Situação Cadastral                 : ATIVA
  Data de Abertura                   : 28/09/1953
  CNAE                               : 06.10-8-00
  Descrição CNAE                     : Extração de petróleo e gás natural
  Natureza Jurídica                  : 204-6
  Descrição Natureza Jurídica        : Sociedade Anônima Aberta
  Logradouro                         : AV REPUBLICA DO CHILE
  Número                             : 65
  Município                          : RIO DE JANEIRO
  UF                                 : RJ
  CEP                                : 20031-912
  Sócios                             :
    - FULANO DE TAL (Diretor)
  Status: SUCESSO

================================================================================
TOTAL: 3/3 consulta(s) com sucesso
```

---

## Estrutura do Projeto

```
bot_verifica_cnpj/
├── main.py                  # Ponto de entrada
├── requirements.txt         # Dependências Python
├── bot/
│   ├── config.py            # Configurações (diretórios, delay entre consultas)
│   ├── logger.py            # Logger centralizado (console + arquivo)
│   ├── cnpj_api.py          # Cliente das APIs (ReceitaWS + BrasilAPI)
│   ├── cnpj_bot.py          # Orquestrador: consulta, salva e exibe resumo
│   └── ui/
│       └── input_window.py  # Interface gráfica (tkinter)
├── logs/
│   └── log_cnpj.txt         # Log acumulativo de todas as execuções
└── resultados/              # Arquivos gerados (ignorados pelo git)
```

---

## APIs Utilizadas

| API | URL | Autenticação | Limite |
|---|---|---|---|
| ReceitaWS | `receitaws.com.br` | Não | ~3 req/min gratuito |
| BrasilAPI | `brasilapi.com.br` | Não | Uso justo |

A consulta tenta primeiro a **ReceitaWS**. Em caso de falha, usa a **BrasilAPI** automaticamente.

---

## Configurações (`bot/config.py`)

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `log_dir` | `logs` | Pasta do arquivo de log |
| `output_dir` | `resultados` | Pasta dos arquivos de resultado |
| `delay_entre_consultas` | `1.5` | Segundos de espera entre cada CNPJ |
