from datetime import datetime

from .config import Config
from .logger import get_logger
from .modules.weather import DadosTempo, buscar_previsao
from .modules.whatsapp import enviar_mensagem


class ResultadoPrevisao:
    def __init__(self, tempo: DadosTempo, mensagem_enviada: bool):
        self.tempo = tempo
        self.mensagem_enviada = mensagem_enviada
        self.sucesso = tempo.sucesso and mensagem_enviada
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __repr__(self) -> str:
        return (
            f"ResultadoPrevisao("
            f"tempo_ok={self.tempo.sucesso}, "
            f"enviado={self.mensagem_enviada}, "
            f"sucesso={self.sucesso})"
        )


class PrevisaoBot:
    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger(config.log_dir)

    def executar(self) -> ResultadoPrevisao:
        self.logger.info("=" * 60)
        self.logger.info("  INICIANDO AUTOMAÇÃO — BOT PREVISÃO DO TEMPO")
        self.logger.info("=" * 60)

        dados = self._step_buscar_previsao()
        mensagem = self._step_formatar_mensagem(dados)
        enviado = self._step_enviar_whatsapp(mensagem)

        resultado = ResultadoPrevisao(dados, enviado)
        self._exibir_resumo(resultado)
        return resultado

    def _step_buscar_previsao(self) -> DadosTempo:
        self.logger.info(f"[PASSO 1/3] Buscando previsão do tempo para '{self.config.cidade}'")
        dados = buscar_previsao(self.config.cidade)

        if dados.sucesso:
            self.logger.info(f"  Previsão capturada — Min: {dados.min_temp} | Max: {dados.max_temp}")
        else:
            self.logger.error(f"  Falha ao buscar previsão: {dados.erro}")

        return dados

    def _step_formatar_mensagem(self, dados: DadosTempo) -> str:
        self.logger.info("[PASSO 2/3] Formatando mensagem")

        if not dados.sucesso:
            return f"❌ Não foi possível obter a previsão para {self.config.cidade}.\nTente novamente mais tarde."

        linhas = [
            f"🌤 Previsão do tempo — {dados.cidade}",
            f"📅 {dados.data} ({dados.dia_semana})",
            "",
            f"🌡 Mínima: {dados.min_temp}  |  Máxima: {dados.max_temp}",
            "",
            "⏱ Por hora:",
        ]

        for h in dados.horas:
            linhas.append(str(h))

        linhas.append("")
        linhas.append("🤖 Bot Previsão")

        return "\n".join(linhas)

    def _step_enviar_whatsapp(self, mensagem: str) -> bool:
        self.logger.info(f"[PASSO 3/3] Enviando mensagem para '{self.config.contato_whatsapp}'")
        return enviar_mensagem(self.config.contato_whatsapp, mensagem, self.config, self.logger)

    def _exibir_resumo(self, resultado: ResultadoPrevisao) -> None:
        self.logger.info("-" * 60)
        self.logger.info("  RESULTADO FINAL")
        self.logger.info("-" * 60)
        self.logger.info(f"  Previsão capturada : {'SIM' if resultado.tempo.sucesso else 'NÃO'}")
        self.logger.info(f"  Mensagem enviada   : {'SIM' if resultado.mensagem_enviada else 'NÃO'}")
        self.logger.info(f"  Status geral       : {'SUCESSO ✓' if resultado.sucesso else 'FALHA ✗'}")
        self.logger.info(f"  Horário            : {resultado.timestamp}")
        self.logger.info("=" * 60)
