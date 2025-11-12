import os
from datetime import datetime

def ensureDir(path):
    os.makedirs(path, exist_ok=True)

def ensureDirs(paths):
    for p in paths:
        ensureDir(p)

def getTimestamp(fmt):
    return datetime.now().strftime(fmt)