import sys

from bot.config import Config
from bot.cnpj_bot import CnpjBot
from bot.logger import get_logger
from bot.ui.input_window import InputWindow


def main():
    config = Config()
    logger = get_logger(config.log_dir)

    logger.info("Abrindo tela de entrada de CNPJs")
    janela = InputWindow()
    cnpjs = janela.obter_cnpjs()

    if not cnpjs:
        logger.warning("Nenhum CNPJ informado. Encerrando.")
        sys.exit(0)

    logger.info(f"Carregando configurações da automação")
    logger.info(f"  CNPJs      : {len(cnpjs)} para consulta")
    logger.info(f"  Logs       : ./{config.log_dir}/")
    logger.info(f"  Resultados : ./{config.output_dir}/")

    try:
        bot = CnpjBot(config)
        resultados = bot.executar(cnpjs)
        sucessos = sum(1 for r in resultados if r.sucesso)
        logger.info(f"Consulta finalizada — {sucessos}/{len(resultados)} com SUCESSO")
        sys.exit(0 if sucessos > 0 else 1)

    except KeyboardInterrupt:
        logger.warning("Automação interrompida pelo usuário")
        sys.exit(130)
    except Exception as erro:
        logger.error(f"Erro fatal: {erro}")
        sys.exit(1)


if __name__ == "__main__":
    main()
