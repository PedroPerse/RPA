from playwright.sync_api import sync_playwright, Page

from .config import Config
from .logger import get_logger


class BrowserManager:
    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger(config.log_dir)
        self._playwright = None
        self._browser = None
        self._context = None
        self._page: Page | None = None

    def __enter__(self) -> Page:
        return self.iniciar()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finalizar()

    def iniciar(self) -> Page:
        self.logger.info("Iniciando Playwright")
        self._playwright = sync_playwright().start()

        self.logger.info(f"Abrindo navegador ({self.config.browser_display_name()})")
        launcher = getattr(self._playwright, self.config.browser_type)
        self._browser = launcher.launch(
            headless=self.config.headless,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"],
        )

        self.logger.info("Criando nova aba do navegador")
        self._context = self._browser.new_context(
            locale="pt-BR",
            viewport={"width": 1280, "height": 800},
        )
        self._context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        self._page = self._context.new_page()
        self._page.set_default_timeout(self.config.timeout)

        self.logger.info("Navegador pronto para uso")
        return self._page

    def finalizar(self):
        self.logger.info("Encerrando navegador")
        if self._page:
            self._page.close()
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
        self.logger.info("Navegador encerrado com sucesso")
