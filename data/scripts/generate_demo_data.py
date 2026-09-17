"""
CLI Entry Point Script to trigger NovaMart Data Generation.
"""

import sys
from pathlib import Path

# Ensure root directory is on Python path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from data.generators.generate_data import run_data_generation

if __name__ == "__main__":
    output_directory = sys.argv[1] if len(sys.argv) > 1 else "data/output"
    run_data_generation(output_directory)
