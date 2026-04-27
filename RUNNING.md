# How To Run The Project

This file explains the fastest way to run the Cloud Task Scheduling Simulator.

## 1. Open The Project Folder

Open a terminal in:

```text
C:\Users\User\Desktop\Cloud Computing Task Scheduling Simulator
```

## 2. Check Python

Make sure Python is installed:

```bash
python --version
```

If Python is installed, continue.

## 3. Run In CLI Mode

Use this command:

```bash
python main.py
```

What this does:

- loads or generates the 500-task dataset
- creates the virtual machines
- runs FCFS, SJF, and EFT
- calculates performance metrics
- saves results to `results/output.csv`
- opens the chart window

## 4. Run In GUI Mode

Use this command:

```bash
python gui/app.py
```

What this does:

- opens the Tkinter interface
- lets you run FCFS, SJF, or EFT with buttons
- shows the metrics in the app
- opens charts and the execution timeline

## 5. Output Files

After running the simulator, these files are used:

- `dataset/tasks.csv`
- `results/output.csv`

## 6. Important Notes

- The dataset contains 500 tasks.
- If `dataset/tasks.csv` is missing, the project will generate it automatically.
- The GUI needs a Python installation that includes `tkinter`.

## 7. If Something Does Not Work

If `python` is not recognized:

```bash
py main.py
```

or

```bash
py gui/app.py
```

If the GUI does not open, make sure `tkinter` is available in your Python installation.

