from __future__ import annotations

from models.assignment import Assignment
from models.task import Task
from models.vm import VM


def clone_tasks(tasks: list[Task]) -> list[Task]:
    return [task.clone() for task in tasks]


def clone_vms(vms: list[VM]) -> list[VM]:
    return [vm.clone() for vm in vms]


def record_assignment(task: Task, vm: VM, start_time: float, finish_time: float, execution_time: float) -> Assignment:
    task.start_time = start_time
    task.finish_time = finish_time
    task.vm_id = vm.id
    vm.ready_time = finish_time
    vm.busy_time += execution_time
    return Assignment(
        task_id=task.id,
        vm_id=vm.id,
        start_time=start_time,
        finish_time=finish_time,
        execution_time=execution_time,
        waiting_time=task.waiting_time,
    )


def select_earliest_vm(vms: list[VM]) -> VM:
    return min(vms, key=lambda vm: (vm.ready_time, vm.id))


def select_eft_vm(task: Task, vms: list[VM]) -> tuple[VM, float, float, float]:
    best_vm = vms[0]
    best_start = max(task.arrival_time, best_vm.ready_time)
    best_execution = best_vm.execution_time(task.length)
    best_finish = best_start + best_execution

    for vm in vms[1:]:
        start_time = max(task.arrival_time, vm.ready_time)
        execution_time = vm.execution_time(task.length)
        finish_time = start_time + execution_time
        if finish_time < best_finish or (finish_time == best_finish and vm.id < best_vm.id):
            best_vm = vm
            best_start = start_time
            best_execution = execution_time
            best_finish = finish_time

    return best_vm, best_start, best_execution, best_finish
