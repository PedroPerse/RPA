from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import requests

DIAS_SEMANA = [
    "Segunda-feira", "Terça-feira", "Quarta-feira",
    "Quinta-feira", "Sexta-feira", "Sábado", "Domingo",
]

# wttr.in weather codes → emoji
_CODIGO_EMOJI: dict[int, str] = {
    113: "☀️",
    116: "⛅",
    119: "☁️",
    122: "☁️",
    143: "🌫️", 248: "🌫️", 260: "🌫️",
    176: "🌦️", 263: "🌦️", 266: "🌦️", 281: "🌦️", 284: "🌦️",
    293: "🌧️", 296: "🌧️", 299: "🌧️", 302: "🌧️",
    305: "🌧️", 308: "🌧️", 353: "🌦️", 356: "🌧️", 359: "🌧️",
    179: "❄️", 227: "❄️", 230: "❄️",
    182: "🌨️", 185: "🌨️", 311: "🌨️", 314: "🌨️",
    317: "🌨️", 320: "🌨️", 323: "🌨️", 326: "🌨️",
    200: "⛈️", 386: "⛈️", 389: "⛈️", 392: "⛈️", 395: "⛈️",
}

# Traduções das descrições em inglês
_DESCRICAO_PT: dict[str, str] = {
    "sunny": "Ensolarado",
    "clear": "Céu limpo",
    "partly cloudy": "Parcialmente nublado",
    "cloudy": "Nublado",
    "overcast": "Encoberto",
    "mist": "Névoa",
    "fog": "Nevoeiro",
    "freezing fog": "Nevoeiro gelado",
    "patchy rain possible": "Chuva isolada possível",
    "patchy rain nearby": "Chuva próxima isolada",
    "patchy snow possible": "Neve isolada possível",
    "blowing snow": "Neve com vento",
    "blizzard": "Tempestade de neve",
    "thundery outbreaks possible": "Trovoadas possíveis",
    "light rain": "Chuva fraca",
    "moderate rain": "Chuva moderada",
    "heavy rain": "Chuva forte",
    "light snow": "Neve fraca",
    "light drizzle": "Garoa",
    "freezing drizzle": "Garoa gelada",
    "light sleet": "Granizo fraco",
    "moderate snow": "Neve moderada",
    "heavy snow": "Neve forte",
    "ice pellets": "Granizo",
    "thunderstorm": "Tempestade",
    "light rain shower": "Pancada de chuva fraca",
    "moderate or heavy rain shower": "Pancada de chuva moderada",
    "torrential rain shower": "Chuva torrencial",
    "light snow showers": "Neve fraca",
    "patchy light rain": "Chuva fraca isolada",
    "patchy light rain with thunder": "Chuva com trovões",
    "moderate or heavy rain with thunder": "Chuva forte com trovões",
    "patchy light drizzle": "Garoa fraca isolada",
    "heavy freezing drizzle": "Garoa gelada forte",
    "light freezing rain": "Chuva gelada fraca",
    "moderate or heavy freezing rain": "Chuva gelada moderada",
    "light sleet showers": "Granizo fraco",
    "moderate or heavy sleet showers": "Granizo moderado",
    "moderate or heavy snow showers": "Neve moderada/forte",
    "light showers of ice pellets": "Granizo fraco",
    "moderate or heavy showers of ice pellets": "Granizo moderado",
    "patchy light rain in area with thunder": "Chuva fraca com trovões",
    "moderate or heavy rain in area with thunder": "Chuva forte com trovões",
    "patchy light snow in area with thunder": "Neve fraca com trovões",
    "moderate or heavy snow in area with thunder": "Neve forte com trovões",
}


@dataclass
class HoraTempo:
    hora: str
    temp: str
    emoji: str
    descricao: str

    def __str__(self) -> str:
        return f"{self.hora} {self.emoji} {self.temp}  {self.descricao}"


@dataclass
class DadosTempo:
    cidade: str
    data: str
    dia_semana: str
    min_temp: str
    max_temp: str
    horas: list[HoraTempo] = field(default_factory=list)
    sucesso: bool = False
    erro: Optional[str] = None


def _emoji(codigo: int) -> str:
    return _CODIGO_EMOJI.get(codigo, "🌡️")


def _descricao(desc_en: str) -> str:
    return _DESCRICAO_PT.get(desc_en.strip().lower(), desc_en.strip())


def buscar_previsao(cidade: str) -> DadosTempo:
    cidade_url = cidade.replace(" ", "+")
    url = f"https://wttr.in/{cidade_url}?format=j1"

    try:
        response = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (bot-previsao-tempo)"},
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return DadosTempo(
            cidade=cidade, data="", dia_semana="",
            min_temp="?", max_temp="?",
            sucesso=False, erro=str(e),
        )

    hoje = data["weather"][0]
    now = datetime.now()

    horas: list[HoraTempo] = []
    for h in hoje["hourly"]:
        hora_num = int(h["time"]) // 100
        horas.append(HoraTempo(
            hora=f"{hora_num:02d}h",
            temp=f"{h['tempC']}°",
            emoji=_emoji(int(h["weatherCode"])),
            descricao=_descricao(h["weatherDesc"][0]["value"]),
        ))

    return DadosTempo(
        cidade=cidade,
        data=now.strftime("%d/%m/%Y"),
        dia_semana=DIAS_SEMANA[now.weekday()],
        min_temp=f"{hoje['mintempC']}°",
        max_temp=f"{hoje['maxtempC']}°",
        horas=horas,
        sucesso=True,
    )
