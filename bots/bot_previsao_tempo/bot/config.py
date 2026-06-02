import os
from dataclasses import dataclass, field


@dataclass
class Config:
    cidade: str = field(default_factory=lambda: os.getenv("CIDADE", "São Paulo"))
    contato_whatsapp: str = field(default_factory=lambda: os.getenv("CONTATO_WHATSAPP", ""))
    headless: bool = False
    timeout: int = 30000
    log_dir: str = "logs"
    storage_dir: str = "storage"

    def validar(self) -> bool:
        return bool(self.contato_whatsapp.strip())
