from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Assignment:
    task_id: str
    vm_id: str
    start_time: float
    finish_time: float
    execution_time: float
    waiting_time: float

