import re
from typing import Optional

from playwright.sync_api import Frame, Page

from ..logger import get_logger


class ResultadoCnpj:
    def __init__(self, cnpj: str, dados: dict, sucesso: bool, erro: Optional[str] = None):
        self.cnpj = cnpj
        self.dados = dados
        self.sucesso = sucesso
        self.erro = erro

    def __repr__(self) -> str:
        return f"ResultadoCnpj(cnpj={self.cnpj!r}, sucesso={self.sucesso})"


class ReceitaFederalPage:
    URL_FORMULARIO = "https://servicos.receita.fazenda.gov.br/Servicos/cnpjreva/Cnpjreva_Solicitacao.asp"

    _SELETORES_CNPJ = [
        "input[name='cnpj']",
        "input#cnpj",
        "input[id='cnpj']",
        "input[maxlength='18']",
        "input[maxlength='14']",
        "input[type='text']:first-of-type",
    ]

    def __init__(self, page: Page, log_dir: str = "logs"):
        self.page = page
        self.logger = get_logger(log_dir)

    def navegar(self):
        self.logger.info("Acessando formulário de consulta CNPJ")
        self.page.goto(self.URL_FORMULARIO, wait_until="domcontentloaded")
        try:
            self.page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        self.logger.info("Formulário carregado")
        self._log_frames()

    def preencher_cnpj(self, cnpj: str) -> bool:
        cnpj_limpo = re.sub(r"\D", "", cnpj)
        self.logger.info(f"Preenchendo CNPJ: {self._formatar(cnpj_limpo)}")

        preenchido = self._tentar_preencher(self.page, cnpj_limpo)
        if not preenchido:
            for frame in self.page.frames:
                if frame == self.page.main_frame:
                    continue
                url = frame.url or ""
                if "hcaptcha" in url or "recaptcha" in url:
                    continue
                self.logger.info(f"Tentando iframe: {url}")
                if self._tentar_preencher(frame, cnpj_limpo):
                    preenchido = True
                    break

        if not preenchido:
            self.logger.error("Não foi possível localizar o campo de CNPJ na página")
            self._salvar_screenshot("erro_campo_cnpj")
            return False

        self._mostrar_dialogo_captcha(self._formatar(cnpj_limpo))
        return True

    def aguardar_resultado(self, timeout_captcha: int = 120000) -> bool:
        if self._na_pagina_resultado():
            self.logger.info("Resultado já carregado na página")
            return True
        self.logger.info(f"Aguardando página de resultado (timeout: {timeout_captcha // 1000}s)...")
        try:
            self.page.wait_for_url("**/Cnpjreva_Comprovante.asp**", timeout=timeout_captcha)
            self.page.wait_for_load_state("domcontentloaded")
            self.logger.info("Página de resultado carregada")
            return True
        except Exception:
            self.logger.warning("Timeout aguardando resultado")
            return False

    def capturar_dados(self) -> dict:
        self.logger.info("Capturando dados do CNPJ")
        dados = {}
        try:
            linhas = self.page.locator("tr").all()
            for linha in linhas:
                try:
                    celulas = linha.locator("td").all()
                    if len(celulas) >= 2:
                        chave = (celulas[0].text_content() or "").strip().rstrip(":").strip()
                        valor = (celulas[1].text_content() or "").strip()
                        if chave and valor and chave != valor:
                            dados[chave] = valor
                except Exception:
                    continue

            if not dados:
                dados = self._capturar_por_texto()

        except Exception as e:
            self.logger.error(f"Erro ao capturar dados: {e}")

        self.logger.info(f"{len(dados)} campo(s) capturado(s)")
        return dados

    def voltar_formulario(self):
        self.logger.info("Voltando ao formulário para próxima consulta")
        self.page.goto(self.URL_FORMULARIO, wait_until="domcontentloaded")
        try:
            self.page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass

    # ── helpers ──────────────────────────────────────────────────────────────

    def _mostrar_dialogo_captcha(self, cnpj_fmt: str):
        """Abre janela pedindo ao usuário que resolva o CAPTCHA. Só libera após validar."""
        import tkinter as tk

        self.logger.info("Aguardando usuário resolver o CAPTCHA")
        root = tk.Tk()
        root.title("Resolva o CAPTCHA")
        root.geometry("400x220")
        root.resizable(False, False)
        root.attributes("-topmost", True)
        root.configure(bg="#f0f0f0")

        tk.Label(
            root,
            text=f"CNPJ: {cnpj_fmt}",
            font=("Segoe UI", 12, "bold"),
            bg="#f0f0f0",
            fg="#333333",
        ).pack(pady=(18, 4))

        tk.Label(
            root,
            text="No navegador:\n  1. Marque  ☑  'Sou humano'\n  2. Clique em  CONSULTAR\n  3. Aguarde o resultado carregar",
            font=("Segoe UI", 10),
            bg="#f0f0f0",
            fg="#555555",
            justify="left",
        ).pack(padx=30)

        aviso_var = tk.StringVar(value="")
        tk.Label(
            root,
            textvariable=aviso_var,
            font=("Segoe UI", 9, "bold"),
            bg="#f0f0f0",
            fg="#c62828",
        ).pack(pady=(6, 0))

        def ao_clicar_pronto():
            if not self._na_pagina_resultado():
                aviso_var.set("⚠  Aguarde o resultado carregar no navegador primeiro.")
                return
            root.destroy()

        tk.Button(
            root,
            text="✓  Pronto",
            command=ao_clicar_pronto,
            font=("Segoe UI", 11, "bold"),
            bg="#2e7d32",
            fg="white",
            activebackground="#1b5e20",
            activeforeground="white",
            relief="flat",
            padx=24,
            pady=8,
            cursor="hand2",
        ).pack(pady=(8, 0))

        root.protocol("WM_DELETE_WINDOW", root.destroy)
        root.mainloop()
        self.logger.info("Usuário confirmou resolução do CAPTCHA — prosseguindo")

    def _na_pagina_resultado(self) -> bool:
        """Verifica se o navegador já está na página de resultado."""
        return "Cnpjreva_Comprovante.asp" in (self.page.url or "")

    def _clicar_consultar(self):
        """Tenta clicar no botão Consultar após preencher o CNPJ."""
        seletores = [
            "input[value='Consultar']",
            "input[value*='onsultar']",
            "button:has-text('Consultar')",
            "a:has-text('Consultar')",
            "input[type='submit']",
            "button[type='submit']",
        ]
        for seletor in seletores:
            try:
                btn = self.page.locator(seletor).first
                if btn.is_visible(timeout=2000):
                    btn.click()
                    self.logger.info("Botão Consultar clicado")
                    return
            except Exception:
                continue
        self.logger.info("Botão Consultar não localizado — aguardando ação manual do usuário")

    def _tentar_preencher(self, contexto, cnpj_limpo: str) -> bool:
        seletores = ["input#cnpj", "input[name='cnpj']", "input[maxlength='18']"]
        for seletor in seletores:
            try:
                campo = contexto.locator(seletor).first
                if not campo.is_visible(timeout=3000):
                    continue
                campo.scroll_into_view_if_needed()
                campo.click()
                campo.press("Control+a")
                campo.press("Delete")
                campo.press_sequentially(cnpj_limpo, delay=80)
                valor = campo.input_value()
                if valor:
                    self.logger.info(f"Campo preenchido via '{seletor}': {valor} — resolva o CAPTCHA e clique em Consultar")
                    return True
            except Exception as e:
                self.logger.info(f"Seletor '{seletor}' falhou: {e}")
                continue

        # Fallback: preenchimento via JavaScript
        try:
            self.logger.info("Tentando preencher via JavaScript")
            resultado = self.page.evaluate(f"""() => {{
                const inp = document.querySelector('input#cnpj') || document.querySelector('input[name="cnpj"]');
                if (!inp) return null;
                inp.focus();
                inp.value = '{cnpj_limpo}';
                inp.dispatchEvent(new Event('input', {{bubbles: true}}));
                inp.dispatchEvent(new Event('change', {{bubbles: true}}));
                return inp.value;
            }}""")
            if resultado:
                self.logger.info(f"Campo preenchido via JavaScript: {resultado} — resolva o CAPTCHA e clique em Consultar")
                return True
        except Exception as e:
            self.logger.warning(f"Fallback JavaScript falhou: {e}")

        return False

    def _capturar_por_texto(self) -> dict:
        dados = {}
        try:
            conteudo = self.page.locator("body").text_content() or ""
            for linha in conteudo.splitlines():
                linha = linha.strip()
                if ":" in linha:
                    partes = linha.split(":", 1)
                    chave = partes[0].strip()
                    valor = partes[1].strip()
                    if chave and valor and len(chave) < 60:
                        dados[chave] = valor
        except Exception:
            pass
        return dados

    def _log_frames(self):
        frames = self.page.frames
        self.logger.info(f"Frames detectados na página: {len(frames)}")
        for i, f in enumerate(frames):
            self.logger.info(f"  Frame[{i}]: {f.url}")

    def _log_inputs_pagina(self):
        try:
            inputs = self.page.evaluate("""() =>
                [...document.querySelectorAll('input')].map(i => ({
                    id: i.id, name: i.name, type: i.type,
                    maxlength: i.maxLength, placeholder: i.placeholder,
                    visible: i.offsetParent !== null
                }))
            """)
            self.logger.info(f"Inputs encontrados na página principal: {len(inputs)}")
            for inp in inputs:
                self.logger.info(f"  input → {inp}")
        except Exception as e:
            self.logger.warning(f"Não foi possível listar inputs: {e}")

    def _salvar_screenshot(self, nome: str):
        try:
            caminho = f"logs/{nome}.png"
            self.page.screenshot(path=caminho)
            self.logger.info(f"Screenshot salvo em: {caminho}")
        except Exception:
            pass

    @staticmethod
    def _formatar(cnpj: str) -> str:
        if len(cnpj) == 14:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        return cnpj
