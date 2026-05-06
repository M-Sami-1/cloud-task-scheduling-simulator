from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class VM:
    id: str
    mips: float
    name: str = field(default="")
    ram_mb: int = field(default=0)
    bandwidth_mbps: int = field(default=0)
    pes: int = field(default=1)
    ready_time: float = field(default=0.0)
    busy_time: float = field(default=0.0)

    def clone(self) -> "VM":
        return VM(
            id=self.id,
            mips=self.mips,
            name=self.name,
            ram_mb=self.ram_mb,
            bandwidth_mbps=self.bandwidth_mbps,
            pes=self.pes,
            ready_time=self.ready_time,
            busy_time=self.busy_time,
        )

    def execution_time(self, task_length: float) -> float:
        return task_length / self.mips if self.mips else float("inf")

    def utilization(self, makespan: float) -> float:
        return self.busy_time / makespan if makespan else 0.0
