# Run The Project From Normal PowerShell

This guide starts from zero and shows how to run the project using normal Windows PowerShell.

## Step 1: Open PowerShell

1. Press the `Windows` key.
2. Type `PowerShell`.
3. Open `Windows PowerShell`.

You should now see a blue or dark terminal window.

## Step 2: Go To The Project Folder

Type this command and press `Enter`:

```powershell
cd "C:\Users\User\Desktop\Cloud Computing Task Scheduling Simulator"
```

This moves PowerShell into your project folder.

## Step 3: Check That Python Is Installed

Type:

```powershell
python --version
```

If Python is installed, you will see something like:

```text
Python 3.x.x
```

If `python` does not work, try:

```powershell
py --version
```

## Step 4: Run The Project In CLI Mode

To run the simulator normally, type:

```powershell
python main.py
```

If that does not work, use:

```powershell
py main.py
```

What happens:

- the project loads or generates the task dataset
- it creates virtual machines
- it runs FCFS, SJF, and EFT
- it calculates metrics
- it saves results in `results/output.csv`
- it opens the chart window

## Step 5: Run The Project In GUI Mode

To open the graphical interface, type:

```powershell
python gui/app.py
```

If that does not work, use:

```powershell
py gui/app.py
```

What happens:

- the Tkinter application opens
- you can click `Run FCFS`
- you can click `Run SJF`
- you can click `Run EFT`
- results are shown in the interface
- charts and timeline are displayed

## Step 6: Where The Output Is Saved

After running the project, check these files:

- `dataset/tasks.csv`
- `results/output.csv`

## Step 7: Full Example For CLI

If you want the full command flow from the beginning, type these one by one:

```powershell
cd "C:\Users\User\Desktop\Cloud Computing Task Scheduling Simulator"
python --version
python main.py
```

## Step 8: Full Example For GUI

Type these one by one:

```powershell
cd "C:\Users\User\Desktop\Cloud Computing Task Scheduling Simulator"
python --version
python gui/app.py
```

## Step 9: If Python Is Not Recognized

If PowerShell says Python is not recognized, try:

```powershell
py main.py
```

or

```powershell
py gui/app.py
```

If both `python` and `py` fail, then Python is not installed correctly on your system.

## Step 10: If The GUI Does Not Open

Possible reasons:

- Python may not include `tkinter`
- the Python installation may be broken

In that case, use CLI mode first:

```powershell
python main.py
```

## Step 11: Quick Summary

Main project folder:

```text
C:\Users\User\Desktop\Cloud Computing Task Scheduling Simulator
```

Main commands:

```powershell
python main.py
python gui/app.py
```

