import os
from dataclasses import dataclass, field


@dataclass
class Config:
    browser_type: str = "chromium"
    headless: bool = field(default_factory=lambda: os.getenv("HEADLESS", "false").lower() == "true")
    search_url: str = "https://www.google.com.br"
    search_query: str = "cotação dólar hoje"
    timeout: int = 30000
    log_dir: str = "logs"

    def browser_display_name(self) -> str:
        names = {"chromium": "Chromium (Chrome)", "firefox": "Firefox", "webkit": "Safari (WebKit)"}
        return names.get(self.browser_type, self.browser_type.capitalize())
