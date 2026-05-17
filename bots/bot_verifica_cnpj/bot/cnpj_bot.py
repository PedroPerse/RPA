import time
from datetime import datetime
from pathlib import Path

from .config import Config
from .cnpj_api import CnpjApiClient, ResultadoCnpj
from .logger import get_logger

_CAMPOS = [
    ("cnpj", "CNPJ"),
    ("razao_social", "Razão Social"),
    ("nome_fantasia", "Nome Fantasia"),
    ("situacao_cadastral", "Situação Cadastral"),
    ("descricao_situacao_cadastral", "Descrição Situação"),
    ("data_inicio_atividade", "Data de Abertura"),
    ("cnae_fiscal", "CNAE"),
    ("cnae_fiscal_descricao", "Descrição CNAE"),
    ("natureza_juridica", "Natureza Jurídica"),
    ("descricao_natureza_juridica", "Descrição Natureza Jurídica"),
    ("porte", "Porte"),
    ("descricao_porte", "Descrição Porte"),
    ("logradouro", "Logradouro"),
    ("numero", "Número"),
    ("complemento", "Complemento"),
    ("bairro", "Bairro"),
    ("municipio", "Município"),
    ("uf", "UF"),
    ("cep", "CEP"),
    ("telefone", "Telefone"),
    ("email", "E-mail"),
]


class CnpjBot:
    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger(config.log_dir)
        self._api = CnpjApiClient(config.log_dir)

    def executar(self, cnpjs: list[str]) -> list[ResultadoCnpj]:
        self.logger.info("=" * 60)
        self.logger.info("  INICIANDO CONSULTA — BOT VERIFICAÇÃO CNPJ")
        self.logger.info("=" * 60)

        resultados = []
        for i, cnpj in enumerate(cnpjs, start=1):
            self.logger.info(f"[{i}/{len(cnpjs)}] Consultando: {cnpj}")
            resultado = self._api.consultar(cnpj)
            resultados.append(resultado)
            if i < len(cnpjs):
                time.sleep(self.config.delay_entre_consultas)

        self._salvar_resultados(resultados)
        self._exibir_resumo(resultados)
        return resultados

    def _salvar_resultados(self, resultados: list[ResultadoCnpj]):
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho = Path(self.config.output_dir) / f"resultado_cnpj_{timestamp}.txt"

        with open(caminho, "w", encoding="utf-8") as f:
            f.write(f"BOT VERIFICAÇÃO CNPJ — {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

            for i, r in enumerate(resultados, start=1):
                cnpj_fmt = self._fmt(r.cnpj)
                f.write(f"[{i}/{len(resultados)}] CNPJ: {cnpj_fmt}\n")
                f.write("-" * 80 + "\n")

                if r.sucesso:
                    for chave, label in _CAMPOS:
                        valor = r.dados.get(chave, "")
                        if valor:
                            f.write(f"  {label:<35}: {valor}\n")
                    socios = r.dados.get("qsa", [])
                    if socios:
                        f.write(f"  {'Sócios':<35}:\n")
                        for s in socios:
                            f.write(f"    - {s.get('nome_socio', '')} ({s.get('qualificacao_socio', '')})\n")
                    f.write("  Status: SUCESSO\n")
                else:
                    f.write(f"  Status: FALHA — {r.erro}\n")

                f.write("\n")

            sucessos = sum(1 for r in resultados if r.sucesso)
            f.write("=" * 80 + "\n")
            f.write(f"TOTAL: {sucessos}/{len(resultados)} consulta(s) com sucesso\n")

        self.logger.info(f"Resultado salvo em: {caminho}")

    def _exibir_resumo(self, resultados: list[ResultadoCnpj]):
        self.logger.info("-" * 60)
        self.logger.info("  RESUMO FINAL")
        self.logger.info("-" * 60)
        for r in resultados:
            if r.sucesso:
                nome = r.dados.get("razao_social", "")
                sit = r.dados.get("descricao_situacao_cadastral", r.dados.get("situacao_cadastral", ""))
                self.logger.info(f"  {self._fmt(r.cnpj)} → {nome} [{sit}]")
            else:
                self.logger.info(f"  {self._fmt(r.cnpj)} → FALHA ({r.erro})")
        self.logger.info("=" * 60)

    @staticmethod
    def _fmt(cnpj: str) -> str:
        if len(cnpj) == 14:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        return cnpj
