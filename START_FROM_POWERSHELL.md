# Run From Windows PowerShell

## 1. Open PowerShell

Open Windows PowerShell in the project folder:

```powershell
cd "C:\Users\User\Desktop\Cloud Computing Task Scheduling Simulator"
```

## 2. Run The Batch Benchmark

```powershell
python main.py
```

## 3. Run A Single Experiment

```powershell
python main.py --task-count 500
```

## 4. Open The GUI

```powershell
python gui/app.py
```

## 5. Use A Custom GoCJ CSV

```powershell
python main.py --task-count 1000 --dataset "C:\path\to\GoCJ_Dataset_1000.csv"
```
