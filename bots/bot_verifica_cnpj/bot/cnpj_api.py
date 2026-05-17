import re
from typing import Optional

import requests

from .logger import get_logger


class ResultadoCnpj:
    def __init__(self, cnpj: str, dados: dict, sucesso: bool, erro: Optional[str] = None):
        self.cnpj = cnpj
        self.dados = dados
        self.sucesso = sucesso
        self.erro = erro

    def __repr__(self) -> str:
        return f"ResultadoCnpj(cnpj={self.cnpj!r}, sucesso={self.sucesso})"


class CnpjApiClient:
    _URL_RECEITAWS  = "https://www.receitaws.com.br/v1/cnpj/{cnpj}"
    _URL_BRASILAPI  = "https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
    _HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    def __init__(self, log_dir: str = "logs"):
        self.logger = get_logger(log_dir)

    def consultar(self, cnpj: str) -> ResultadoCnpj:
        cnpj_limpo = re.sub(r"\D", "", cnpj)
        self.logger.info(f"Consultando via API: {self._fmt(cnpj_limpo)}")

        try:
            dados = self._receitaws(cnpj_limpo)
            self.logger.info(f"Dados obtidos via ReceitaWS — {len(dados)} campos")
            return ResultadoCnpj(cnpj_limpo, dados, sucesso=True)
        except Exception as e:
            self.logger.warning(f"ReceitaWS falhou: {e} — tentando BrasilAPI")

        try:
            dados = self._brasilapi(cnpj_limpo)
            self.logger.info(f"Dados obtidos via BrasilAPI — {len(dados)} campos")
            return ResultadoCnpj(cnpj_limpo, dados, sucesso=True)
        except Exception as e:
            self.logger.error(f"BrasilAPI também falhou: {e}")

        return ResultadoCnpj(cnpj_limpo, {}, sucesso=False, erro="Ambas as APIs falharam")

    # ── APIs ─────────────────────────────────────────────────────────────────

    def _receitaws(self, cnpj: str) -> dict:
        resp = requests.get(
            self._URL_RECEITAWS.format(cnpj=cnpj),
            headers=self._HEADERS,
            timeout=15,
        )
        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code}")
        data = resp.json()
        if data.get("status") == "ERROR":
            raise Exception(data.get("message", "Erro desconhecido"))
        return self._normalizar_receitaws(data)

    def _brasilapi(self, cnpj: str) -> dict:
        resp = requests.get(
            self._URL_BRASILAPI.format(cnpj=cnpj),
            headers=self._HEADERS,
            timeout=15,
        )
        if resp.status_code == 404:
            raise Exception("CNPJ não encontrado na Receita Federal")
        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code}")
        return resp.json()

    # ── normalização ─────────────────────────────────────────────────────────

    def _normalizar_receitaws(self, data: dict) -> dict:
        """Converte resposta da ReceitaWS para o mesmo formato da BrasilAPI."""
        atividades = data.get("atividade_principal") or [{}]
        cnae_cod  = atividades[0].get("code", "") if atividades else ""
        cnae_desc = atividades[0].get("text", "") if atividades else ""

        natureza = data.get("natureza_juridica", "")
        if " - " in natureza:
            nat_cod, nat_desc = natureza.split(" - ", 1)
        else:
            nat_cod, nat_desc = natureza, natureza

        socios = [
            {
                "nome_socio": s.get("nome", ""),
                "qualificacao_socio": s.get("qual", ""),
            }
            for s in data.get("qsa", [])
        ]

        return {
            "cnpj": re.sub(r"\D", "", data.get("cnpj", "")),
            "razao_social": data.get("nome", ""),
            "nome_fantasia": data.get("fantasia", ""),
            "situacao_cadastral": data.get("situacao", ""),
            "descricao_situacao_cadastral": data.get("situacao", ""),
            "data_inicio_atividade": data.get("abertura", ""),
            "data_situacao_cadastral": data.get("data_situacao", ""),
            "cnae_fiscal": cnae_cod,
            "cnae_fiscal_descricao": cnae_desc,
            "natureza_juridica": nat_cod.strip(),
            "descricao_natureza_juridica": nat_desc.strip(),
            "porte": data.get("porte", ""),
            "descricao_porte": data.get("porte", ""),
            "logradouro": data.get("logradouro", ""),
            "numero": data.get("numero", ""),
            "complemento": data.get("complemento", ""),
            "bairro": data.get("bairro", ""),
            "municipio": data.get("municipio", ""),
            "uf": data.get("uf", ""),
            "cep": data.get("cep", ""),
            "telefone": data.get("telefone", ""),
            "email": data.get("email", ""),
            "capital_social": data.get("capital_social", ""),
            "qsa": socios,
        }

    @staticmethod
    def _fmt(cnpj: str) -> str:
        if len(cnpj) == 14:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        return cnpj
