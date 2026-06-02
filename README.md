# RPA — Repositório de Automações

Coleção de bots de automação RPA desenvolvidos em Python, prontos para uso e de código aberto.

Cada bot é um projeto independente com seu próprio repositório, instalação e documentação.

---

## Bots Disponíveis

| Bot | Descrição | Repositório |
|---|---|---|
| **Bot Cotação Dólar** | Captura a cotação do dólar (USD → BRL) via Google usando Playwright | [bot-cotacao-dollar](https://github.com/PedroPerse/bot-cotacao-dollar) |
| **Bot Verificação CNPJ** | Consulta dados de CNPJs via API da Receita Federal (sem CAPTCHA) | [bot-verifica-cnpj](https://github.com/PedroPerse/bot-verifica-cnpj) |
| **Bot Download Faturas** | Baixa faturas em PDF do e-mail (Gmail/Outlook) filtrando por vencimento | [download-de-faturas-email](https://github.com/PedroPerse/download-de-faturas-email) |
| **Bot Preenchimento Formulário** | Preenche formulários web automaticamente a partir de uma planilha Excel | [bot-preenchimento-formulario](https://github.com/PedroPerse/bot-preenchimento-formulario) |
| **Bot Previsão do Tempo** | Busca a previsão do dia (mín/máx + detalhes por hora) e envia via WhatsApp Web | [bot-previsao-tempo](https://github.com/PedroPerse/bot-previsao-tempo) |

---

## Como Usar

Cada bot pode ser clonado e usado individualmente — acesse o repositório do bot desejado e siga as instruções do README.

**Exemplo — clonar apenas o Bot Cotação Dólar:**
```bash
git clone https://github.com/PedroPerse/bot-cotacao-dollar.git
cd bot-cotacao-dollar
pip install -r requirements.txt
python main.py
```

**Para clonar este repositório completo com todos os bots:**
```bash
git clone --recurse-submodules https://github.com/PedroPerse/RPA.git
```

---

## Tecnologias

- **Python 3.10+**
- **Playwright** — automação de navegador
- **Requests** — consumo de APIs REST
- **Tkinter** — interfaces gráficas
- **openpyxl** — leitura de planilhas Excel
- **imap-tools** — acesso a e-mails via IMAP
- **pdfplumber** — extração de texto de PDFs

---

## Contribuindo

Novos bots serão adicionados ao longo do tempo. Sinta-se à vontade para abrir uma issue ou pull request com sugestões.
