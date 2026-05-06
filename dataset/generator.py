from __future__ import annotations

import csv
import random
from pathlib import Path

from config import DEFAULT_TASK_COUNT, TASKS_CSV, TaskConfig
from models.task import Task


_TASK_ID_COLUMNS = ("id", "task_id", "job_id", "cloudlet_id")
_LENGTH_COLUMNS = ("length", "job_length", "task_length", "mi", "cloudlet_length")
_ARRIVAL_COLUMNS = ("arrival_time", "arrival", "submit_time", "a_time")


def _extract_first(row: dict[str, str], candidates: tuple[str, ...], *, default: str = "") -> str:
    for key in candidates:
        value = row.get(key)
        if value not in (None, ""):
            return str(value)
    return default


def _coerce_float(value: str | float | int | None, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_tasks(tasks: list[Task], count: int | None = None) -> list[Task]:
    if count is None:
        return tasks
    if count <= 0:
        raise ValueError("Task count must be greater than zero.")
    if len(tasks) >= count:
        return [task.clone() for task in tasks[:count]]

    normalized = [task.clone() for task in tasks]
    index = 0
    while len(normalized) < count:
        source = tasks[index % len(tasks)]
        copy_index = len(normalized) + 1
        normalized.append(
            Task(
                id=f"T{copy_index:04d}",
                length=source.length,
                arrival_time=source.arrival_time,
            )
        )
        index += 1
    return normalized


def generate_tasks(count: int, *, min_length: int, max_length: int, min_arrival: int, max_arrival: int, seed: int) -> list[Task]:
    if count <= 0:
        raise ValueError("Task count must be greater than zero.")
    if min_length <= 0 or max_length <= 0:
        raise ValueError("Task lengths must be greater than zero.")
    if min_length > max_length:
        min_length, max_length = max_length, min_length
    if min_arrival > max_arrival:
        min_arrival, max_arrival = max_arrival, min_arrival

    rng = random.Random(seed)
    tasks: list[Task] = []
    for index in range(1, count + 1):
        tasks.append(
            Task(
                id=f"T{index:04d}",
                length=rng.randint(min_length, max_length),
                arrival_time=rng.randint(min_arrival, max_arrival),
            )
        )
    return tasks


def generate_tasks_csv(path: Path = TASKS_CSV, task_config: TaskConfig = TaskConfig()) -> list[Task]:
    path.parent.mkdir(parents=True, exist_ok=True)
    tasks = generate_tasks(
        task_config.count,
        min_length=task_config.min_length,
        max_length=task_config.max_length,
        min_arrival=task_config.min_arrival,
        max_arrival=task_config.max_arrival,
        seed=task_config.seed,
    )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["id", "length", "arrival_time"])
        for task in tasks:
            writer.writerow([task.id, task.length, task.arrival_time])
    return tasks


def load_tasks_from_csv(path: Path = TASKS_CSV, count: int | None = None) -> list[Task]:
    if not path.exists():
        return generate_tasks_csv(path, TaskConfig(count=count or DEFAULT_TASK_COUNT))

    tasks: list[Task] = []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            task_id = _extract_first(row, _TASK_ID_COLUMNS)
            if not task_id:
                task_id = f"T{len(tasks) + 1:04d}"
            length = _coerce_float(_extract_first(row, _LENGTH_COLUMNS), default=0.0)
            arrival_time = _coerce_float(_extract_first(row, _ARRIVAL_COLUMNS), default=float(len(tasks)))
            tasks.append(
                Task(
                    id=task_id,
                    length=length,
                    arrival_time=arrival_time,
                )
            )
    if not tasks:
        return generate_tasks_csv(path, TaskConfig(count=count or DEFAULT_TASK_COUNT))
    return _normalize_tasks(tasks, count)


def load_experiment_tasks(task_count: int, path: Path | None = None) -> list[Task]:
    source = path or TASKS_CSV
    if source.exists():
        tasks = load_tasks_from_csv(source, count=task_count)
    else:
        tasks = generate_tasks_csv(source, TaskConfig(count=max(task_count, DEFAULT_TASK_COUNT)))
        tasks = _normalize_tasks(tasks, task_count)
    if len(tasks) < task_count:
        tasks = _normalize_tasks(tasks, task_count)
    return tasks
