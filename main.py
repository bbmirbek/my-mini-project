from pathlib import Path
from typing import Optional

import logging
import re

from datetime import datetime, timedelta

from utils.pandas_part import build_report_dataframe
from utils.excel_formatting import format_and_save_report
from utils.SecondList import export_cards_png_from_excel
from utils.detailed_pandas import build_detailed_report
from utils.detailed_excel_fromatting import format_and_save_detailed_report
from utils.io_utils import read_excel

import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

brands = ["alura", "aylle", "rossa", "baylu"]

def input_brand():
    name = input("Введите имя бренда: ").strip()
    name = name.lower()

    while not name in brands:
        name = input("Введите правильное имя бренда: ").strip()
    
    return name

def check_period(user_input):
    m = re.match(r"\s*(\d{2}\.\d{2}\.\d{4})\s*-\s*(\d{2}\.\d{2}\.\d{4})\s*", user_input)
    
    if not m:
        logging.error("Неправильный формат даты")
        return False
    
    start = datetime.strptime(m.group(1), "%d.%m.%Y")
    end = datetime.strptime(m.group(2), "%d.%m.%Y")
    
    if (end < start):
        logging.error("Дата окончания раньше даты начала")
        return False
    
    return True

def input_period():
    period_str = input("Введите период (dd.mm.yyyy - dd.mm.yyyy): ").strip()

    while not check_period(period_str):
        period_str = input("Введите правильный период (dd.mm.yyyy - dd.mm.yyyy): ").strip()
    
    m = re.match(r"\s*(\d{2}\.\d{2}\.\d{4})\s*-\s*(\d{2}\.\d{2}\.\d{4})\s*", period_str)

    start = datetime.strptime(m.group(1), "%d.%m.%Y")
    end = datetime.strptime(m.group(2), "%d.%m.%Y")
    
    return start, end


def process_all_excel_files(brand, start_date, end_date, data_root: Path = Path("data")) -> None:
    if not data_root.exists():
        logger.error(f"Директория не найдена: {data_root}")
        return
    
    excel_files = list(data_root.rglob("*.xlsx"))
    
    if not excel_files:
        logger.warning(f"Excel файлы не найдены в {data_root}")
        return
    
    parts_data = []
    parts_reklama = []
    parts_storage = []

    start_str, end_str = str(start_date), str(end_date)
    start = datetime.strptime(start_str, "%d.%m.%Y") 
    end   = datetime.strptime(end_str,   "%d.%m.%Y")            # 2025-10-20 00:00
    end_next = end + timedelta(days=1)                          # 2025-10-21 00:00 (делаем правую границу ИСКЛЮЧИТЕЛЬНОЙ)

    for excel_path in excel_files:
        df = read_excel(excel_path)
    
        if not df["Бренд"].eq(brand).any():
            continue
         
        if len(df.columns) < 10 and "ID кампании" in df.columns:
            dt = pd.to_datetime(df["Дата списания"], format="%Y-%m-%d %H:%M", errors="coerce")

            mask = (dt >= start) & (dt < end_next)   # [start, end] по датам/времени

            df_period = df.loc[mask].copy()
            parts_reklama.append(df_period)

        elif len(df.columns) > 20 and len(df.columns) < 30 and "Номер склада" in df.columns:
            dt = pd.to_datetime(df["Дата"], format="%Y-%m-%d", errors="coerce")

            mask = dt.between(start_date, end_date, inclusive="both")

            df_period = df.loc[mask].copy()
            parts_storage.append(df_period)

        elif len(df.columns) > 50:
            # Конвертируем все колонки с датами за один раз
            date_columns = [
                "Дата заказа покупателем",
                "Дата продажи",
                "Дата начала действия фиксации", 
                "Дата конца действия фиксации"
            ]

            # Проверяем, попадает ли хотя бы одна дата в диапазон
            masks = [
                pd.to_datetime(df[col], format="%Y-%m-%d", errors="coerce")
                .between(start_date, end_date, inclusive="both")
                for col in date_columns
            ]

            # Объединяем все маски через OR
            mask = pd.concat(masks, axis=1).any(axis=1)

            df_period = df.loc[mask].copy()
            parts_data.append(df_period)


    df_data = pd.concat(parts_data, ignore_index=True, sort=False, copy=False)
    df_data.drop_duplicates().reset_index(drop=True)

    df_reklama = pd.concat(parts_reklama, ignore_index=True, sort=False, copy=False)
    df_reklama.drop_duplicates().reset_index(drop=True)

    df_storage = pd.concat(parts_reklama, ignore_index=True, sort=False, copy=False)
    df_storage.drop_duplicates().reset_index(drop=True)


def main():
    brand_name = input_brand()
    start_date, end_date = input_period()

    process_all_excel_files(brand_name, start_date, end_date)

    


if __name__ == "__main__":
    main()
