# Cloud Task Scheduling Simulator

A modular Python simulator for cloud task scheduling on virtual machines.

## Features

- Simulates task execution on VMs
- Implements three scheduling algorithms:
  - FCFS
  - SJF
  - EFT
- Generates a 500-task dataset automatically
- Calculates performance metrics:
  - Makespan
  - Throughput
  - VM utilization
- Saves run results to CSV
- Provides a Tkinter GUI
- Displays comparison charts and a Gantt-style execution timeline

## Project Structure

```text
project/
├── main.py
├── config.py
├── models/
│   ├── task.py
│   ├── vm.py
│   └── assignment.py
├── algorithms/
│   ├── fcfs.py
│   ├── sjf.py
│   └── eft.py
├── scheduler/
│   └── scheduler.py
├── dataset/
│   ├── generator.py
│   └── tasks.csv
├── metrics/
│   └── metrics.py
├── visualization/
│   └── plotter.py
├── gui/
│   └── app.py
└── results/
    ├── output.csv
    └── plots/
```

## Requirements

- Python 3.12+ recommended
- `tkinter` available in your Python installation

## How To Run

### CLI Mode

```bash
python main.py
```

This will:

- load or generate the dataset
- run FCFS, SJF, and EFT
- save metrics to `results/output.csv`
- open the chart viewer

### GUI Mode

```bash
python gui/app.py
```

This opens the Tkinter application with:

- buttons for FCFS, SJF, and EFT
- a comparison table
- a simulation summary panel
- chart/timeline display after each run

## Output Files

- `dataset/tasks.csv` - generated task dataset
- `results/output.csv` - summary metrics for each algorithm

## Metrics

The simulator reports:

- **Makespan** - total completion time of the workload
- **Throughput** - tasks completed per unit time
- **VM Utilization** - busy time divided by total schedule time for each VM

## Notes

- The simulator creates 500 random tasks with:
  - length between 1000 and 10000
  - arrival time between 0 and 100
- VM count is configurable in the GUI
- The EFT algorithm assigns each task to the VM with the earliest completion time

## Screenshot / Demo

After a run, the app shows:

- makespan comparison
- throughput comparison
- utilization comparison
- Gantt-style execution timeline

## Troubleshooting

- If the GUI does not open, make sure your Python installation includes `tkinter`.
- If you delete `dataset/tasks.csv`, it will be regenerated automatically on the next run.

