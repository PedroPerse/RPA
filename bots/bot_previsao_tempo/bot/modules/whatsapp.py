import logging
from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page, sync_playwright


# Seletores alternativos para detectar que o WhatsApp carregou após login
_SELETORES_LOGADO = [
    '[data-testid="chat-list-search"]',
    '[data-testid="chat-list"]',
    '#pane-side',
    '[aria-label="Lista de conversas"]',
    '[aria-label="Conversation list"]',
]


def _aguardar_app_carregar(page: Page, timeout_ms: int) -> bool:
    """Tenta vários seletores para confirmar que o app carregou."""
    seletor_combinado = ", ".join(_SELETORES_LOGADO)
    try:
        page.wait_for_selector(seletor_combinado, timeout=timeout_ms)
        return True
    except Exception:
        return False


def _esta_logado(page: Page) -> bool:
    return _aguardar_app_carregar(page, timeout_ms=12000)


def _aguardar_qr_login(page: Page, logger: logging.Logger, timeout_ms: int = 180000) -> None:
    logger.warning("=" * 60)
    logger.warning("  AÇÃO NECESSÁRIA: Escaneie o QR Code no WhatsApp")
    logger.warning("  Abra o WhatsApp no celular → Aparelhos conectados → Conectar")
    logger.warning(f"  Aguardando login (timeout: {timeout_ms // 1000}s)...")
    logger.warning("=" * 60)
    if not _aguardar_app_carregar(page, timeout_ms):
        raise TimeoutError("Login não detectado dentro do tempo limite. Tente novamente.")
    logger.info("Login realizado com sucesso!")


def _buscar_e_abrir_contato(page: Page, contato: str, logger: logging.Logger) -> None:
    logger.info(f"Pesquisando contato: '{contato}'")

    seletor_busca = ", ".join(_SELETORES_LOGADO[:2])
    search_box = page.locator('[data-testid="chat-list-search"]').or_(
        page.locator('[aria-label="Pesquisar ou começar uma nova conversa"]')
    ).first
    search_box.wait_for(state="visible", timeout=15000)
    search_box.click()
    search_box.fill(contato)

    # Aguarda resultados aparecerem
    page.wait_for_timeout(2500)

    # Tenta clicar pelo título exato primeiro, depois no primeiro resultado
    try:
        exact = page.locator(f'span[title="{contato}"]').first
        exact.wait_for(state="visible", timeout=6000)
        exact.click()
        logger.info(f"Contato '{contato}' encontrado e selecionado")
    except Exception:
        logger.warning(f"Seletor exato não encontrou '{contato}' — clicando no primeiro resultado")
        first_result = page.locator('[data-testid="cell-frame-container"]').first
        first_result.wait_for(state="visible", timeout=6000)
        first_result.click()

    page.wait_for_timeout(1500)


def _digitar_e_enviar(page: Page, mensagem: str, logger: logging.Logger) -> None:
    logger.info("Digitando mensagem no campo de texto")

    message_box = page.locator('[data-testid="conversation-compose-box-input"]')
    message_box.wait_for(state="visible", timeout=15000)
    message_box.click()

    # Digita linha por linha, usando Shift+Enter para quebras de linha
    linhas = mensagem.split("\n")
    for i, linha in enumerate(linhas):
        page.keyboard.type(linha)
        if i < len(linhas) - 1:
            page.keyboard.press("Shift+Enter")

    page.keyboard.press("Enter")
    page.wait_for_timeout(2000)
    logger.info("Mensagem enviada!")


def _tirar_screenshot(page: Page, log_dir: str, logger: logging.Logger) -> None:
    try:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = Path(log_dir) / f"whatsapp_enviado_{ts}.png"
        page.screenshot(path=str(screenshot_path))
        logger.info(f"Screenshot salvo: {screenshot_path}")
    except Exception as e:
        logger.warning(f"Não foi possível salvar o screenshot: {e}")


def enviar_mensagem(contato: str, mensagem: str, config, logger: logging.Logger) -> bool:
    # Perfil persistente salva IndexedDB + cookies — único jeito de manter sessão do WhatsApp Web
    profile_dir = str(Path(config.storage_dir) / "browser_profile")
    Path(profile_dir).mkdir(parents=True, exist_ok=True)

    logger.info(f"Perfil do navegador: {profile_dir}")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="pt-BR",
        )
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        page = context.new_page()
        page.set_default_timeout(config.timeout)

        try:
            logger.info("Abrindo WhatsApp Web")
            page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")

            if not _esta_logado(page):
                _aguardar_qr_login(page, logger)

            logger.info("WhatsApp Web autenticado e pronto")

            _buscar_e_abrir_contato(page, contato, logger)
            _digitar_e_enviar(page, mensagem, logger)
            _tirar_screenshot(page, config.log_dir, logger)
            return True

        except Exception as e:
            logger.error(f"Erro ao enviar mensagem no WhatsApp: {e}")
            try:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                Path(config.log_dir).mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(Path(config.log_dir) / f"erro_{ts}.png"))
            except Exception:
                pass
            return False

        finally:
            context.close()
