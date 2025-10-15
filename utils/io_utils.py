# utils/io_utils.py
import pandas as pd
from pathlib import Path

def read_excel(path: str):
    return pd.read_excel(path)

def write_report(result_df):
    out_path = Path("reports") / "report.xlsx"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        result_df.to_excel(writer, sheet_name="Еженедельный отчёт", index=False)
    print(f"✅ Отчёт успешно сохранён: {out_path}")
