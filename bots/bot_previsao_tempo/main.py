import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from bot.config import Config
from bot.logger import get_logger
from bot.previsao_bot import PrevisaoBot


def main():
    config = Config()
    logger = get_logger(config.log_dir)

    logger.info("Carregando configurações da automação")
    logger.info(f"  Cidade           : {config.cidade}")
    logger.info(f"  Contato WhatsApp : {config.contato_whatsapp or '(não configurado)'}")

    if not config.validar():
        logger.error("CONTATO_WHATSAPP não está configurado no arquivo .env")
        sys.exit(1)

    try:
        bot = PrevisaoBot(config)
        resultado = bot.executar()

        if resultado.sucesso:
            logger.info("Automação finalizada com SUCESSO")
            sys.exit(0)
        else:
            logger.error("Automação finalizada com FALHA")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("Automação interrompida pelo usuário")
        sys.exit(130)
    except Exception as erro:
        logger.error(f"Erro fatal: {erro}")
        sys.exit(1)


if __name__ == "__main__":
    main()
