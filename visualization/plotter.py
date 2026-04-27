from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from config import OUTPUT_PLOT_DIR
from scheduler.scheduler import ScheduleResult


@dataclass
class ChartSpec:
    title: str
    labels: list[str]
    values: list[float]
    ylabel: str


class Plotter:
    def __init__(self, output_dir: Path = OUTPUT_PLOT_DIR) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def comparison_specs(self, results: list[ScheduleResult]) -> list[ChartSpec]:
        algorithms = [result.algorithm for result in results]
        return [
            ChartSpec("Makespan Comparison", algorithms, [result.metrics["makespan"] for result in results], "Makespan"),
            ChartSpec("Throughput Comparison", algorithms, [result.metrics["throughput"] for result in results], "Throughput"),
            ChartSpec(
                "Average VM Utilization",
                algorithms,
                [result.metrics["average_utilization"] for result in results],
                "Utilization",
            ),
        ]

    def show_results_window(self, parent: tk.Tk | tk.Toplevel, results: list[ScheduleResult], selected_algorithm: str) -> tk.Toplevel:
        window = tk.Toplevel(parent)
        window.title(f"Simulation Charts - {selected_algorithm}")
        window.geometry("1240x900")
        window.configure(bg="#f4f7fb")

        canvas = tk.Canvas(window, bg="#f4f7fb", highlightthickness=0)
        scrollbar = ttk.Scrollbar(window, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, padding=16)

        scroll_frame.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        title = ttk.Label(
            scroll_frame,
            text="Performance Charts",
            font=("Segoe UI", 18, "bold"),
            background="#f4f7fb",
            foreground="#111827",
        )
        title.grid(row=0, column=0, sticky="w", pady=(0, 12))

        specs = self.comparison_specs(results)
        for index, spec in enumerate(specs, start=1):
            card = ttk.Frame(scroll_frame, padding=12, style="Card.TFrame")
            card.grid(row=index, column=0, sticky="ew", pady=10)
            ttk.Label(card, text=spec.title, style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
            chart = tk.Canvas(card, width=1120, height=320, bg="white", highlightthickness=1, highlightbackground="#d1d5db")
            chart.pack(fill="x", expand=True)
            self._draw_bar_chart(chart, spec)

        selected = next(result for result in results if result.algorithm == selected_algorithm)
        gantt_card = ttk.Frame(scroll_frame, padding=12, style="Card.TFrame")
        gantt_card.grid(row=len(specs) + 1, column=0, sticky="ew", pady=10)
        ttk.Label(gantt_card, text=f"Gantt Chart - {selected.algorithm}", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
        gantt = tk.Canvas(gantt_card, width=1120, height=max(320, 70 * len(selected.vms) + 80), bg="white", highlightthickness=1, highlightbackground="#d1d5db")
        gantt.pack(fill="x", expand=True)
        self._draw_gantt_chart(gantt, selected)

        return window

    def _draw_bar_chart(self, canvas: tk.Canvas, spec: ChartSpec) -> None:
        width = int(canvas["width"])
        height = int(canvas["height"])
        margin_left, margin_right, margin_top, margin_bottom = 90, 30, 35, 60
        chart_w = width - margin_left - margin_right
        chart_h = height - margin_top - margin_bottom
        max_value = max(spec.values) if spec.values else 1
        if max_value <= 0:
            max_value = 1
        colors = ["#355C7D", "#6C5B7B", "#C06C84"]

        canvas.create_text(margin_left, 12, text=spec.title, anchor="w", fill="#111827", font=("Segoe UI", 16, "bold"))
        canvas.create_line(margin_left, margin_top, margin_left, margin_top + chart_h, fill="#111827", width=2)
        canvas.create_line(margin_left, margin_top + chart_h, margin_left + chart_w, margin_top + chart_h, fill="#111827", width=2)
        canvas.create_text(20, margin_top + chart_h / 2, text=spec.ylabel, fill="#111827", angle=90, font=("Segoe UI", 10, "bold"))

        bar_space = chart_w / max(len(spec.values), 1)
        bar_width = bar_space * 0.56
        for index, (label, value) in enumerate(zip(spec.labels, spec.values)):
            x_center = margin_left + (index + 0.5) * bar_space
            bar_height = (value / max_value) * (chart_h - 20)
            x0 = x_center - bar_width / 2
            y0 = margin_top + chart_h - bar_height
            x1 = x_center + bar_width / 2
            y1 = margin_top + chart_h
            canvas.create_rectangle(x0, y0, x1, y1, fill=colors[index % len(colors)], outline="#111827")
            canvas.create_text(x_center, y0 - 10, text=f"{value:.2f}", fill="#111827", font=("Segoe UI", 9, "bold"))
            canvas.create_text(x_center, margin_top + chart_h + 18, text=label, fill="#111827", font=("Segoe UI", 10, "bold"))

    def _draw_gantt_chart(self, canvas: tk.Canvas, result: ScheduleResult) -> None:
        width = int(canvas["width"])
        height = int(canvas["height"])
        margin_left, margin_right, margin_top, margin_bottom = 100, 30, 35, 45
        chart_w = width - margin_left - margin_right
        chart_h = height - margin_top - margin_bottom
        vm_ids = [vm.id for vm in result.vms]
        vm_index = {vm_id: idx for idx, vm_id in enumerate(vm_ids)}
        row_height = chart_h / max(len(vm_ids), 1)
        makespan = max((assignment.finish_time for assignment in result.assignments), default=1)
        if makespan <= 0:
            makespan = 1
        colors = ["#355C7D", "#6C5B7B", "#C06C84", "#F67280", "#99B898", "#F8B195"]

        canvas.create_line(margin_left, margin_top, margin_left, margin_top + chart_h, fill="#111827", width=2)
        canvas.create_line(margin_left, margin_top + chart_h, margin_left + chart_w, margin_top + chart_h, fill="#111827", width=2)
        canvas.create_text(20, margin_top + chart_h / 2, text="VMs", fill="#111827", angle=90, font=("Segoe UI", 10, "bold"))
        canvas.create_text(margin_left, 12, text="Execution Timeline", anchor="w", fill="#111827", font=("Segoe UI", 16, "bold"))

        for vm_id, index in vm_index.items():
            y_mid = margin_top + index * row_height + row_height / 2
            canvas.create_text(55, y_mid, text=vm_id, fill="#111827", font=("Segoe UI", 10, "bold"))
            canvas.create_line(margin_left, y_mid + row_height / 4, margin_left + chart_w, y_mid + row_height / 4, fill="#e5e7eb")

        for index, assignment in enumerate(result.assignments):
            y_index = vm_index[assignment.vm_id]
            y_top = margin_top + y_index * row_height + 8
            y_bottom = y_top + max(20, row_height * 0.45)
            x0 = margin_left + (assignment.start_time / makespan) * chart_w
            x1 = margin_left + (assignment.finish_time / makespan) * chart_w
            color = colors[index % len(colors)]
            canvas.create_rectangle(x0, y_top, x1, y_bottom, fill=color, outline="#111827")
            canvas.create_text((x0 + x1) / 2, (y_top + y_bottom) / 2, text=assignment.task_id, fill="white", font=("Segoe UI", 8, "bold"))

