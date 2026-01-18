# updater.py
import sys
import time
import os
import shutil
import subprocess

old_exe = sys.argv[1]
new_exe = sys.argv[2]

time.sleep(1)

try:
    shutil.move(new_exe, old_exe)
except Exception:
    sys.exit(1)

subprocess.Popen([old_exe])
