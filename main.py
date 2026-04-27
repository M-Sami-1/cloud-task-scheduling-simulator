from __future__ import annotations

import tkinter as tk

from config import OUTPUT_CSV, TASKS_CSV, enable_dpi_awareness, ensure_runtime_paths

ensure_runtime_paths()
enable_dpi_awareness()

from dataset.generator import load_tasks_from_csv, generate_tasks_csv
from scheduler.scheduler import Scheduler
from visualization.plotter import Plotter


def format_metrics_row(result) -> str:
    metrics = result.metrics
    utilization = ", ".join(f"{vm_id}: {value:.2f}" for vm_id, value in metrics["vm_utilization"].items())
    return (
        f"{result.algorithm:<5} | "
        f"makespan={metrics['makespan']:.2f} | "
        f"throughput={metrics['throughput']:.4f} | "
        f"avg_util={metrics['average_utilization']:.2f} | "
        f"avg_wait={metrics['average_waiting_time']:.2f} | "
        f"vm_util={utilization}"
    )


def main() -> None:
    scheduler = Scheduler()
    plotter = Plotter()

    tasks = load_tasks_from_csv() if TASKS_CSV.exists() else generate_tasks_csv()
    vms = scheduler.build_vms(count=5, min_mips=500, max_mips=2000)

    results = scheduler.run_all(tasks, vms)
    scheduler.save_summary_csv(results, OUTPUT_CSV)

    print("Cloud Task Scheduling Simulator")
    print("=" * 40)
    for result in results:
        print(format_metrics_row(result))
    print("=" * 40)
    print(f"Results saved to: {OUTPUT_CSV.resolve()}")

    root = tk.Tk()
    root.withdraw()
    plotter.show_results_window(root, results, results[0].algorithm)
    root.mainloop()


if __name__ == "__main__":
    main()
