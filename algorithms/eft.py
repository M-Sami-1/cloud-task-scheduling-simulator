from __future__ import annotations

from algorithms.common import clone_tasks, clone_vms, record_assignment, select_eft_vm
from models.assignment import Assignment
from models.task import Task
from models.vm import VM


def schedule_eft(tasks: list[Task], vms: list[VM]) -> tuple[list[Assignment], list[Task], list[VM]]:
    ordered_tasks = sorted(clone_tasks(tasks), key=lambda task: (task.arrival_time, task.id))
    working_vms = clone_vms(vms)
    assignments: list[Assignment] = []

    for task in ordered_tasks:
        best_vm, best_start, best_exec, best_finish = select_eft_vm(task, working_vms)
        assignments.append(record_assignment(task, best_vm, best_start, best_finish, best_exec))

    return assignments, ordered_tasks, working_vms
