# Cloud Task Scheduling Simulator

A modular Python project that simulates cloud task scheduling on virtual machines and compares multiple algorithms with metrics, charts, and a Tkinter GUI.

## Features

- Simulates task execution on a configurable set of VMs
- Supports five scheduling algorithms:
  - FCFS
  - SJF
  - EFT
  - Min-Min
  - Max-Min
- Generates a 500-task dataset automatically
- Calculates performance metrics:
  - Makespan
  - Throughput
  - VM utilization
  - Average waiting time
- Saves results to CSV
- Provides a Tkinter dashboard with:
  - run controls
  - comparison table
  - per-algorithm CSV download
  - summary CSV download
  - detailed result view
  - full VM utilization snapshot view
  - execution timeline
- Displays charts with distinct colors for each scheduler

## Project Structure

```text
project/
|-- main.py
|-- config.py
|-- models/
|   |-- task.py
|   |-- vm.py
|   |-- assignment.py
|-- algorithms/
|   |-- fcfs.py
|   |-- sjf.py
|   |-- eft.py
|   |-- minmin.py
|   |-- maxmin.py
|-- scheduler/
|   |-- scheduler.py
|-- dataset/
|   |-- generator.py
|   |-- tasks.csv
|-- metrics/
|   |-- metrics.py
|-- visualization/
|   |-- plotter.py
|-- gui/
|   |-- app.py
|-- results/
|   |-- output.csv
```

## Requirements

- Python 3.12 or newer is recommended
- `tkinter` must be available in your Python installation

## How To Run From PowerShell

### 1. Open PowerShell

Start normal Windows PowerShell.

### 2. Go to the project folder

```powershell
cd "C:\Users\User\Desktop\Cloud Computing Task Scheduling Simulator"
```

### 3. Check Python

```powershell
python --version
```

If that does not work, try:

```powershell
py --version
```

### 4. Run the CLI version

```powershell
python main.py
```

This will:

- load or generate the task dataset
- run the selected scheduling algorithms
- save the summary CSV in `results/output.csv`
- open the results and charts

### 5. Run the GUI version

```powershell
python gui/app.py
```

This opens the dashboard where you can:

- choose the task count
- choose the number of VMs
- select FCFS, SJF, EFT, Min-Min, and Max-Min
- run the simulation
- view the comparison table
- download a summary CSV
- download a CSV for each algorithm
- open a detailed result window
- open a full VM utilization snapshot

## Output Files

- `dataset/tasks.csv` - generated task dataset
- `results/output.csv` - summary results for the latest run
- individual algorithm CSV files - saved when you click the download button in the table

## Metrics

- **Makespan** - total completion time of the workload
- **Throughput** - tasks completed per unit time
- **VM Utilization** - busy time divided by total schedule time for each VM
- **Average Waiting Time** - average wait before execution starts

## Dataset Details

- Number of tasks: 500 by default
- Task length range: 1000 to 10000
- Arrival time range: 0 to 100
- VM count is configurable from the GUI

## Notes

- EFT assigns each task to the VM that finishes it earliest.
- Min-Min and Max-Min are included for comparison in the dashboard.
- The VM utilization chart can also be opened in a full-size view from the GUI.

## Troubleshooting

- If the GUI does not open, make sure `tkinter` is installed with Python.
- If Python is not recognized, use `py main.py` or `py gui/app.py`.
- If `dataset/tasks.csv` is missing, the app regenerates it automatically.

## Screenshots

The dashboard includes:

- makespan comparison
- throughput comparison
- VM utilization snapshot
- detailed per-algorithm results
- complete VM utilization view

