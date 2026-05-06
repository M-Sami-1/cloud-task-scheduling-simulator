from __future__ import annotations

from algorithms.common import clone_tasks, clone_vms, record_assignment, select_earliest_vm
from models.assignment import Assignment
from models.task import Task
from models.vm import VM


def schedule_fcfs(tasks: list[Task], vms: list[VM]) -> tuple[list[Assignment], list[Task], list[VM]]:
    ordered_tasks = sorted(clone_tasks(tasks), key=lambda task: (task.arrival_time, task.id))
    working_vms = clone_vms(vms)
    assignments: list[Assignment] = []

    for task in ordered_tasks:
        vm = select_earliest_vm(working_vms)
        start_time = max(task.arrival_time, vm.ready_time)
        execution_time = vm.execution_time(task.length)
        finish_time = start_time + execution_time
        assignments.append(record_assignment(task, vm, start_time, finish_time, execution_time))

    return assignments, ordered_tasks, working_vms
