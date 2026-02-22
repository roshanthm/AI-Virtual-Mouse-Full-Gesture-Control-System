import shutil
import os

folder = "venv"

if os.path.exists(folder):
    shutil.rmtree(folder)
    print("venv deleted successfully.")
else:
    print("venv folder does not exist.")
