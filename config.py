from pathlib import Path

# This is global path.
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

# This is the configuration for the BPR in the Task02 & Task04
alpha = 0.15 # 延误系数
beta = 4 # 拥堵敏感度系数

# This is for the `capacity` in Task03
PEAK_DURATION = 8.0 

# This is the cofiguration for the ODE Simulation.
T_END = 20.0
DT = 0.1

# This is the BLOCKED_ROADS Matrix
BLOCKED_NODE_PAIRS = [
    ("T02", "C03"),
    ("C03", "T02"),
    ("C03", "C04"),
    ("C04", "C03"),
]

