# Cloud Task Scheduling Simulator Documentation

## 1. System Overview

This project simulates basic task scheduling in a cloud datacenter and compares three scheduling policies:

- First Come First Served (`FCFS`)
- Shortest Job First (`SJF`)
- Earliest Finish Time First (`EFT`)

The simulator is implemented in Python and provides both:

- a command-line experiment runner
- a Tkinter graphical user interface

## 2. System Design

The codebase is organized into the following layers:

- `models/` contains the task, VM, assignment, and datacenter data classes.
- `dataset/` loads task workloads from CSV files and provides a deterministic fallback generator.
- `algorithms/` implements the scheduling policies.
- `scheduler/` orchestrates experiments, metrics, and CSV exports.
- `metrics/` computes makespan, throughput, and VM utilization.
- `visualization/` renders charts and detailed execution timelines.
- `gui/` provides the interactive dashboard.

## 3. Datacenter Model

The simulator uses a fixed 10-VM datacenter.

Each VM is represented as a heterogeneous instance profile with:

- VM identifier
- name
- MIPS
- RAM
- bandwidth
- processing elements

The datacenter is built from 10 VM templates so the experiment remains reproducible and aligned with the assignment requirement.

## 4. Dataset Handling

The workload loader accepts GoCJ-compatible CSV files.

Supported columns include:

- `id`, `task_id`, `job_id`, or `cloudlet_id`
- `length`, `job_length`, `task_length`, `mi`, or `cloudlet_length`
- `arrival_time`, `arrival`, `submit_time`, or `a_time`

If a requested task count is larger than the number of rows available in a local CSV, the loader repeats the workload deterministically so experiments can still run for 100 to 1000 tasks.

## 5. Scheduling Algorithms

### FCFS

Tasks are scheduled in arrival order. Each task is assigned to the VM that becomes available first.

### SJF

Tasks are ordered by shortest execution length first, then by arrival time and task ID. Each task is assigned to the earliest available VM.

### EFT

For each task, the scheduler evaluates all VMs and chooses the placement that yields the earliest completion time.

## 6. Evaluation Metrics

The simulator computes:

- `makespan`: total time to complete the workload
- `throughput`: tasks completed per unit time
- `resource_utilization`: average VM utilization across the datacenter
- `average_waiting_time`: average time spent waiting before execution

Per-VM utilization is also exported for analysis.

## 7. Experimental Setup

Default experiment sizes:

- 100 tasks
- 200 tasks
- 300 tasks
- 400 tasks
- 500 tasks
- 600 tasks
- 700 tasks
- 800 tasks
- 900 tasks
- 1000 tasks

Outputs are saved to:

- `results/output.csv`
- `results/batch_summary.csv`
- `results/batch_details.csv`

## 8. How To Run

### Batch experiment

```powershell
python main.py
```

### Single experiment

```powershell
python main.py --task-count 500
```

### GUI

```powershell
python gui/app.py
```

### Custom dataset

```powershell
python main.py --task-count 1000 --dataset "C:\path\to\GoCJ_Dataset_1000.csv"
```

## 9. Reporting

The scheduler writes both summary and detailed CSV files so the results can be analyzed later in spreadsheet tools or imported into a report.

## 10. Notes

- The project is designed to run even when the official GoCJ CSV is not present locally.
- When no external dataset is supplied, the simulator uses the bundled compatible dataset file.
- The GUI is intended for interactive comparison, while `main.py` is intended for reproducible experiment runs.
