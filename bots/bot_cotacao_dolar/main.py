import sys

from bot.browser import BrowserManager
from bot.config import Config
from bot.cotacao_bot import CotacaoBot
from bot.logger import get_logger


def main():
    config = Config()
    logger = get_logger(config.log_dir)

    logger.info("Carregando configurações da automação")
    logger.info(f"  Navegador  : {config.browser_display_name()}")
    logger.info(f"  Modo       : {'Silencioso (headless)' if config.headless else 'Visível'}")
    logger.info(f"  Pesquisa   : {config.search_query}")
    logger.info(f"  Logs       : ./{config.log_dir}/")

    try:
        with BrowserManager(config) as page:
            bot = CotacaoBot(config, page)
            resultado = bot.executar()

        if resultado.sucesso:
            logger.info("Automação finalizada com SUCESSO")
            sys.exit(0)
        else:
            logger.error("Automação finalizada com FALHA — cotação não capturada")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("Automação interrompida pelo usuário")
        sys.exit(130)
    except Exception as erro:
        logger.error(f"Erro fatal: {erro}")
        sys.exit(1)


if __name__ == "__main__":
    main()
