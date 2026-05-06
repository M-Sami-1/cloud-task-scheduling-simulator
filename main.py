from __future__ import annotations

import argparse
from pathlib import Path

from config import DEFAULT_EXPERIMENT_COUNTS, OUTPUT_BATCH_CSV, OUTPUT_BATCH_DETAILS_CSV, OUTPUT_CSV, TASKS_CSV, ensure_runtime_paths
from dataset.generator import load_experiment_tasks
from scheduler.scheduler import Scheduler


def format_metrics_row(result) -> str:
    metrics = result.metrics
    utilization = ", ".join(f"{vm_id}: {value:.2f}" for vm_id, value in metrics["vm_utilization"].items())
    return (
        f"{result.algorithm:<5} | "
        f"tasks={len(result.assignments):<4} | "
        f"makespan={metrics['makespan']:.2f} | "
        f"throughput={metrics['throughput']:.4f} | "
        f"util={metrics['resource_utilization']:.2f} | "
        f"wait={metrics['average_waiting_time']:.2f} | "
        f"vm_util={utilization}"
    )


def run_single_experiment(scheduler: Scheduler, task_count: int, dataset_path: Path | None) -> None:
    tasks = load_experiment_tasks(task_count, dataset_path or TASKS_CSV)
    vms = scheduler.build_vms()
    results = scheduler.run_all(tasks, vms)
    scheduler.save_summary_csv(results, OUTPUT_CSV)

    print(f"Task count: {task_count}")
    print(f"Dataset: {(dataset_path or TASKS_CSV).resolve()}")
    for result in results:
        print(format_metrics_row(result))
    print(f"Summary saved to: {OUTPUT_CSV.resolve()}")


def run_batch_experiment(scheduler: Scheduler, task_counts: tuple[int, ...], dataset_path: Path | None) -> None:
    batch_results = scheduler.run_experiment_suite(list(task_counts), source_path=dataset_path or TASKS_CSV)
    scheduler.save_batch_summary_csv(batch_results, OUTPUT_BATCH_CSV)
    scheduler.save_batch_details_csv(batch_results, OUTPUT_BATCH_DETAILS_CSV)

    print("Batch experiment completed.")
    for task_count in task_counts:
        print(f"\nTask count: {task_count}")
        for result in batch_results[task_count]:
            print(format_metrics_row(result))

    print(f"\nBatch summary saved to: {OUTPUT_BATCH_CSV.resolve()}")
    print(f"Batch details saved to: {OUTPUT_BATCH_DETAILS_CSV.resolve()}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cloud task scheduling simulator")
    parser.add_argument(
        "--task-count",
        type=int,
        help="Run a single experiment with the requested number of tasks.",
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        help="Optional path to a GoCJ CSV file or compatible task dataset.",
    )
    return parser.parse_args()


def main() -> None:
    ensure_runtime_paths()
    args = parse_args()
    scheduler = Scheduler()

    if args.task_count is not None:
        run_single_experiment(scheduler, args.task_count, args.dataset)
    else:
        run_batch_experiment(scheduler, DEFAULT_EXPERIMENT_COUNTS, args.dataset)


if __name__ == "__main__":
    main()
