from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from scheduler.scheduler import ScheduleResult


class Plotter:
    def __init__(self) -> None:
        self.algorithm_colors = {
            "FCFS": "#165DFF",
            "SJF": "#22A559",
            "EFT": "#FF9F1A",
            "Min-Min": "#8B5CF6",
            "Max-Min": "#EF4444",
        }

    def draw_algorithm_metric_chart(self, canvas: tk.Canvas, results: list[ScheduleResult], metric_key: str, y_label: str) -> None:
        canvas.delete("all")
        width = max(canvas.winfo_width(), int(canvas.cget("width")))
        height = max(canvas.winfo_height(), int(canvas.cget("height")))
        margin_left, margin_right, margin_top, margin_bottom = 56, 24, 30, 30
        chart_w = width - margin_left - margin_right
        chart_h = height - margin_top - margin_bottom

        values = [float(result.metrics[metric_key]) for result in results]
        labels = [result.algorithm for result in results]
        max_value = max(values) if values else 1.0
        if max_value <= 0:
            max_value = 1.0

        self._draw_panel_axes(canvas, margin_left, margin_top, chart_w, chart_h, y_label)

        point_positions: list[tuple[float, float]] = []
        x_step = chart_w / max(len(values), 1)
        for index, (label, value) in enumerate(zip(labels, values)):
            x = margin_left + (index + 0.5) * x_step
            y = margin_top + chart_h - ((value / max_value) * (chart_h - 18))
            point_positions.append((x, y))

        if len(point_positions) > 1:
            flat_points = [coordinate for point in point_positions for coordinate in point]
            canvas.create_line(*flat_points, fill="#9db8ff", width=3, smooth=True)

        for (x, y), label, value in zip(point_positions, labels, values):
            color = self.algorithm_colors.get(label, "#2563eb")
            canvas.create_oval(x - 6, y - 6, x + 6, y + 6, fill=color, outline="white", width=2)
            canvas.create_text(
                x,
                y - 14,
                text=f"{value:.3f}" if metric_key != "makespan" else f"{value:.1f}",
                fill="#111827",
                font=("Segoe UI", 8, "bold"),
            )

        legend_x = margin_left + 8
        for index, label in enumerate(labels):
            color = self.algorithm_colors.get(label, "#2563eb")
            item_x = legend_x + index * 96
            canvas.create_rectangle(item_x, 6, item_x + 16, 16, fill=color, outline=color)
            canvas.create_text(item_x + 22, 11, text=label, anchor="w", fill="#374151", font=("Segoe UI", 9, "bold"))

    def draw_vm_utilization_chart(self, canvas: tk.Canvas, result: ScheduleResult) -> None:
        canvas.delete("all")
        width = max(canvas.winfo_width(), int(canvas.cget("width")))
        height = max(canvas.winfo_height(), int(canvas.cget("height")))
        margin_left, margin_right, margin_top, margin_bottom = 58, 18, 34, 48
        chart_w = width - margin_left - margin_right
        chart_h = height - margin_top - margin_bottom

        utilization = result.metrics["vm_utilization"]
        vm_ids = list(utilization.keys())
        values = [float(utilization[vm_id]) for vm_id in vm_ids]

        if not values:
            canvas.create_text(
                width / 2,
                height / 2,
                text="No VM utilization data available",
                fill="#64748b",
                font=("Segoe UI", 10, "bold"),
            )
            return

        max_value = max(values) if values else 1.0
        max_value = max(max_value, 1.0)

        canvas.create_text(
            margin_left,
            10,
            text=f"Algorithm: {result.algorithm}",
            anchor="w",
            fill="#0f172a",
            font=("Segoe UI Semibold", 11),
        )
        self._draw_panel_axes(canvas, margin_left, margin_top, chart_w, chart_h, "Util.")

        bar_space = chart_w / max(len(values), 1)
        bar_width = bar_space * 0.55
        for index, (vm_id, value) in enumerate(zip(vm_ids, values)):
            x_center = margin_left + (index + 0.5) * bar_space
            bar_height = (value / max_value) * (chart_h - 18)
            x0 = x_center - bar_width / 2
            y0 = margin_top + chart_h - bar_height
            x1 = x_center + bar_width / 2
            y1 = margin_top + chart_h
            canvas.create_rectangle(x0, y0, x1, y1, fill="#2f7cf6", outline="#1b4db2")
            canvas.create_text(
                x_center,
                y0 - 10,
                text=f"{value:.3f}",
                fill="#111827",
                font=("Segoe UI", 8, "bold"),
            )
            canvas.create_text(x_center, margin_top + chart_h + 11, text=vm_id, fill="#374151", font=("Segoe UI", 8, "bold"))

    def show_result_window(self, parent: tk.Tk | tk.Toplevel, result: ScheduleResult) -> tk.Toplevel:
        window = tk.Toplevel(parent)
        window.title(f"{result.algorithm} - Detailed View")
        window.geometry("1500x940")
        window.configure(bg="#eef3fb")

        canvas = tk.Canvas(window, bg="#eef3fb", highlightthickness=0)
        scrollbar = ttk.Scrollbar(window, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg="#eef3fb")
        frame.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        outer = tk.Frame(frame, bg="#eef3fb")
        outer.pack(fill="both", expand=True, padx=18, pady=18)

        header = tk.Frame(outer, bg="#ffffff", highlightthickness=1, highlightbackground="#dce5f3")
        header.pack(fill="x", pady=(0, 16))
        inner = tk.Frame(header, bg="#ffffff", padx=18, pady=16)
        inner.pack(fill="both", expand=True)

        tk.Label(inner, text=f"{result.algorithm} - Detailed View", bg="#ffffff", fg="#0f172a", font=("Segoe UI Semibold", 18)).pack(anchor="w")
        tk.Label(
            inner,
            text="Task assignments, VM usage, and execution timeline for the selected scheduler.",
            bg="#ffffff",
            fg="#64748b",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 0))

        metrics = tk.Frame(outer, bg="#eef3fb")
        metrics.pack(fill="x", pady=(0, 14))
        metric_cards = [
            ("Makespan", f"{result.metrics['makespan']:.3f}"),
            ("Throughput", f"{result.metrics['throughput']:.4f}"),
            ("Avg Utilization", f"{result.metrics['average_utilization']:.3f}"),
            ("Avg Waiting", f"{result.metrics['average_waiting_time']:.3f}"),
        ]
        for label, value in metric_cards:
            card = tk.Frame(metrics, bg="#ffffff", highlightthickness=1, highlightbackground="#dce5f3")
            card.pack(side="left", fill="x", expand=True, padx=(0, 12))
            tk.Label(card, text=label, bg="#ffffff", fg="#64748b", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14, pady=(12, 2))
            tk.Label(card, text=value, bg="#ffffff", fg="#0f172a", font=("Segoe UI Semibold", 16)).pack(anchor="w", padx=14, pady=(0, 12))

        gantt_card = tk.Frame(outer, bg="#ffffff", highlightthickness=1, highlightbackground="#dce5f3")
        gantt_card.pack(fill="x", pady=(0, 16))
        tk.Label(gantt_card, text="Execution Timeline", bg="#ffffff", fg="#0f172a", font=("Segoe UI Semibold", 12)).pack(anchor="w", padx=16, pady=(14, 8))
        gantt_canvas = tk.Canvas(gantt_card, width=1040, height=360, bg="#ffffff", highlightthickness=0)
        gantt_canvas.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.draw_gantt_chart(gantt_canvas, result)

        table_card = tk.Frame(outer, bg="#ffffff", highlightthickness=1, highlightbackground="#dce5f3")
        table_card.pack(fill="both", expand=True)
        tk.Label(table_card, text="Task Schedule", bg="#ffffff", fg="#0f172a", font=("Segoe UI Semibold", 12)).pack(anchor="w", padx=16, pady=(14, 8))

        table_canvas = tk.Canvas(table_card, bg="#ffffff", highlightthickness=0, height=260)
        table_scroll = ttk.Scrollbar(table_card, orient="vertical", command=table_canvas.yview)
        table_frame = tk.Frame(table_canvas, bg="#ffffff")
        table_frame.bind("<Configure>", lambda _event: table_canvas.configure(scrollregion=table_canvas.bbox("all")))
        table_canvas.create_window((0, 0), window=table_frame, anchor="nw")
        table_canvas.configure(yscrollcommand=table_scroll.set)
        table_canvas.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=(0, 12))
        table_scroll.pack(side="right", fill="y", pady=(0, 12))

        headers = ["Task", "VM", "Start", "Finish", "Wait"]
        for col, text in enumerate(headers):
            tk.Label(table_frame, text=text, bg="#f8fafc", fg="#334155", font=("Segoe UI", 9, "bold"), width=16, pady=8).grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

        for row_index, assignment in enumerate(result.assignments, start=1):
            bg = "#ffffff" if row_index % 2 else "#f8fafc"
            values = [
                assignment.task_id,
                assignment.vm_id,
                f"{assignment.start_time:.2f}",
                f"{assignment.finish_time:.2f}",
                f"{assignment.waiting_time:.2f}",
            ]
            for col, value in enumerate(values):
                tk.Label(table_frame, text=value, bg=bg, fg="#0f172a", font=("Segoe UI", 9), width=16, pady=7).grid(row=row_index, column=col, sticky="nsew", padx=1, pady=1)

        return window

    def show_results_window(self, parent: tk.Tk | tk.Toplevel, results: list[ScheduleResult], selected_algorithm: str) -> tk.Toplevel:
        selected = next((result for result in results if result.algorithm == selected_algorithm), results[0])
        window = tk.Toplevel(parent)
        window.title("Simulation Results")
        window.geometry("1920x1040")
        window.configure(bg="#eef3fb")

        wrapper = tk.Frame(window, bg="#eef3fb")
        wrapper.pack(fill="both", expand=True, padx=18, pady=18)

        title = tk.Label(wrapper, text="Performance Charts", bg="#eef3fb", fg="#0f172a", font=("Segoe UI Semibold", 17))
        title.pack(anchor="w", pady=(0, 12))

        for heading, key, label in (
            ("Makespan Comparison", "makespan", "Makespan (s)"),
            ("Throughput Comparison", "throughput", "Throughput"),
            ("VM Utilization Snapshot", "utilization", "Util."),
        ):
            card = tk.Frame(wrapper, bg="#ffffff", highlightthickness=1, highlightbackground="#dce5f3")
            card.pack(fill="x", pady=(0, 14))
            tk.Label(card, text=heading, bg="#ffffff", fg="#111827", font=("Segoe UI Semibold", 12)).pack(anchor="w", padx=16, pady=(12, 8))
            canvas = tk.Canvas(card, width=1820, height=300 if key != "utilization" else 380, bg="#ffffff", highlightthickness=0)
            canvas.pack(fill="both", expand=True, padx=12, pady=(0, 12))
            if key == "makespan":
                self.draw_algorithm_metric_chart(canvas, results, "makespan", label)
            elif key == "throughput":
                self.draw_algorithm_metric_chart(canvas, results, "throughput", label)
            else:
                self.draw_vm_utilization_chart(canvas, selected)

        tk.Button(
            wrapper,
            text=f"Open {selected.algorithm} Timeline",
            font=("Segoe UI", 10, "bold"),
            bg="#1673ff",
            fg="#ffffff",
            activebackground="#0d62de",
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            command=lambda: self.show_timeline_window(window, selected),
        ).pack(anchor="e")

        return window

    def show_vm_utilization_window(self, parent: tk.Tk | tk.Toplevel, result: ScheduleResult) -> tk.Toplevel:
        window = tk.Toplevel(parent)
        window.title(f"VM Utilization Snapshot - {result.algorithm}")
        window.geometry("1700x760")
        window.configure(bg="#eef3fb")

        outer = tk.Frame(window, bg="#eef3fb")
        outer.pack(fill="both", expand=True, padx=18, pady=18)

        header = tk.Frame(outer, bg="#ffffff", highlightthickness=1, highlightbackground="#dce5f3")
        header.pack(fill="x", pady=(0, 14))
        inner = tk.Frame(header, bg="#ffffff", padx=18, pady=14)
        inner.pack(fill="both", expand=True)

        tk.Label(inner, text=f"VM Utilization Snapshot - {result.algorithm}", bg="#ffffff", fg="#0f172a", font=("Segoe UI Semibold", 18)).pack(anchor="w")
        tk.Label(
            inner,
            text="Complete utilization view for every VM in the selected scheduling result.",
            bg="#ffffff",
            fg="#64748b",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 0))

        card = tk.Frame(outer, bg="#ffffff", highlightthickness=1, highlightbackground="#dce5f3")
        card.pack(fill="both", expand=True)
        tk.Label(card, text="Complete VM Utilization Chart", bg="#ffffff", fg="#0f172a", font=("Segoe UI Semibold", 12)).pack(anchor="w", padx=16, pady=(12, 8))

        canvas = tk.Canvas(card, width=1620, height=560, bg="#ffffff", highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.draw_vm_utilization_chart(canvas, result)

        return window

    def show_timeline_window(self, parent: tk.Tk | tk.Toplevel, result: ScheduleResult) -> tk.Toplevel:
        window = tk.Toplevel(parent)
        window.title(f"Execution Timeline - {result.algorithm}")
        window.geometry("1760x680")
        window.configure(bg="#eef3fb")

        card = tk.Frame(window, bg="#ffffff", highlightthickness=1, highlightbackground="#dce5f3")
        card.pack(fill="both", expand=True, padx=18, pady=18)

        header = tk.Frame(card, bg="#ffffff", padx=16, pady=14)
        header.pack(fill="x")
        ttk.Label(header, text=f"Gantt Timeline - {result.algorithm}", style="CardTitle.TLabel").pack(side="left")

        canvas = tk.Canvas(card, bg="#ffffff", highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.draw_gantt_chart(canvas, result)
        return window

    def draw_gantt_chart(self, canvas: tk.Canvas, result: ScheduleResult) -> None:
        canvas.delete("all")
        width = max(canvas.winfo_width(), int(canvas.cget("width")) or 1080)
        height = max(canvas.winfo_height(), int(canvas.cget("height")) or 460)
        margin_left, margin_right, margin_top, margin_bottom = 90, 30, 28, 36
        chart_w = width - margin_left - margin_right
        chart_h = height - margin_top - margin_bottom
        vm_ids = [vm.id for vm in result.vms]
        vm_index = {vm_id: idx for idx, vm_id in enumerate(vm_ids)}
        row_height = chart_h / max(len(vm_ids), 1)
        makespan = max((assignment.finish_time for assignment in result.assignments), default=1.0)
        if makespan <= 0:
            makespan = 1.0

        canvas.create_line(margin_left, margin_top, margin_left, margin_top + chart_h, fill="#94a3b8", width=1)
        canvas.create_line(margin_left, margin_top + chart_h, margin_left + chart_w, margin_top + chart_h, fill="#94a3b8", width=1)
        canvas.create_text(margin_left, 8, text="Execution Timeline", anchor="w", fill="#111827", font=("Segoe UI", 12, "bold"))

        for vm_id, index in vm_index.items():
            y_mid = margin_top + index * row_height + row_height / 2
            canvas.create_text(50, y_mid, text=vm_id, fill="#111827", font=("Segoe UI", 10, "bold"))
            canvas.create_line(margin_left, y_mid + row_height / 4, margin_left + chart_w, y_mid + row_height / 4, fill="#eef2f7")

        for index, assignment in enumerate(result.assignments):
            y_index = vm_index[assignment.vm_id]
            y_top = margin_top + y_index * row_height + 8
            y_bottom = y_top + max(18, row_height * 0.42)
            x0 = margin_left + (assignment.start_time / makespan) * chart_w
            x1 = margin_left + (assignment.finish_time / makespan) * chart_w
            color = list(self.algorithm_colors.values())[index % len(self.algorithm_colors)]
            canvas.create_rectangle(x0, y_top, x1, y_bottom, fill=color, outline="")
            if (x1 - x0) > 38:
                canvas.create_text((x0 + x1) / 2, (y_top + y_bottom) / 2, text=assignment.task_id, fill="white", font=("Segoe UI", 8, "bold"))

    def _draw_panel_axes(self, canvas: tk.Canvas, left: int, top: int, chart_w: int, chart_h: int, y_label: str) -> None:
        canvas.create_rectangle(0, 0, int(canvas.cget("width")), int(canvas.cget("height")), fill="#ffffff", outline="")
        for ratio in (0.0, 0.25, 0.5, 0.75, 1.0):
            y = top + chart_h - (ratio * chart_h)
            canvas.create_line(left, y, left + chart_w, y, fill="#edf2f7")
        canvas.create_line(left, top, left, top + chart_h, fill="#94a3b8", width=1)
        canvas.create_line(left, top + chart_h, left + chart_w, top + chart_h, fill="#94a3b8", width=1)
        canvas.create_text(18, top + chart_h / 2, text=y_label, fill="#6b7280", angle=90, font=("Segoe UI", 9, "bold"))
