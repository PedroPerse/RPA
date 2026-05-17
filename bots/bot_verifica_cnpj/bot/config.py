from dataclasses import dataclass, field


@dataclass
class Config:
    log_dir: str = "logs"
    output_dir: str = "resultados"
    delay_entre_consultas: float = 1.5
