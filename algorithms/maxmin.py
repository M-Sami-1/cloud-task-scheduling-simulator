from __future__ import annotations

from models.assignment import Assignment
from models.task import Task
from models.vm import VM


def schedule_maxmin(tasks: list[Task], vms: list[VM]) -> tuple[list[Assignment], list[Task], list[VM]]:
    ordered_tasks = sorted(tasks, key=lambda task: (-task.length, task.arrival_time, task.id))
    working_vms = [vm.clone() for vm in vms]
    assignments: list[Assignment] = []

    for task in ordered_tasks:
        best_vm = None
        best_start = 0.0
        best_finish = float("inf")
        best_exec = 0.0

        for vm in working_vms:
            start_time = max(task.arrival_time, vm.ready_time)
            execution_time = vm.execution_time(task.length)
            finish_time = start_time + execution_time
            if finish_time < best_finish or (finish_time == best_finish and vm.id < (best_vm.id if best_vm else vm.id)):
                best_vm = vm
                best_start = start_time
                best_finish = finish_time
                best_exec = execution_time

        assert best_vm is not None
        best_vm.ready_time = best_finish
        best_vm.busy_time += best_exec
        task.start_time = best_start
        task.finish_time = best_finish
        task.vm_id = best_vm.id
        assignments.append(
            Assignment(
                task_id=task.id,
                vm_id=best_vm.id,
                start_time=best_start,
                finish_time=best_finish,
                execution_time=best_exec,
                waiting_time=task.waiting_time,
            )
        )

    return assignments, ordered_tasks, working_vms

