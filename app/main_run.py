import sys
import os
from pathlib import Path

# Get the current directory of main.py
current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent

# Add the necessary directories to sys.path
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(current_dir / "agents"))
sys.path.insert(0, str(current_dir / "applications_management"))
sys.path.insert(0, str(current_dir / "prompts"))

from agents.main import main 
from applications_management import update_spreadsheet, download_job_description

if __name__ == '__main__':
    main()
    update_spreadsheet.add_job_info_to_sheet()
    download_job_description.main()
