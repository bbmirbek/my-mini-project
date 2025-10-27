# utils/io_utils.py
import pandas as pd
from pathlib import Path

def read_excel(path: str):
    return pd.read_excel(path)

