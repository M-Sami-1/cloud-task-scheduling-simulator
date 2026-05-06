# How To Run

## Batch Experiment

```powershell
python main.py
```

This runs the default workload sweep from 100 to 1000 tasks and saves:

- `results/batch_summary.csv`
- `results/batch_details.csv`

## Single Experiment

```powershell
python main.py --task-count 500
```

## GUI

```powershell
python gui/app.py
```

## Custom Dataset

```powershell
python main.py --task-count 1000 --dataset "C:\path\to\GoCJ_Dataset_1000.csv"
```

The dataset should be GoCJ-compatible and contain at least a task length column.
