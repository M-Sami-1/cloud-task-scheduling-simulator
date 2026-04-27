from __future__ import annotations

from models.assignment import Assignment
from models.task import Task
from models.vm import VM


def schedule_sjf(tasks: list[Task], vms: list[VM]) -> tuple[list[Assignment], list[Task], list[VM]]:
    ordered_tasks = sorted(tasks, key=lambda task: (task.length, task.arrival_time, task.id))
    working_vms = [vm.clone() for vm in vms]
    assignments: list[Assignment] = []

    for task in ordered_tasks:
        vm = min(working_vms, key=lambda item: (item.ready_time, item.id))
        start_time = max(task.arrival_time, vm.ready_time)
        execution_time = vm.execution_time(task.length)
        finish_time = start_time + execution_time
        vm.ready_time = finish_time
        vm.busy_time += execution_time
        task.start_time = start_time
        task.finish_time = finish_time
        task.vm_id = vm.id
        assignments.append(
            Assignment(
                task_id=task.id,
                vm_id=vm.id,
                start_time=start_time,
                finish_time=finish_time,
                execution_time=execution_time,
                waiting_time=task.waiting_time,
            )
        )

    return assignments, ordered_tasks, working_vms

