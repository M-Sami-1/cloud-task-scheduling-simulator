from __future__ import annotations

import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import OUTPUT_CSV, TASKS_CSV, TaskConfig, enable_dpi_awareness, ensure_runtime_paths

ensure_runtime_paths()
enable_dpi_awareness()

from dataset.generator import generate_tasks, generate_tasks_csv, load_tasks_from_csv
from scheduler.scheduler import ScheduleResult, Scheduler
from visualization.plotter import Plotter


class SchedulerApp:
    BG = "#f8fafc"
    CARD = "#ffffff"
    BORDER = "#d8e2ee"
    HEADER = "#0f172a"
    ACCENT = "#0ea5e9"
    ACCENT_DARK = "#0284c7"
    SUCCESS = "#14b8a6"
    WARNING = "#f59e0b"
    TEXT = "#0f172a"
    MUTED = "#64748b"
    ROW_ALT = "#f8fbff"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Task Scheduling in Cloud Computing")
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        window_w = min(1800, max(1500, screen_w - 120))
        window_h = min(1120, max(980, screen_h - 60))
        self.root.geometry(f"{window_w}x{window_h}")
        self.root.minsize(1500, 980)
        self.root.configure(bg=self.BG)

        self.scheduler = Scheduler()
        self.plotter = Plotter()
        self.latest_results: list[ScheduleResult] = []
        self.active_algorithm: str | None = None
        self.reference_csv_path: Path | None = None

        self.selected_count = tk.IntVar(value=500)
        self.custom_count_var = tk.StringVar()
        self.vm_count_var = tk.IntVar(value=5)
        self.dataset_label_var = tk.StringVar(value=TASKS_CSV.name)
        self.status_var = tk.StringVar(value="Ready to run experiments.")
        self.footer_var = tk.StringVar(value="Task Scheduling Simulator - Research Dashboard")
        self.summary_name_var = tk.StringVar(value="Summary Results")

        self.algorithm_vars = {
            "FCFS": tk.BooleanVar(value=True),
            "SJF": tk.BooleanVar(value=True),
            "EFT": tk.BooleanVar(value=True),
            "Min-Min": tk.BooleanVar(value=False),
            "Max-Min": tk.BooleanVar(value=False),
        }

        self._setup_style()
        self._build_scrollable_shell()
        self._build_header()
        self._build_experiment_card()
        self._build_dashboard()
        self._build_footer()
        self._load_initial_dataset()

    def _setup_style(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Thin.TSeparator", background=self.BORDER)
        style.configure("TCombobox", padding=6)
        style.configure("TSpinbox", padding=6)

    def _build_scrollable_shell(self) -> None:
        self.shell_canvas = tk.Canvas(self.root, bg=self.BG, highlightthickness=0)
        self.shell_scroll = ttk.Scrollbar(self.root, orient="vertical", command=self.shell_canvas.yview)
        self.content = tk.Frame(self.shell_canvas, bg=self.BG)
        self.content_window = self.shell_canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.shell_canvas.configure(yscrollcommand=self.shell_scroll.set)

        self.shell_canvas.pack(side="left", fill="both", expand=True)
        self.shell_scroll.pack(side="right", fill="y")

        self.shell_canvas.bind("<Configure>", self._on_shell_canvas_configure)
        self.content.bind("<Configure>", self._on_content_configure)
        self.shell_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.shell_canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.shell_canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _on_shell_canvas_configure(self, event: tk.Event) -> None:
        self.shell_canvas.itemconfigure(self.content_window, width=event.width)

    def _on_content_configure(self, _event: tk.Event) -> None:
        self.shell_canvas.configure(scrollregion=self.shell_canvas.bbox("all"))

    def _on_mousewheel(self, event: tk.Event) -> None:
        if getattr(event, "num", None) == 4:
            self.shell_canvas.yview_scroll(-1, "units")
        elif getattr(event, "num", None) == 5:
            self.shell_canvas.yview_scroll(1, "units")
        elif getattr(event, "delta", 0):
            self.shell_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _build_header(self) -> None:
        header = tk.Frame(self.content, bg=self.HEADER, height=58)
        header.pack(fill="x")
        header.pack_propagate(False)

        center = tk.Frame(header, bg=self.HEADER)
        center.place(relx=0.02, rely=0.5, anchor="w")
        tk.Label(
            center,
            text="Task Scheduling in Cloud Computing",
            bg=self.HEADER,
            fg="#ffffff",
            font=("Segoe UI Semibold", 17),
        ).pack(anchor="w")

    def _build_experiment_card(self) -> None:
        card = self._card(self.content)
        card.pack(fill="x", padx=24, pady=(18, 18))
        inner = tk.Frame(card, bg=self.CARD, padx=22, pady=18)
        inner.pack(fill="both", expand=True)

        tk.Label(inner, text="Run Experiments", bg=self.CARD, fg=self.TEXT, font=("Segoe UI Semibold", 18)).grid(row=0, column=0, sticky="w", pady=(0, 16))

        dataset_col = self._section(inner)
        task_col = self._section(inner)
        scheduler_col = self._section(inner)
        action_col = self._section(inner)

        dataset_col.grid(row=1, column=0, sticky="nsew", padx=(0, 20))
        task_col.grid(row=1, column=1, sticky="nsew", padx=(0, 20))
        scheduler_col.grid(row=1, column=2, sticky="nsew", padx=(0, 20))
        action_col.grid(row=1, column=3, sticky="nsew")

        inner.grid_columnconfigure(0, weight=4)
        inner.grid_columnconfigure(1, weight=5)
        inner.grid_columnconfigure(2, weight=3)
        inner.grid_columnconfigure(3, weight=2)

        tk.Label(dataset_col, text="Dataset Source", bg=self.CARD, fg=self.TEXT, font=("Segoe UI Semibold", 12)).pack(anchor="w")
        tk.Label(
            dataset_col,
            text="Upload a CSV if you want to inspect a reference file, or keep the generated dataset.",
            bg=self.CARD,
            fg=self.MUTED,
            justify="left",
            wraplength=370,
        ).pack(anchor="w", pady=(4, 12))

        dataset_box = tk.Frame(dataset_col, bg="#f8fbff", highlightthickness=1, highlightbackground=self.BORDER)
        dataset_box.pack(fill="x")
        tk.Button(
            dataset_box,
            text="Choose CSV",
            command=self._choose_reference_file,
            bg="#ffffff",
            fg=self.TEXT,
            activebackground="#f1f5f9",
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        ).pack(side="left", padx=6, pady=6)
        tk.Button(
            dataset_box,
            text="Use Generated",
            command=self._clear_reference_file,
            bg=self.BG,
            fg=self.ACCENT_DARK,
            activebackground="#e0f2fe",
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        ).pack(side="left", padx=(0, 8), pady=6)
        tk.Label(dataset_box, textvariable=self.dataset_label_var, bg="#f8fbff", fg=self.TEXT, font=("Segoe UI", 10), anchor="w").pack(side="left", padx=8)

        tk.Label(task_col, text="Task Counts", bg=self.CARD, fg=self.TEXT, font=("Segoe UI Semibold", 12)).pack(anchor="w")
        tk.Label(task_col, text="Pick a preset or enter a custom amount.", bg=self.CARD, fg=self.MUTED).pack(anchor="w", pady=(4, 12))
        preset_row = tk.Frame(task_col, bg=self.CARD)
        preset_row.pack(anchor="w")
        for count in (100, 200, 500, 1000):
            self._make_task_radio(preset_row, count).pack(side="left", padx=(0, 12))
        custom_row = tk.Frame(task_col, bg=self.CARD)
        custom_row.pack(fill="x", pady=(14, 0))
        self.custom_entry = tk.Entry(
            custom_row,
            textvariable=self.custom_count_var,
            font=("Segoe UI", 11),
            relief="flat",
            bd=0,
            bg="#ffffff",
            fg=self.TEXT,
            highlightthickness=2,
            highlightbackground=self.BORDER,
            highlightcolor=self.ACCENT,
            insertbackground=self.TEXT,
        )
        self.custom_entry.pack(fill="x", ipady=9)
        self._set_custom_placeholder()
        self.custom_entry.bind("<FocusIn>", self._clear_custom_placeholder)
        self.custom_entry.bind("<FocusOut>", self._restore_custom_placeholder)

        tk.Label(scheduler_col, text="Schedulers", bg=self.CARD, fg=self.TEXT, font=("Segoe UI Semibold", 12)).pack(anchor="w")
        tk.Label(scheduler_col, text="Select the algorithms to compare.", bg=self.CARD, fg=self.MUTED).pack(anchor="w", pady=(4, 12))
        for algorithm in ("FCFS", "SJF", "EFT", "Min-Min", "Max-Min"):
            ttk.Checkbutton(scheduler_col, text=algorithm, variable=self.algorithm_vars[algorithm]).pack(anchor="w", pady=4)

        tk.Label(action_col, text="Resources", bg=self.CARD, fg=self.TEXT, font=("Segoe UI Semibold", 12)).pack(anchor="w")
        tk.Label(action_col, text="VM Count", bg=self.CARD, fg=self.MUTED).pack(anchor="w", pady=(8, 6))
        ttk.Spinbox(action_col, from_=1, to=20, textvariable=self.vm_count_var, width=10).pack(anchor="w")
        tk.Button(
            action_col,
            text="Run",
            command=self.run_selected_experiments,
            bg=self.ACCENT,
            fg="#ffffff",
            activebackground=self.ACCENT_DARK,
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=38,
            pady=12,
            font=("Segoe UI Semibold", 11),
            cursor="hand2",
        ).pack(anchor="e", pady=(34, 0))

    def _build_dashboard(self) -> None:
        dashboard = tk.Frame(self.content, bg=self.BG)
        dashboard.pack(fill="both", expand=True, padx=24, pady=(0, 12))

        left = tk.Frame(dashboard, bg=self.BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 16))

        right = tk.Frame(dashboard, bg=self.BG, width=900)
        right.pack(side="left", fill="y")
        right.pack_propagate(False)

        self._build_summary_card(left)
        self._build_chart_stack(right)

    def _build_summary_card(self, parent: tk.Widget) -> None:
        self.summary_card = self._card(parent)
        self.summary_card.pack(fill="both", expand=True)
        header = tk.Frame(self.summary_card, bg=self.CARD, padx=18, pady=12)
        header.pack(fill="x")
        tk.Label(header, textvariable=self.summary_name_var, bg=self.CARD, fg=self.TEXT, font=("Segoe UI Semibold", 15)).pack(side="left")
        tk.Label(header, textvariable=self.status_var, bg=self.CARD, fg=self.MUTED, font=("Segoe UI", 10)).pack(side="right")

        table_shell = tk.Frame(self.summary_card, bg=self.CARD, padx=16, pady=2)
        table_shell.pack(fill="both", expand=True)
        self.table_header = tk.Frame(table_shell, bg="#eaf2fb", highlightthickness=1, highlightbackground=self.BORDER)
        self.table_header.pack(fill="x")
        self.table_body = tk.Frame(table_shell, bg=self.CARD)
        self.table_body.pack(fill="both", expand=True, pady=(1, 0))

        self._build_table_header(self.table_header)

        actions = tk.Frame(self.summary_card, bg=self.CARD, padx=16, pady=12)
        actions.pack(fill="x")
        tk.Button(
            actions,
            text="Download Summary CSV",
            command=self._download_summary_csv,
            bg=self.HEADER,
            fg="#ffffff",
            activebackground="#111827",
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=26,
            pady=11,
            font=("Segoe UI Semibold", 10),
            cursor="hand2",
        ).pack(fill="x")
        tk.Button(
            actions,
            text="Open Full VM Snapshot",
            command=self._open_vm_snapshot,
            bg="#1d4ed8",
            fg="#ffffff",
            activebackground="#1e40af",
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=26,
            pady=11,
            font=("Segoe UI Semibold", 10),
            cursor="hand2",
        ).pack(fill="x", pady=(10, 0))

    def _build_table_header(self, parent: tk.Widget) -> None:
        columns = [
            ("Scheduler", 15),
            ("Tasks", 8),
            ("Makespan(s)", 12),
            ("Throughput", 12),
            ("Util.", 8),
            ("Plot", 8),
            ("CSV", 8),
        ]
        for index, (title, width) in enumerate(columns):
            tk.Label(
                parent,
                text=title,
                bg="#eaf2fb",
                fg=self.TEXT,
                font=("Segoe UI Semibold", 10),
                width=width,
                pady=10,
            ).grid(row=0, column=index, sticky="nsew", padx=1)
        for index in range(len(columns)):
            parent.grid_columnconfigure(index, weight=1)

    def _build_chart_stack(self, parent: tk.Widget) -> None:
        self.chart_makespan = self._chart_card(parent, "Makespan Comparison", 265)
        self.chart_makespan.pack(fill="x", pady=(0, 12))
        self.chart_throughput = self._chart_card(parent, "Throughput Comparison", 265)
        self.chart_throughput.pack(fill="x", pady=(0, 12))
        self.chart_utilization = self._chart_card(parent, "VM Utilization Snapshot", 410)
        self.chart_utilization.pack(fill="both", expand=True)

        self.makespan_canvas = self._chart_canvas(self.chart_makespan, width=840, height=265)
        self.throughput_canvas = self._chart_canvas(self.chart_throughput, width=840, height=265)
        self.utilization_canvas = self._chart_canvas(self.chart_utilization, width=840, height=410)

    def _chart_card(self, parent: tk.Widget, title: str, height: int) -> tk.Frame:
        card = self._card(parent)
        card.pack_propagate(False)
        card.configure(height=height)
        inner = tk.Frame(card, bg=self.CARD, padx=18, pady=12)
        inner.pack(fill="both", expand=True)
        tk.Label(inner, text=title, bg=self.CARD, fg=self.TEXT, font=("Segoe UI Semibold", 13)).pack(anchor="w", pady=(0, 8))
        card.inner = inner  # type: ignore[attr-defined]
        return card

    def _chart_canvas(self, card: tk.Frame, width: int = 620, height: int = 220) -> tk.Canvas:
        canvas = tk.Canvas(card.inner, width=width, height=height, bg=self.CARD, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        return canvas

    def _build_footer(self) -> None:
        footer = tk.Label(self.content, textvariable=self.footer_var, bg=self.BG, fg=self.MUTED, font=("Segoe UI", 10))
        footer.pack(fill="x", pady=(0, 12))

    def _card(self, parent: tk.Widget) -> tk.Frame:
        return tk.Frame(parent, bg=self.CARD, highlightthickness=1, highlightbackground=self.BORDER)

    def _section(self, parent: tk.Widget) -> tk.Frame:
        return tk.Frame(parent, bg=self.CARD)

    def _make_task_radio(self, parent: tk.Widget, count: int) -> tk.Frame:
        frame = tk.Frame(parent, bg=self.CARD)
        tk.Radiobutton(
            frame,
            text=str(count),
            variable=self.selected_count,
            value=count,
            bg=self.CARD,
            activebackground=self.CARD,
            fg=self.TEXT,
            selectcolor="#fde68a",
            font=("Segoe UI", 10),
            command=self._clear_custom_value,
        ).pack(side="left")
        return frame

    def _set_custom_placeholder(self) -> None:
        if not self.custom_count_var.get():
            self.custom_count_var.set("Custom e.g. 350")
            self.custom_entry.configure(fg=self.MUTED)

    def _clear_custom_placeholder(self, _event: tk.Event) -> None:
        if self.custom_count_var.get() == "Custom e.g. 350":
            self.custom_count_var.set("")
            self.custom_entry.configure(fg=self.TEXT)

    def _restore_custom_placeholder(self, _event: tk.Event) -> None:
        if not self.custom_count_var.get().strip():
            self._set_custom_placeholder()

    def _clear_custom_value(self) -> None:
        if self.custom_count_var.get() == "Custom e.g. 350":
            self.custom_count_var.set("")
            self.custom_entry.configure(fg=self.TEXT)

    def _choose_reference_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Choose CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.reference_csv_path = Path(path)
            self.dataset_label_var.set(self.reference_csv_path.name)
            self.status_var.set(f"Using dataset: {self.reference_csv_path.name}")

    def _clear_reference_file(self) -> None:
        self.reference_csv_path = None
        self.dataset_label_var.set(TASKS_CSV.name)
        self.status_var.set("Using generated dataset.")

    def _load_initial_dataset(self) -> None:
        if not TASKS_CSV.exists():
            generate_tasks_csv()
        self.dataset_label_var.set(TASKS_CSV.name)

    def _resolve_task_count(self) -> int:
        custom = self.custom_count_var.get().strip()
        if custom and custom != "Custom e.g. 350":
            try:
                count = int(custom)
            except ValueError as exc:
                raise ValueError("Custom task count must be a whole number.") from exc
            if count <= 0:
                raise ValueError("Task count must be greater than zero.")
            return count
        return self.selected_count.get()

    def _selected_algorithms(self) -> list[str]:
        algorithms = [name for name, enabled in self.algorithm_vars.items() if enabled.get()]
        if not algorithms:
            raise ValueError("Select at least one scheduler.")
        return algorithms

    def _load_tasks_for_run(self, task_count: int):
        if self.reference_csv_path and self.reference_csv_path.exists():
            return load_tasks_from_csv(self.reference_csv_path)

        task_config = TaskConfig(count=task_count)
        tasks = generate_tasks_csv(task_config=task_config)
        return tasks

    def run_selected_experiments(self) -> None:
        try:
            task_count = self._resolve_task_count()
            algorithms = self._selected_algorithms()
            self.status_var.set("Running simulation...")
            self.root.update_idletasks()

            tasks = self._load_tasks_for_run(task_count)
            vms = self.scheduler.build_vms(self.vm_count_var.get(), 500, 2000)
            self.latest_results = [self.scheduler.run(tasks, vms, algorithm) for algorithm in algorithms]
            order = ["FCFS", "SJF", "EFT", "Min-Min", "Max-Min"]
            self.latest_results.sort(key=lambda result: order.index(result.algorithm) if result.algorithm in order else 99)
            self.scheduler.save_summary_csv(self.latest_results, OUTPUT_CSV)

            if self.latest_results:
                self.active_algorithm = self.latest_results[0].algorithm
            self.summary_name_var.set("Summary Results")
            self.status_var.set(f"{len(self.latest_results)} scheduler(s) completed - {len(tasks)} tasks")
            self._render_results_table()
            self.root.after_idle(self._refresh_charts)
        except Exception as exc:
            self.status_var.set("Run failed.")
            messagebox.showerror("Simulation Error", str(exc))

    def _render_results_table(self) -> None:
        for child in self.table_body.winfo_children():
            child.destroy()

        for index, result in enumerate(self.latest_results):
            row_bg = self.ROW_ALT if index % 2 else self.CARD
            row = tk.Frame(self.table_body, bg=row_bg, highlightthickness=1, highlightbackground=self.BORDER)
            row.pack(fill="x", pady=(0, 1))
            row.grid_columnconfigure(0, weight=2)
            row.grid_columnconfigure(1, weight=1)
            row.grid_columnconfigure(2, weight=1)
            row.grid_columnconfigure(3, weight=1)
            row.grid_columnconfigure(4, weight=1)
            row.grid_columnconfigure(5, weight=1)
            row.grid_columnconfigure(6, weight=1)

            cells = [
                (result.algorithm, 15),
                (len(result.assignments), 8),
                (f"{result.metrics['makespan']:.3f}", 12),
                (f"{result.metrics['throughput']:.4f}", 12),
                (f"{result.metrics['average_utilization']:.3f}", 8),
            ]
            for col, (value, width) in enumerate(cells):
                tk.Label(row, text=value, bg=row_bg, fg=self.TEXT, font=("Segoe UI", 10, "bold" if col == 0 else "normal"), width=width, pady=10).grid(row=0, column=col, sticky="nsew", padx=1)

            tk.Button(
                row,
                text="View",
                command=lambda res=result: self._view_algorithm(res),
                bg="#e0f2fe",
                fg=self.ACCENT_DARK,
                activebackground="#bae6fd",
                relief="flat",
                bd=0,
                padx=12,
                pady=7,
                font=("Segoe UI", 9, "bold"),
                cursor="hand2",
            ).grid(row=0, column=5, padx=4, pady=6)

            tk.Button(
                row,
                text="Download",
                command=lambda res=result: self._download_algorithm_csv(res),
                bg="#ecfeff",
                fg=self.SUCCESS,
                activebackground="#cffafe",
                relief="flat",
                bd=0,
                padx=12,
                pady=7,
                font=("Segoe UI", 9, "bold"),
                cursor="hand2",
            ).grid(row=0, column=6, padx=4, pady=6)

        if self.latest_results:
            self.active_algorithm = self.active_algorithm or self.latest_results[0].algorithm

    def _refresh_charts(self) -> None:
        if not self.latest_results:
            return
        self.root.update_idletasks()
        self._draw_charts()
        self.root.after(75, self._draw_charts)
        self.root.update_idletasks()

    def _draw_charts(self) -> None:
        if not self.latest_results:
            return
        self.plotter.draw_algorithm_metric_chart(self.makespan_canvas, self.latest_results, "makespan", "Makespan (s)")
        self.plotter.draw_algorithm_metric_chart(self.throughput_canvas, self.latest_results, "throughput", "Throughput")
        selected = self._active_result() or self.latest_results[0]
        self.plotter.draw_vm_utilization_chart(self.utilization_canvas, selected)

    def _active_result(self) -> ScheduleResult | None:
        if not self.active_algorithm:
            return None
        for result in self.latest_results:
            if result.algorithm == self.active_algorithm:
                return result
        return None

    def _view_algorithm(self, result: ScheduleResult) -> None:
        self.active_algorithm = result.algorithm
        self.plotter.show_result_window(self.root, result)
        self._refresh_charts()

    def _open_vm_snapshot(self) -> None:
        result = self._active_result() or (self.latest_results[0] if self.latest_results else None)
        if result is None:
            messagebox.showinfo("No Results", "Run a simulation first to open the VM utilization snapshot.")
            return
        self.plotter.show_vm_utilization_window(self.root, result)

    def _download_algorithm_csv(self, result: ScheduleResult) -> None:
        default_name = f"{result.algorithm.lower()}_result.csv"
        save_path = filedialog.asksaveasfilename(
            title=f"Save {result.algorithm} CSV",
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV files", "*.csv")],
        )
        if not save_path:
            return
        self.scheduler.save_algorithm_csv(result, Path(save_path))
        self.status_var.set(f"Saved {result.algorithm} CSV to {Path(save_path).name}")

    def _download_summary_csv(self) -> None:
        if not self.latest_results:
            messagebox.showinfo("Summary CSV", "Run a simulation first.")
            return
        save_path = filedialog.asksaveasfilename(
            title="Save Summary CSV",
            defaultextension=".csv",
            initialfile="summary_results.csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not save_path:
            return
        self.scheduler.save_summary_csv(self.latest_results, Path(save_path))
        self.status_var.set(f"Saved summary CSV to {Path(save_path).name}")

    def start(self) -> None:
        self.root.mainloop()


def main() -> None:
    root = tk.Tk()
    app = SchedulerApp(root)
    app.start()


if __name__ == "__main__":
    main()
