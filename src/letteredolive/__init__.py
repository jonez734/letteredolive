import sys
from pathlib import Path

shell_path = Path(__file__).parent / "shell"
if str(shell_path.parent) not in sys.path:
    sys.path.insert(0, str(shell_path.parent))

from shell import *  # noqa: F401, F403