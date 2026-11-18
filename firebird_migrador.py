import os
import queue
import subprocess
import tempfile
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


APP_TITLE = "Migrador Firebird 2.1 para 3.0"


class MigradorFirebird(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("790x650")
        self.minsize(690, 560)
        self.events = queue.Queue()
        self.running = False

        self.source_var = tk.StringVar()
        self.gbak21_var = tk.StringVar()
        self.gbak30_var = tk.StringVar()
        self.dest_var = tk.StringVar()
        self.user_var = tk.StringVar(value="SYSDBA")
        self.password21_var = tk.StringVar()
        self.password30_var = tk.StringVar()
        self.show_password_var = tk.BooleanVar(value=False)

        self._build_ui()
        self.after(100, self._process_events)

    def _build_ui(self):
        root = ttk.Frame(self, padding=14)
        root.pack(fill="both", expand=True)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(8, weight=1)

        ttk.Label(root, text="Migração Firebird 2.1 → 3.0", font=("Segoe UI", 16, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 6)
        )
        ttk.Label(
            root,
            text=("O programa cria um backup temporário com o gbak 2.1 e restaura uma nova cópia "
                  "com o gbak 3.0. O arquivo de origem não é alterado."),
            wraplength=740,
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 14))

        self._file_row(root, 2, "Banco de origem (.fdb/.gdb):", self.source_var, self._choose_source)
        self._file_row(root, 3, "gbak do Firebird 2.1:", self.gbak21_var, self._choose_gbak21)
        self._file_row(root, 4, "gbak do Firebird 3.0:", self.gbak30_var, self._choose_gbak30)
        self._file_row(root, 5, "Novo banco de destino:", self.dest_var, self._choose_destination)

        ttk.Label(root, text="Usuário:").grid(row=6, column=0, sticky="w", pady=5)
        ttk.Entry(root, textvariable=self.user_var, width=26).grid(row=6, column=1, sticky="w", pady=5)

        pass_frame = ttk.Frame(root)
        pass_frame.grid(row=7, column=0, columnspan=3, sticky="ew", pady=4)
        pass_frame.columnconfigure(1, weight=1)
        ttk.Label(pass_frame, text="Senha no Firebird 2.1:").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        self.pass21_entry = ttk.Entry(pass_frame, textvariable=self.password21_var, show="•", width=30)
        self.pass21_entry.grid(row=0, column=1, sticky="w", pady=4)
        ttk.Label(pass_frame, text="Senha no Firebird 3.0:").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
        self.pass30_entry = ttk.Entry(pass_frame, textvariable=self.password30_var, show="•", width=30)
        self.pass30_entry.grid(row=1, column=1, sticky="w", pady=4)
        ttk.Checkbutton(pass_frame, text="Mostrar senhas", variable=self.show_password_var,
                        command=self._toggle_passwords).grid(row=0, column=2, rowspan=2, padx=12)
        ttk.Label(
            pass_frame,
            text="As senhas são usadas somente durante a execução e não são gravadas pelo programa.",
            foreground="#555",
        ).grid(row=2, column=0, columnspan=3, sticky="w", pady=(4, 0))

        ttk.Label(root, text="Andamento / mensagens:").grid(row=8, column=0, columnspan=3, sticky="w", pady=(10, 4))
        self.log = tk.Text(root, height=12, wrap="word", state="disabled", font=("Consolas", 9))
        self.log.grid(row=9, column=0, columnspan=3, sticky="nsew")
        root.rowconfigure(9, weight=1)
        scroll = ttk.Scrollbar(root, orient="vertical", command=self.log.yview)
        scroll.grid(row=9, column=3, sticky="ns")
        self.log.configure(yscrollcommand=scroll.set)

        buttons = ttk.Frame(root)
        buttons.grid(row=10, column=0, columnspan=3, sticky="ew", pady=(12, 0))
        self.start_button = ttk.Button(buttons, text="Iniciar migração", command=self._start)
        self.start_button.pack(side="left")
        self.progress = ttk.Progressbar(buttons, mode="indeterminate", length=220)
        self.progress.pack(side="left", padx=12)
        ttk.Button(buttons, text="Fechar", command=self.destroy).pack(side="right")

    @staticmethod
    def _file_row(parent, row, label, variable, command):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=(0, 8), pady=5)
        ttk.Button(parent, text="Procurar...", command=command).grid(row=row, column=2, sticky="ew", pady=5)

    def _choose_source(self):
        path = filedialog.askopenfilename(
            title="Selecione o banco Firebird de origem",
            filetypes=[("Bancos Firebird", "*.fdb *.gdb"), ("Todos os arquivos", "*.*")],
        )
        if path:
            self.source_var.set(path)
            if not self.dest_var.get():
                p = Path(path)
                self.dest_var.set(str(p.with_name(p.stem + "_FB3" + p.suffix)))

    def _choose_gbak21(self):
        self._choose_exe(self.gbak21_var, "Selecione gbak.exe do Firebird 2.1")

    def _choose_gbak30(self):
        self._choose_exe(self.gbak30_var, "Selecione gbak.exe do Firebird 3.0")

    @staticmethod
    def _choose_exe(variable, title):
        path = filedialog.askopenfilename(
            title=title,
            filetypes=[("gbak.exe", "gbak.exe"), ("Executáveis", "*.exe"), ("Todos os arquivos", "*.*")],
        )
        if path:
            variable.set(path)

    def _choose_destination(self):
        path = filedialog.asksaveasfilename(
            title="Escolha o nome e local do novo banco",
            defaultextension=".fdb",
            filetypes=[("Banco Firebird", "*.fdb"), ("Todos os arquivos", "*.*")],
        )
        if path:
            self.dest_var.set(path)

    def _toggle_passwords(self):
        show = "" if self.show_password_var.get() else "•"
        self.pass21_entry.configure(show=show)
        self.pass30_entry.configure(show=show)

    def _append_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text.rstrip() + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _validate(self):
        source = Path(self.source_var.get().strip())
        gbak21 = Path(self.gbak21_var.get().strip())
        gbak30 = Path(self.gbak30_var.get().strip())
        dest = Path(self.dest_var.get().strip())
        username = self.user_var.get().strip()

        if not source.is_file():
            raise ValueError("Selecione um arquivo de banco de origem existente.")
        if not gbak21.is_file():
            raise ValueError("Selecione o gbak.exe da instalação Firebird 2.1.")
        if not gbak30.is_file():
            raise ValueError("Selecione o gbak.exe da instalação Firebird 3.0.")
        if not dest.name:
            raise ValueError("Informe o caminho do novo banco de destino.")
        if not dest.parent.exists():
            raise ValueError("A pasta escolhida para o destino não existe.")
        if source.resolve() == dest.resolve():
            raise ValueError("O destino não pode ser o mesmo arquivo da origem.")
        if dest.exists():
            raise ValueError("O arquivo de destino já existe. Escolha outro nome para evitar sobrescrevê-lo.")
        if not username:
            raise ValueError("Informe o usuário do banco.")
        if not self.password21_var.get():
            raise ValueError("Informe a senha do usuário no Firebird 2.1.")
        if not self.password30_var.get():
            raise ValueError("Informe a senha do usuário no Firebird 3.0.")
        return source, gbak21, gbak30, dest, username

    def _start(self):
        if self.running:
            return
        try:
            args = self._validate()
        except ValueError as exc:
            messagebox.showerror("Dados incompletos", str(exc), parent=self)
            return
        if not messagebox.askyesno(
            "Confirmar migração",
            "Será criado um novo banco no destino. O banco original será mantido sem alterações.\n\nContinuar?",
            parent=self,
        ):
            return

        self.running = True
        self.start_button.configure(state="disabled")
        self.progress.start(10)
        self._append_log("Iniciando migração. Não feche o programa até a conclusão.")
        source, gbak21, gbak30, dest, username = args
        password21 = self.password21_var.get()
        password30 = self.password30_var.get()
        threading.Thread(
            target=self._worker,
            args=(source, gbak21, gbak30, dest, username, password21, password30),
            daemon=True,
        ).start()

    def _run_gbak(self, executable, arguments, password, label):
        # A senha é fornecida por variável de ambiente, evitando incluí-la na linha de comando.
        env = os.environ.copy()
        env["ISC_PASSWORD"] = password
        self.events.put(("log", f"\n{label}"))
        try:
            result = subprocess.run(
                [str(executable), *arguments],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                timeout=None,
            )
        except OSError as exc:
            raise RuntimeError(f"Não foi possível executar {executable}: {exc}") from exc
        for output in (result.stdout, result.stderr):
            if output.strip():
                self.events.put(("log", output.strip()))
        if result.returncode != 0:
            raise RuntimeError(f"{label} falhou (código {result.returncode}). Confira as mensagens acima.")

    def _worker(self, source, gbak21, gbak30, dest, username, password21, password30):
        try:
            with tempfile.TemporaryDirectory(prefix="firebird_migracao_") as tmp:
                backup = Path(tmp) / "migracao.fbk"
                self._run_gbak(
                    gbak21,
                    ["-b", "-v", "-user", username, str(source), str(backup)],
                    password21,
                    "Etapa 1/2: backup usando Firebird 2.1...",
                )
                if not backup.is_file() or backup.stat().st_size == 0:
                    raise RuntimeError("O gbak 2.1 terminou, mas não gerou um arquivo de backup válido.")

                self._run_gbak(
                    gbak30,
                    ["-c", "-v", "-user", username, str(backup), str(dest)],
                    password30,
                    "Etapa 2/2: restauração usando Firebird 3.0...",
                )
                if not dest.exists():
                    raise RuntimeError("A restauração terminou sem erro, mas o arquivo de destino não foi encontrado.")

            self.events.put(("done", f"Migração concluída. Novo banco criado em:\n{dest}"))
        except Exception as exc:
            # Se o gbak deixou um arquivo de destino parcial, não o removemos automaticamente.
            self.events.put(("error", str(exc)))

    def _process_events(self):
        try:
            while True:
                kind, text = self.events.get_nowait()
                if kind == "log":
                    self._append_log(text)
                elif kind in ("done", "error"):
                    self.running = False
                    self.start_button.configure(state="normal")
                    self.progress.stop()
                    self._append_log(text)
                    if kind == "done":
                        messagebox.showinfo("Concluído", text, parent=self)
                    else:
                        messagebox.showerror("Migração interrompida", text, parent=self)
        except queue.Empty:
            pass
        self.after(100, self._process_events)


if __name__ == "__main__":
    app = MigradorFirebird()
    app.mainloop()
