from __future__ import annotations

import csv
import random
from pathlib import Path
from typing import Iterable

from config import TASKS_CSV, TaskConfig
from models.task import Task


def generate_tasks(count: int, *, min_length: int, max_length: int, min_arrival: int, max_arrival: int, seed: int) -> list[Task]:
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


def load_tasks_from_csv(path: Path = TASKS_CSV) -> list[Task]:
    if not path.exists():
        return generate_tasks_csv(path)

    tasks: list[Task] = []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            tasks.append(
                Task(
                    id=str(row["id"]),
                    length=float(row["length"]),
                    arrival_time=float(row["arrival_time"]),
                )
            )
    return tasks

