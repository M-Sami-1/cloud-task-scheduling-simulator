from __future__ import annotations

from statistics import mean

from models.assignment import Assignment
from models.vm import VM


def calculate_metrics(assignments: list[Assignment], vms: list[VM]) -> dict[str, object]:
    makespan = max((assignment.finish_time for assignment in assignments), default=0.0)
    throughput = (len(assignments) / makespan) if makespan else 0.0
    vm_utilization = {
        vm.id: (vm.busy_time / makespan if makespan else 0.0)
        for vm in vms
    }
    average_utilization = mean(vm_utilization.values()) if vm_utilization else 0.0
    average_waiting_time = mean([assignment.waiting_time for assignment in assignments]) if assignments else 0.0

    return {
        "makespan": makespan,
        "throughput": throughput,
        "vm_utilization": vm_utilization,
        "average_utilization": average_utilization,
        "average_waiting_time": average_waiting_time,
    }
