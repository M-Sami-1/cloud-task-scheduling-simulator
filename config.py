from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
ALGORITHMS_DIR = BASE_DIR / "algorithms"
SCHEDULER_DIR = BASE_DIR / "scheduler"
DATASET_DIR = BASE_DIR / "dataset"
METRICS_DIR = BASE_DIR / "metrics"
VISUALIZATION_DIR = BASE_DIR / "visualization"
GUI_DIR = BASE_DIR / "gui"
RESULTS_DIR = BASE_DIR / "results"

TASKS_CSV = DATASET_DIR / "tasks.csv"
OUTPUT_CSV = RESULTS_DIR / "output.csv"
OUTPUT_BATCH_CSV = RESULTS_DIR / "batch_summary.csv"
OUTPUT_BATCH_DETAILS_CSV = RESULTS_DIR / "batch_details.csv"
OUTPUT_PLOT_DIR = RESULTS_DIR / "plots"

DEFAULT_TASK_COUNT = 1000
DEFAULT_VM_COUNT = 10
DEFAULT_EXPERIMENT_COUNTS = (100, 200, 300, 400, 500, 600, 700, 800, 900, 1000)
DEFAULT_TASK_MIN_LENGTH = 1000
DEFAULT_TASK_MAX_LENGTH = 10000
DEFAULT_TASK_MIN_ARRIVAL = 0
DEFAULT_TASK_MAX_ARRIVAL = 100
DEFAULT_RANDOM_SEED = 42


def ensure_runtime_paths() -> None:
    """Create the output folders used by the simulator."""
    for path in (DATASET_DIR, RESULTS_DIR, OUTPUT_PLOT_DIR):
        path.mkdir(parents=True, exist_ok=True)


def enable_dpi_awareness() -> None:
    """Reduce Windows scaling blur for Tkinter windows when possible."""
    try:
        import ctypes

        if hasattr(ctypes, "windll"):
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                try:
                    ctypes.windll.user32.SetProcessDPIAware()
                except Exception:
                    pass
    except Exception:
        pass


@dataclass(frozen=True)
class VMConfig:
    count: int = DEFAULT_VM_COUNT


@dataclass(frozen=True)
class TaskConfig:
    count: int = DEFAULT_TASK_COUNT
    min_length: int = DEFAULT_TASK_MIN_LENGTH
    max_length: int = DEFAULT_TASK_MAX_LENGTH
    min_arrival: int = DEFAULT_TASK_MIN_ARRIVAL
    max_arrival: int = DEFAULT_TASK_MAX_ARRIVAL
    seed: int = DEFAULT_RANDOM_SEED


ensure_runtime_paths()
