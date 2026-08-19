#!/usr/bin/env python
import sys
from pathlib import Path

shell_path = Path(__file__).parent / "shell"
if str(shell_path.parent) not in sys.path:
    sys.path.insert(0, str(shell_path.parent))

from shell import __main__  # noqa: F401, E402

if __name__ == "__main__" or __name__ == "letteredolive.__main__":
    __main__.main()