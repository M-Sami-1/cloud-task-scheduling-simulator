from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    id: str
    length: float
    arrival_time: float
    start_time: float = field(default=0.0)
    finish_time: float = field(default=0.0)
    vm_id: str | None = field(default=None)

    @property
    def waiting_time(self) -> float:
        return max(0.0, self.start_time - self.arrival_time)

    @property
    def turnaround_time(self) -> float:
        return max(0.0, self.finish_time - self.arrival_time)

