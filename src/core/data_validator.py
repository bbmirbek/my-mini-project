# src/core/data_validator.py

import logging
from datetime import datetime, timedelta
from typing import List, Tuple
import pandas as pd

logger = logging.getLogger(__name__)


def find_missing_dates(
    df_data: pd.DataFrame,
    df_reklama: pd.DataFrame,
    start_date: datetime,
    end_date: datetime
) -> Tuple[List[datetime], List[datetime]]:
    """
    Находит дни без данных в каждом DataFrame.
    
    Returns:
        Tuple[List[datetime], List[datetime]]: (missing_in_data, missing_in_reklama)
    """
    # Все дни в периоде
    all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Дни с данными в df_data
    dates_in_data = pd.to_datetime(
        df_data["Дата продажи"], 
        format="%Y-%m-%d", 
        errors="coerce"
    ).dt.date.unique()
    
    # Дни с данными в df_reklama
    dates_in_reklama = pd.to_datetime(
        df_reklama["Дата списания"], 
        format="%Y-%m-%d %H:%M", 
        errors="coerce"
    ).dt.date.unique()
    
    # Находим пропущенные дни
    missing_in_data = [
        d.date() for d in all_dates 
        if d.date() not in dates_in_data
    ]
    
    missing_in_reklama = [
        d.date() for d in all_dates 
        if d.date() not in dates_in_reklama
    ]
    
    return missing_in_data, missing_in_reklama


def check_data_completeness(
    df_data: pd.DataFrame,
    df_reklama: pd.DataFrame,
    start_date: datetime,
    end_date: datetime
) -> bool:
    """
    Проверяет полноту данных и запрашивает подтверждение у пользователя.
    
    Returns:
        bool: True если продолжить, False если отменить
    """
    missing_data, missing_reklama = find_missing_dates(
        df_data, df_reklama, start_date, end_date
    )
    
    if not missing_data and not missing_reklama:
        logger.info("✅ Все дни в периоде имеют данные")
        return True
    
    # Выводим информацию о пропущенных днях
    print("\n⚠️  ВНИМАНИЕ: Обнаружены дни без данных!\n")
    
    if missing_data:
        print(f"📊 Дни без данных о продажах ({len(missing_data)}):")
        for date in sorted(missing_data)[:10]:  # показываем первые 10
            print(f"   • {date.strftime('%d.%m.%Y')}")
        if len(missing_data) > 10:
            print(f"   ... и ещё {len(missing_data) - 10} дней")
        print()
    
    if missing_reklama:
        print(f"📢 Дни без рекламных данных ({len(missing_reklama)}):")
        for date in sorted(missing_reklama)[:10]:
            print(f"   • {date.strftime('%d.%m.%Y')}")
        if len(missing_reklama) > 10:
            print(f"   ... и ещё {len(missing_reklama) - 10} дней")
        print()
    
    # Запрашиваем подтверждение
    while True:
        response = input("Продолжить обработку? (да/нет): ").strip().lower()
        if response in ['да', 'yes', 'y', 'д']:
            logger.info("Пользователь подтвердил продолжение")
            return True
        elif response in ['нет', 'no', 'n', 'н']:
            logger.info("Пользователь отменил обработку")
            return False
        else:
            print("Пожалуйста, введите 'да' или 'нет'")