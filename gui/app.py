from __future__ import annotations

import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import OUTPUT_CSV, ensure_runtime_paths

ensure_runtime_paths()

from dataset.generator import generate_tasks_csv, load_tasks_from_csv
from scheduler.scheduler import Scheduler
from visualization.plotter import Plotter


class SchedulerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Cloud Task Scheduling Simulator")
        self.root.geometry("1180x760")
        self.root.minsize(1040, 700)
        self.root.configure(bg="#f4f7fb")

        self.scheduler = Scheduler()
        self.plotter = Plotter()
        self.task_count_var = tk.IntVar(value=500)
        self.vm_count_var = tk.IntVar(value=5)
        self.selected_algorithm_var = tk.StringVar(value="FCFS")
        self.summary_text = tk.StringVar(value="Run a simulation to see metrics here.")

        self._setup_style()
        self._build_layout()

    def _setup_style(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("App.TFrame", background="#f4f7fb")
        style.configure("Card.TFrame", background="#ffffff", relief="flat")
        style.configure("Header.TLabel", background="#f4f7fb", foreground="#1f2937", font=("Segoe UI", 22, "bold"))
        style.configure("Sub.TLabel", background="#f4f7fb", foreground="#4b5563", font=("Segoe UI", 10))
        style.configure("CardTitle.TLabel", background="#ffffff", foreground="#111827", font=("Segoe UI", 12, "bold"))
        style.configure("Metric.TLabel", background="#ffffff", foreground="#111827", font=("Segoe UI", 10))
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=(14, 10))
        style.map("Action.TButton", foreground=[("active", "#ffffff")], background=[("active", "#2563eb")])
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def _build_layout(self) -> None:
        outer = ttk.Frame(self.root, style="App.TFrame", padding=18)
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer, style="App.TFrame")
        header.pack(fill="x", pady=(0, 14))
        ttk.Label(header, text="Cloud Task Scheduling Simulator", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Compare FCFS, SJF, and EFT across a generated 500-task workload.",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        top = ttk.Frame(outer, style="App.TFrame")
        top.pack(fill="x", pady=(0, 14))

        controls = ttk.Frame(top, style="Card.TFrame", padding=16)
        controls.pack(side="left", fill="y", padx=(0, 12))
        ttk.Label(controls, text="Simulation Controls", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        ttk.Label(controls, text="Tasks").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(controls, textvariable=self.task_count_var, width=10, state="readonly").grid(row=1, column=1, sticky="ew", pady=4, padx=(10, 0))

        ttk.Label(controls, text="VMs").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Spinbox(controls, from_=1, to=20, textvariable=self.vm_count_var, width=8).grid(row=2, column=1, sticky="ew", pady=4, padx=(10, 0))

        ttk.Label(controls, text="Focus").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Combobox(
            controls,
            textvariable=self.selected_algorithm_var,
            values=("FCFS", "SJF", "EFT"),
            width=10,
            state="readonly",
        ).grid(row=3, column=1, sticky="ew", pady=4, padx=(10, 0))

        button_row = ttk.Frame(controls, style="Card.TFrame")
        button_row.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ttk.Button(button_row, text="Run FCFS", style="Action.TButton", command=lambda: self.run_simulation("FCFS")).grid(row=0, column=0, padx=(0, 8), pady=4)
        ttk.Button(button_row, text="Run SJF", style="Action.TButton", command=lambda: self.run_simulation("SJF")).grid(row=0, column=1, padx=(0, 8), pady=4)
        ttk.Button(button_row, text="Run EFT", style="Action.TButton", command=lambda: self.run_simulation("EFT")).grid(row=0, column=2, pady=4)

        summary = ttk.Frame(top, style="Card.TFrame", padding=16)
        summary.pack(side="left", fill="both", expand=True)
        ttk.Label(summary, text="Selected Run Summary", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(summary, textvariable=self.summary_text, style="Metric.TLabel", justify="left").pack(anchor="w", pady=(10, 0))

        body = ttk.Frame(outer, style="App.TFrame")
        body.pack(fill="both", expand=True)

        table_card = ttk.Frame(body, style="Card.TFrame", padding=14)
        table_card.pack(side="left", fill="both", expand=True, padx=(0, 12))
        ttk.Label(table_card, text="Comparison Table", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 10))

        columns = ("algorithm", "makespan", "throughput", "utilization", "waiting")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", height=12)
        headings = {
            "algorithm": "Algorithm",
            "makespan": "Makespan",
            "throughput": "Throughput",
            "utilization": "Avg Utilization",
            "waiting": "Avg Waiting",
        }
        widths = {"algorithm": 100, "makespan": 120, "throughput": 120, "utilization": 150, "waiting": 120}
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="center")
        self.tree.pack(fill="both", expand=True)

        status_card = ttk.Frame(body, style="Card.TFrame", padding=14)
        status_card.pack(side="left", fill="y")
        ttk.Label(status_card, text="Status", style="CardTitle.TLabel").pack(anchor="w")
        self.status_label = ttk.Label(status_card, text="Waiting for input.", style="Metric.TLabel", wraplength=260, justify="left")
        self.status_label.pack(anchor="w", pady=(10, 0))

    def _build_vms(self) -> list:
        return self.scheduler.build_vms(
            count=self.vm_count_var.get(),
            min_mips=500,
            max_mips=2000,
        )

    def _load_tasks(self):
        tasks = load_tasks_from_csv()
        if not tasks:
            tasks = generate_tasks_csv()
        return tasks

    def run_simulation(self, selected_algorithm: str) -> None:
        try:
            self.status_label.configure(text="Running simulation...")
            self.root.update_idletasks()

            tasks = self._load_tasks()
            vms = self._build_vms()
            results = self.scheduler.run_all(tasks, vms)
            self.scheduler.save_results_csv(results)

            self._refresh_table(results)
            selected = next(result for result in results if result.algorithm == selected_algorithm)
            self.summary_text.set(
                f"Algorithm: {selected.algorithm}\n"
                f"Makespan: {selected.metrics['makespan']:.2f}\n"
                f"Throughput: {selected.metrics['throughput']:.4f}\n"
                f"Average Utilization: {selected.metrics['average_utilization']:.2f}\n"
                f"Average Waiting Time: {selected.metrics['average_waiting_time']:.2f}"
            )
            self.status_label.configure(text=f"Simulation complete. Results saved to {OUTPUT_CSV.resolve()}")
            self.plotter.show_results_window(self.root, results, selected_algorithm)
        except Exception as exc:
            messagebox.showerror("Simulation Error", str(exc))
            self.status_label.configure(text=f"Error: {exc}")

    def _refresh_table(self, results) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for result in results:
            self.tree.insert(
                "",
                "end",
                values=(
                    result.algorithm,
                    f"{result.metrics['makespan']:.2f}",
                    f"{result.metrics['throughput']:.4f}",
                    f"{result.metrics['average_utilization']:.2f}",
                    f"{result.metrics['average_waiting_time']:.2f}",
                ),
            )

    def start(self) -> None:
        self.root.mainloop()


def main() -> None:
    root = tk.Tk()
    app = SchedulerApp(root)
    app.start()


if __name__ == "__main__":
    main()
