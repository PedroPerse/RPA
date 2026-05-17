import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


def _limpar_cnpj(texto: str) -> str:
    return re.sub(r"\D", "", texto)


def _validar_cnpj(cnpj: str) -> bool:
    cnpj = _limpar_cnpj(cnpj)
    if len(cnpj) != 14 or len(set(cnpj)) == 1:
        return False
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
    d1 = 0 if soma % 11 < 2 else 11 - (soma % 11)
    soma = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
    d2 = 0 if soma % 11 < 2 else 11 - (soma % 11)
    return int(cnpj[12]) == d1 and int(cnpj[13]) == d2


class InputWindow:
    def __init__(self):
        self._cnpjs: list[str] = []
        self._root: tk.Tk | None = None
        self._texto: tk.Text | None = None
        self._status_var: tk.StringVar | None = None

    def obter_cnpjs(self) -> list[str]:
        self._criar_janela()
        self._root.mainloop()
        return self._cnpjs

    def _criar_janela(self):
        self._root = tk.Tk()
        self._root.title("Bot Verificação CNPJ")
        self._root.geometry("520x500")
        self._root.minsize(520, 500)
        self._root.resizable(True, False)
        self._root.configure(bg="#f0f0f0")

        # Cabeçalho
        tk.Label(
            self._root,
            text="Verificação de CNPJ",
            font=("Segoe UI", 14, "bold"),
            bg="#f0f0f0",
            fg="#333333",
        ).pack(pady=(18, 2))

        tk.Label(
            self._root,
            text="Informe os CNPJs para consulta (um por linha)",
            font=("Segoe UI", 9),
            bg="#f0f0f0",
            fg="#666666",
        ).pack()

        # Área de texto
        frame_texto = tk.Frame(self._root, bg="#f0f0f0")
        frame_texto.pack(padx=20, pady=10, fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame_texto)
        scrollbar.pack(side="right", fill="y")

        self._texto = tk.Text(
            frame_texto,
            font=("Courier New", 11),
            yscrollcommand=scrollbar.set,
            relief="solid",
            bd=1,
            padx=8,
            pady=6,
            height=12,
        )
        self._texto.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self._texto.yview)
        self._texto.bind("<KeyRelease>", lambda _: self._atualizar_status())

        # Botões secundários
        frame_acoes = tk.Frame(self._root, bg="#f0f0f0")
        frame_acoes.pack(padx=20, fill="x")

        tk.Button(
            frame_acoes,
            text="Carregar arquivo (.txt / .xlsx)",
            command=self._carregar_arquivo,
            font=("Segoe UI", 9),
            relief="flat",
            bg="#e0e0e0",
            padx=10, pady=4,
        ).pack(side="left")

        tk.Button(
            frame_acoes,
            text="Limpar",
            command=self._limpar,
            font=("Segoe UI", 9),
            relief="flat",
            bg="#e0e0e0",
            padx=10, pady=4,
        ).pack(side="left", padx=(6, 0))

        # Status
        self._status_var = tk.StringVar(value="Nenhum CNPJ informado")
        tk.Label(
            self._root,
            textvariable=self._status_var,
            font=("Segoe UI", 9),
            bg="#f0f0f0",
            fg="#888888",
        ).pack(pady=(8, 0))

        # Botão executar
        tk.Button(
            self._root,
            text="Executar Consulta",
            command=self._ao_executar,
            font=("Segoe UI", 11, "bold"),
            bg="#2e7d32",
            fg="white",
            activebackground="#1b5e20",
            activeforeground="white",
            relief="flat",
            padx=20, pady=8,
            cursor="hand2",
        ).pack(pady=(6, 18))

        self._root.protocol("WM_DELETE_WINDOW", self._ao_fechar)

    def _atualizar_status(self):
        linhas = self._texto.get("1.0", "end").splitlines()
        validos = [l for l in linhas if _validar_cnpj(l.strip())]
        invalidos = [l for l in linhas if l.strip() and not _validar_cnpj(l.strip())]
        partes = []
        if validos:
            partes.append(f"{len(validos)} CNPJ(s) válido(s)")
        if invalidos:
            partes.append(f"{len(invalidos)} inválido(s)")
        self._status_var.set("  •  ".join(partes) if partes else "Nenhum CNPJ informado")

    def _carregar_arquivo(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar arquivo de CNPJs",
            filetypes=[("Arquivos suportados", "*.txt *.xlsx *.csv"), ("Todos", "*.*")],
        )
        if not caminho:
            return

        cnpjs = []
        sufixo = Path(caminho).suffix.lower()

        try:
            if sufixo == ".xlsx":
                import openpyxl
                wb = openpyxl.load_workbook(caminho, read_only=True, data_only=True)
                ws = wb.active
                for linha in ws.iter_rows(values_only=True):
                    for celula in linha:
                        if celula:
                            cnpjs.append(str(celula).strip())
                wb.close()
            else:
                with open(caminho, encoding="utf-8", errors="ignore") as f:
                    cnpjs = [l.strip() for l in f if l.strip()]
        except Exception as e:
            messagebox.showerror("Erro ao carregar arquivo", str(e))
            return

        self._texto.delete("1.0", "end")
        self._texto.insert("1.0", "\n".join(cnpjs))
        self._atualizar_status()

    def _limpar(self):
        self._texto.delete("1.0", "end")
        self._atualizar_status()

    def _ao_executar(self):
        linhas = self._texto.get("1.0", "end").splitlines()
        validos = [_limpar_cnpj(l.strip()) for l in linhas if _validar_cnpj(l.strip())]

        if not validos:
            messagebox.showwarning(
                "Nenhum CNPJ válido",
                "Informe ao menos um CNPJ válido antes de executar.",
            )
            return

        self._cnpjs = validos
        self._root.destroy()

    def _ao_fechar(self):
        self._cnpjs = []
        self._root.destroy()
