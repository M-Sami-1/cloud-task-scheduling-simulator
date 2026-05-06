from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import csv

from algorithms.eft import schedule_eft
from algorithms.fcfs import schedule_fcfs
from algorithms.sjf import schedule_sjf
from config import DEFAULT_VM_COUNT, OUTPUT_BATCH_CSV, OUTPUT_BATCH_DETAILS_CSV, OUTPUT_CSV, TASKS_CSV
from dataset.generator import load_experiment_tasks
from metrics.metrics import calculate_metrics
from models.assignment import Assignment
from models.datacenter import Datacenter, VMTemplate
from models.task import Task
from models.vm import VM


DEFAULT_VM_TEMPLATES = [
    VMTemplate(name="m5.large-A", mips=3100, ram_mb=8000, bandwidth_mbps=8),
    VMTemplate(name="m5.large-B", mips=3100, ram_mb=8000, bandwidth_mbps=8),
    VMTemplate(name="m5.xlarge-A", mips=6200, ram_mb=16000, bandwidth_mbps=8),
    VMTemplate(name="m5.xlarge-B", mips=6200, ram_mb=16000, bandwidth_mbps=8),
    VMTemplate(name="m5.2xlarge-A", mips=12400, ram_mb=32000, bandwidth_mbps=10),
    VMTemplate(name="m5.2xlarge-B", mips=12400, ram_mb=32000, bandwidth_mbps=10),
    VMTemplate(name="m5.4xlarge-A", mips=24800, ram_mb=64000, bandwidth_mbps=12),
    VMTemplate(name="m5.4xlarge-B", mips=24800, ram_mb=64000, bandwidth_mbps=12),
    VMTemplate(name="m5.8xlarge-A", mips=49600, ram_mb=128000, bandwidth_mbps=20),
    VMTemplate(name="m5.8xlarge-B", mips=49600, ram_mb=128000, bandwidth_mbps=20),
]


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
        self._algorithm_lookup = {name.upper(): name for name in self.algorithm_map}

    def build_datacenter(self) -> Datacenter:
        return Datacenter(name="GoCJ Research Datacenter", templates=list(DEFAULT_VM_TEMPLATES))

    def build_vms(self, count: int | None = None) -> list[VM]:
        if count is not None and count != DEFAULT_VM_COUNT:
            raise ValueError("This project uses a fixed 10-VM datacenter.")
        return self.build_datacenter().build_vms()

    def load_tasks(self, task_count: int, source_path: Path | None = None) -> list[Task]:
        return load_experiment_tasks(task_count, source_path or TASKS_CSV)

    def run(self, tasks: list[Task], vms: list[VM], algorithm: str) -> ScheduleResult:
        algorithm_key = algorithm.upper()
        if algorithm_key not in self._algorithm_lookup:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        algorithm_name = self._algorithm_lookup[algorithm_key]
        task_copies = [task.clone() for task in tasks]
        vm_copies = [vm.clone() for vm in vms]
        schedule_fn = self.algorithm_map[algorithm_name]
        assignments, scheduled_tasks, scheduled_vms = schedule_fn(task_copies, vm_copies)
        metrics = calculate_metrics(assignments, scheduled_vms)
        return ScheduleResult(
            algorithm=algorithm_name,
            assignments=assignments,
            tasks=scheduled_tasks,
            vms=scheduled_vms,
            metrics=metrics,
        )

    def run_all(self, tasks: list[Task], vms: list[VM]) -> list[ScheduleResult]:
        return [self.run(tasks, vms, algorithm) for algorithm in self.algorithm_map]

    def run_experiment_suite(
        self,
        task_counts: list[int] | tuple[int, ...],
        source_path: Path | None = None,
    ) -> dict[int, list[ScheduleResult]]:
        datacenter_vms = self.build_vms()
        results: dict[int, list[ScheduleResult]] = {}
        for task_count in task_counts:
            tasks = self.load_tasks(task_count, source_path=source_path)
            results[task_count] = self.run_all(tasks, datacenter_vms)
        return results

    def save_summary_csv(self, results: list[ScheduleResult], path: Path = OUTPUT_CSV) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    "timestamp",
                    "algorithm",
                    "tasks",
                    "makespan",
                    "throughput",
                    "resource_utilization",
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
                        len(result.assignments),
                        f"{result.metrics['makespan']:.4f}",
                        f"{result.metrics['throughput']:.4f}",
                        f"{result.metrics['resource_utilization']:.4f}",
                        f"{result.metrics['average_waiting_time']:.4f}",
                        "; ".join(
                            f"{vm_id}:{util:.4f}" for vm_id, util in result.metrics["vm_utilization"].items()
                        ),
                    ]
                )

    def save_algorithm_csv(self, result: ScheduleResult, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    "algorithm",
                    "task_id",
                    "vm_id",
                    "arrival_time",
                    "length",
                    "start_time",
                    "finish_time",
                    "execution_time",
                    "waiting_time",
                ]
            )
            tasks_by_id = {task.id: task for task in result.tasks}
            for assignment in result.assignments:
                task = tasks_by_id[assignment.task_id]
                writer.writerow(
                    [
                        result.algorithm,
                        assignment.task_id,
                        assignment.vm_id,
                        f"{task.arrival_time:.4f}",
                        f"{task.length:.4f}",
                        f"{assignment.start_time:.4f}",
                        f"{assignment.finish_time:.4f}",
                        f"{assignment.execution_time:.4f}",
                        f"{assignment.waiting_time:.4f}",
                    ]
                )

    def save_batch_summary_csv(self, batch_results: dict[int, list[ScheduleResult]], path: Path = OUTPUT_BATCH_CSV) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    "task_count",
                    "algorithm",
                    "makespan",
                    "throughput",
                    "resource_utilization",
                    "average_waiting_time",
                    "vm_utilization",
                ]
            )
            for task_count in sorted(batch_results):
                for result in batch_results[task_count]:
                    writer.writerow(
                        [
                            task_count,
                            result.algorithm,
                            f"{result.metrics['makespan']:.4f}",
                            f"{result.metrics['throughput']:.4f}",
                            f"{result.metrics['resource_utilization']:.4f}",
                            f"{result.metrics['average_waiting_time']:.4f}",
                            "; ".join(
                                f"{vm_id}:{util:.4f}" for vm_id, util in result.metrics["vm_utilization"].items()
                            ),
                        ]
                    )

    def save_batch_details_csv(self, batch_results: dict[int, list[ScheduleResult]], path: Path = OUTPUT_BATCH_DETAILS_CSV) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    "task_count",
                    "algorithm",
                    "task_id",
                    "vm_id",
                    "arrival_time",
                    "length",
                    "start_time",
                    "finish_time",
                    "execution_time",
                    "waiting_time",
                ]
            )
            for task_count in sorted(batch_results):
                for result in batch_results[task_count]:
                    tasks_by_id = {task.id: task for task in result.tasks}
                    for assignment in result.assignments:
                        task = tasks_by_id[assignment.task_id]
                        writer.writerow(
                            [
                                task_count,
                                result.algorithm,
                                assignment.task_id,
                                assignment.vm_id,
                                f"{task.arrival_time:.4f}",
                                f"{task.length:.4f}",
                                f"{assignment.start_time:.4f}",
                                f"{assignment.finish_time:.4f}",
                                f"{assignment.execution_time:.4f}",
                                f"{assignment.waiting_time:.4f}",
                            ]
                        )
