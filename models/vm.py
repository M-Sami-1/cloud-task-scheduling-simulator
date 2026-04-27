from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class VM:
    id: str
    mips: float
    ready_time: float = field(default=0.0)
    busy_time: float = field(default=0.0)

    def clone(self) -> "VM":
        return VM(id=self.id, mips=self.mips, ready_time=self.ready_time, busy_time=self.busy_time)

    def execution_time(self, task_length: float) -> float:
        return task_length / self.mips if self.mips else float("inf")

