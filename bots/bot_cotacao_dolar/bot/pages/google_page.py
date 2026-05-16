import re
from typing import Optional

from playwright.sync_api import Page

from ..logger import get_logger


class GoogleCotacaoPage:
    """Page Object para captura de cotação do dólar via Google."""

    URL = "https://www.google.com.br"

    # Seletores para o valor principal da cotação (USD → BRL)
    _SELETORES_VALOR = [
        "span.DFlfde.SwHCTb",
        "span[data-value]",
        "div[jsname='UXTHHb'] span",
        "div.BNeawe.iBp4i.AP7Wnd",
    ]

    # Seletores para a variação/diferença em relação ao dia anterior
    _SELETORES_VARIACAO = [
        "span.XcVN5d.Pj0Kbb",
        "span.XcVN5d",
        "div.knHeGc span",
        "span.WlRRw",
        "div.fw-bold",
        "span[jsname='vWLAgc']",
        "div.IsqQVc",
        "div.g-blk span.XcVN5d",
    ]

    # Seletores para aceitar termos de consentimento do Google
    _SELETORES_CONSENTIMENTO = [
        "button#L2AGLb",
        "button:has-text('Aceitar tudo')",
        "button:has-text('Aceitar')",
        "form:has(button) button:first-child",
    ]

    def __init__(self, page: Page, log_dir: str = "logs"):
        self.page = page
        self.logger = get_logger(log_dir)

    def navegar(self):
        self.logger.info(f"Acessando URL: {self.URL}")
        self.page.goto(self.URL, wait_until="domcontentloaded")
        self._tratar_consentimento()

    def pesquisar(self, query: str):
        self.logger.info(f"Localizando campo de pesquisa")
        campo = self.page.locator("textarea[name='q'], input[name='q']").first
        campo.click()
        self.logger.info(f"Digitando termo de pesquisa: '{query}'")
        campo.fill(query)
        self.logger.info("Submetendo pesquisa")
        self.page.keyboard.press("Enter")
        self.page.wait_for_load_state("domcontentloaded")
        self.logger.info("Página de resultados carregada")

    def capturar_valor(self) -> Optional[str]:
        self.logger.info("Capturando valor atual do dólar (USD → BRL)")
        for seletor in self._SELETORES_VALOR:
            resultado = self._tentar_capturar(seletor)
            if resultado:
                return resultado
        self.logger.warning("Não foi possível capturar o valor do dólar com os seletores disponíveis")
        return None

    def capturar_variacao(self) -> Optional[str]:
        self.logger.info("Capturando variação em relação ao dia anterior")
        for seletor in self._SELETORES_VARIACAO:
            resultado = self._tentar_capturar(seletor)
            if resultado:
                return resultado
        resultado = self._capturar_variacao_por_texto()
        if resultado:
            return resultado
        self.logger.warning("Não foi possível capturar a variação")
        return None

    def _capturar_variacao_por_texto(self) -> Optional[str]:
        """Fallback: varre spans da página procurando padrão de variação (+/-X,XX%)."""
        try:
            padrao = re.compile(r"[+\-−]\s*\d+[,\.]\d+.*%")
            for span in self.page.locator("span").all():
                try:
                    texto = span.text_content(timeout=500)
                    if texto and padrao.search(texto.strip()):
                        texto = texto.strip()
                        self.logger.info(f"Variação encontrada por padrão de texto: {texto}")
                        return texto
                except Exception:
                    continue
        except Exception:
            pass
        return None

    def _tentar_capturar(self, seletor: str) -> Optional[str]:
        try:
            elemento = self.page.locator(seletor).first
            elemento.wait_for(state="visible", timeout=3000)
            texto = elemento.text_content()
            if texto and texto.strip():
                self.logger.info(f"Dado encontrado via seletor '{seletor}': {texto.strip()}")
                return texto.strip()
        except Exception:
            pass
        return None

    def _tratar_consentimento(self):
        for seletor in self._SELETORES_CONSENTIMENTO:
            try:
                botao = self.page.locator(seletor).first
                if botao.is_visible(timeout=2000):
                    self.logger.info("Aceitando termos de consentimento do Google")
                    botao.click()
                    self.page.wait_for_load_state("domcontentloaded")
                    return
            except Exception:
                continue
