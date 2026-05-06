# Cloud Task Scheduling Simulator

Python simulator for evaluating cloud task scheduling on a fixed 10-VM datacenter using:

- FCFS
- SJF
- EFT

It supports:

- GoCJ-compatible CSV inputs
- workload sizes from 100 to 1000 tasks
- makespan, throughput, and resource utilization metrics
- CSV reporting for detailed analysis
- a Tkinter GUI for interactive runs

## Quick Start

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

## Outputs

- `results/output.csv`
- `results/batch_summary.csv`
- `results/batch_details.csv`

## Documentation

See [DOCUMENTATION.md](./DOCUMENTATION.md) for the system design, algorithms, experiment setup, and output format.
