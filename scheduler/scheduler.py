from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import csv

from algorithms.eft import schedule_eft
from algorithms.fcfs import schedule_fcfs
from algorithms.sjf import schedule_sjf
from config import OUTPUT_CSV, TASKS_CSV
from dataset.generator import generate_tasks_csv, load_tasks_from_csv
from metrics.metrics import calculate_metrics
from models.assignment import Assignment
from models.task import Task
from models.vm import VM


@dataclass
class ScheduleResult:
    algorithm: str
    assignments: list[Assignment]
    tasks: list[Task]
    vms: list[VM]
    metrics: dict[str, object]


class Scheduler:
    def __init__(self, algorithm_map: dict[str, object] | None = None) -> None:
        self.algorithm_map = algorithm_map or {
            "FCFS": schedule_fcfs,
            "SJF": schedule_sjf,
            "EFT": schedule_eft,
        }

    def build_vms(self, count: int, min_mips: int, max_mips: int) -> list[VM]:
        if count <= 0:
            raise ValueError("VM count must be greater than zero.")
        if min_mips <= 0 or max_mips <= 0:
            raise ValueError("VM MIPS values must be greater than zero.")
        if min_mips > max_mips:
            min_mips, max_mips = max_mips, min_mips

        span = max_mips - min_mips
        vms: list[VM] = []
        for index in range(1, count + 1):
            if span == 0:
                mips = float(min_mips)
            else:
                ratio = (index - 1) / max(1, count - 1)
                mips = float(round(min_mips + span * ratio))
            vms.append(VM(id=f"VM{index:02d}", mips=mips))
        return vms

    def load_tasks(self, regenerate: bool = False) -> list[Task]:
        if regenerate or not TASKS_CSV.exists():
            return generate_tasks_csv()
        return load_tasks_from_csv()

    def run(self, tasks: list[Task], vms: list[VM], algorithm: str) -> ScheduleResult:
        algorithm_key = algorithm.upper()
        if algorithm_key not in self.algorithm_map:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        task_copies = [Task(id=task.id, length=task.length, arrival_time=task.arrival_time) for task in tasks]
        vm_copies = [vm.clone() for vm in vms]
        schedule_fn = self.algorithm_map[algorithm_key]
        assignments, scheduled_tasks, scheduled_vms = schedule_fn(task_copies, vm_copies)
        metrics = calculate_metrics(assignments, scheduled_vms)
        return ScheduleResult(
            algorithm=algorithm_key,
            assignments=assignments,
            tasks=scheduled_tasks,
            vms=scheduled_vms,
            metrics=metrics,
        )

    def run_all(self, tasks: list[Task], vms: list[VM]) -> list[ScheduleResult]:
        return [self.run(tasks, vms, algorithm) for algorithm in self.algorithm_map]

    def save_results_csv(self, results: list[ScheduleResult], path: Path = OUTPUT_CSV) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    "timestamp",
                    "algorithm",
                    "makespan",
                    "throughput",
                    "average_utilization",
                    "average_waiting_time",
                    "vm_utilization",
                ]
            )
            timestamp = datetime.now().isoformat(timespec="seconds")
            for result in results:
                writer.writerow(
                    [
                        timestamp,
                        result.algorithm,
                        f"{result.metrics['makespan']:.4f}",
                        f"{result.metrics['throughput']:.4f}",
                        f"{result.metrics['average_utilization']:.4f}",
                        f"{result.metrics['average_waiting_time']:.4f}",
                        "; ".join(
                            f"{vm_id}:{util:.4f}" for vm_id, util in result.metrics["vm_utilization"].items()
                        ),
                    ]
                )
