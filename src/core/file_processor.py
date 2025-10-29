from pathlib import Path

import logging

from datetime import timedelta

from src.utils.constants import brands

from src.data_processing.pandas_part import build_report_dataframe
from src.excel.formatting import format_and_save_report
from src.excel.SecondList import export_cards_png_from_excel
from src.data_processing.detailed_pandas import build_detailed_report
from src.excel.detailed_formatting import format_and_save_detailed_report
from src.utils.io_utils import read_excel
from src.core.brand_detector import check_brand

import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def process_all_excel_files(brand, start_time, end_time, data_root: Path = Path("data")) -> None:
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

    start_date, end_date = start_time.date(), end_time.date()        # 2025-10-20 00:00
    end_next = end_time + timedelta(days=1)                          # 2025-10-21 00:00 (делаем правую границу ИСКЛЮЧИТЕЛЬНОЙ)


    for excel_path in excel_files:
        df = read_excel(excel_path)
        
        # Clean column names to remove whitespace
        df.columns = df.columns.str.strip()
        
        # Check if 'Бренд' column exists
        if 'Бренд' not in df.columns:
            if check_brand(df) != brand:
                continue
        elif not df["Бренд"].eq(brand).any():
            continue
         
        if len(df.columns) < 10 and "ID кампании" in df.columns:
            dt = pd.to_datetime(df["Дата списания"], format="%Y-%m-%d %H:%M", errors="coerce")

            mask = (dt >= start_time) & (dt < end_next)   # [start, end] по датам/времени

            df_period = df.loc[mask].copy()
            if df_period.empty:
                continue
            parts_reklama.append(df_period)

        elif len(df.columns) > 20 and len(df.columns) < 30 and "Номер склада" in df.columns:
            dt = pd.to_datetime(df["Дата"], format="%Y-%m-%d", errors="coerce")

            mask = dt.between(start_date, end_date, inclusive="both")

            df_period = df.loc[mask].copy()
            if df_period.empty:
                continue
            parts_storage.append(df_period)

        elif len(df.columns) > 50:
            # Конвертируем все колонки с датами за один раз
            date_columns = [
                "Дата продажи"
            ]

            # Проверяем, попадает ли хотя бы одна дата в диапазон
            masks = [
                pd.to_datetime(df[col], format="%Y-%m-%d", errors="coerce")
                .between(start_time, end_time, inclusive="both")
                for col in date_columns
            ]

            # Объединяем все маски через OR
            mask = pd.concat(masks, axis=1).any(axis=1)

            df_period = df.loc[mask].copy()
            if df_period.empty:
                continue
            parts_data.append(df_period)


    if not parts_data:
        logger.warning("Нет данных на этот период")
        return
    else:
        df_data = pd.concat(parts_data, ignore_index=True, sort=False, copy=False)
        df_data.drop_duplicates().reset_index(drop=True)

    if not parts_reklama:
        logger.warning("Нет данных на этот период")
        return
    else:
        df_reklama = pd.concat(parts_reklama, ignore_index=True, sort=False, copy=False)
        df_reklama.drop_duplicates().reset_index(drop=True)

    if parts_storage:
        df_storage = pd.concat(parts_storage, ignore_index=True, sort=False, copy=False)
        df_storage.drop_duplicates().reset_index(drop=True)


    Brand = brand.capitalize()

    report_path = Path("reports") / Path(Brand) / (str(start_date) + " - " + str(end_date))
    report_path.mkdir(parents=True, exist_ok=True)

    result_df, fines_df, summary_df, pre_last_df, last_df, corr = build_report_dataframe(df_data, df_reklama)
    format_and_save_report(result_df, fines_df, summary_df, pre_last_df, last_df, corr, report_path / "report.xlsx")
    export_cards_png_from_excel(report_path / "report.xlsx", report_path / "image_report.png", str(report_path.name), Brand)

    if parts_storage:
        detailed_result_df, corr2, Buyout = build_detailed_report(df_data, df_storage)
        format_and_save_detailed_report(detailed_result_df, corr2, Buyout, report_path / "detailed_report.xlsx")

