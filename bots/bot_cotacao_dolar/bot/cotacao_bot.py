from datetime import datetime
from typing import Optional

from playwright.sync_api import Page

from .config import Config
from .logger import get_logger
from .pages.google_page import GoogleCotacaoPage


class ResultadoCotacao:
    def __init__(
        self,
        valor: Optional[str],
        variacao: Optional[str],
        timestamp: str,
    ):
        self.valor = valor
        self.variacao = variacao
        self.timestamp = timestamp
        self.moeda_origem = "USD"
        self.moeda_destino = "BRL"
        self.sucesso = valor is not None

    def __repr__(self) -> str:
        return (
            f"ResultadoCotacao(valor={self.valor!r}, "
            f"variacao={self.variacao!r}, "
            f"sucesso={self.sucesso})"
        )


class CotacaoBot:
    def __init__(self, config: Config, page: Page):
        self.config = config
        self.page = page
        self.logger = get_logger(config.log_dir)
        self._google_page = GoogleCotacaoPage(page, config.log_dir)

    def executar(self) -> ResultadoCotacao:
        self.logger.info("=" * 60)
        self.logger.info("  INICIANDO AUTOMAÇÃO — BOT COTAÇÃO DÓLAR")
        self.logger.info("=" * 60)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            self._step_navegar()
            self._step_pesquisar()
            valor, variacao = self._step_capturar()
            resultado = ResultadoCotacao(valor, variacao, timestamp)
            self._exibir_resumo(resultado)
            return resultado

        except Exception as erro:
            self.logger.error(f"Erro inesperado durante a automação: {erro}")
            raise

    def _step_navegar(self):
        self.logger.info("[PASSO 1/3] Abrindo site de pesquisa")
        self._google_page.navegar()

    def _step_pesquisar(self):
        self.logger.info(f"[PASSO 2/3] Pesquisando cotação: '{self.config.search_query}'")
        self._google_page.pesquisar(self.config.search_query)

    def _step_capturar(self) -> tuple[Optional[str], Optional[str]]:
        self.logger.info("[PASSO 3/3] Capturando dados da cotação")
        valor = self._google_page.capturar_valor()
        variacao = self._google_page.capturar_variacao()
        return valor, variacao

    def _exibir_resumo(self, resultado: ResultadoCotacao):
        self.logger.info("-" * 60)
        self.logger.info("  RESULTADO FINAL DA COTAÇÃO")
        self.logger.info("-" * 60)
        if resultado.valor:
            self.logger.info(f"  Dólar (USD → BRL): R$ {resultado.valor}")
        else:
            self.logger.warning("  Valor do dólar: não capturado")
        if resultado.variacao:
            self.logger.info(f"  Variação (vs. dia anterior): {resultado.variacao}")
        else:
            self.logger.warning("  Variação: não capturada")
        self.logger.info(f"  Horário da consulta: {resultado.timestamp}")
        self.logger.info(f"  Status: {'SUCESSO' if resultado.sucesso else 'FALHA'}")
        self.logger.info("=" * 60)
