import logging
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)


def adjust_dates_to_most_frequent(dates_series: pd.Series, date_format: str = "%Y-%m-%d") -> list:
    """
    Находит самую частую дату (считает её "сегодня").
    Заменяет все даты в диапазоне ±1 день на эту дату.
    Используется для дневных отчётов.
    
    Args:
        dates_series: Series с датами
        date_format: Формат даты
    
    Returns:
        Список скорректированных дат
    """
    # Конвертируем в datetime
    parsed_dates = pd.to_datetime(dates_series, errors='coerce')
    
    # Удаляем NaN для подсчёта
    valid_dates = parsed_dates.dropna()
    
    if valid_dates.empty:
        logger.warning("Нет валидных дат для обработки")
        return dates_series.tolist()
    
    # Находим дату, которая встречается чаще всего (это "сегодня")
    most_frequent_date = valid_dates.mode()[0]
    most_frequent_date_str = most_frequent_date.strftime(date_format)
    
    # Вычисляем вчера и завтра
    yesterday = most_frequent_date - timedelta(days=1)
    tomorrow = most_frequent_date + timedelta(days=1)
    
    # Считаем статистику
    frequency = (valid_dates == most_frequent_date).sum()
    logger.info(f"Самая частая дата ('сегодня'): {most_frequent_date_str} (встречается {frequency} раз из {len(valid_dates)})")
    logger.info(f"Диапазон замены: {yesterday.strftime(date_format)} - {tomorrow.strftime(date_format)} → {most_frequent_date_str}")
    
    # Заменяем вчера, сегодня и завтра на "сегодня"
    corrected_dates = []
    replaced_count = 0
    
    for date_val in parsed_dates:
        if pd.isna(date_val):
            corrected_dates.append(None)
        elif yesterday <= date_val <= tomorrow:
            # Дата в диапазоне [вчера, сегодня, завтра]
            if date_val != most_frequent_date:
                corrected_dates.append(most_frequent_date_str)
                logger.debug(f"Дата {date_val.strftime(date_format)} изменена на {most_frequent_date_str}")
                replaced_count += 1
            else:
                corrected_dates.append(date_val.strftime(date_format))
        else:
            # Дата за пределами диапазона - оставляем как есть
            corrected_dates.append(date_val.strftime(date_format))
    
    if replaced_count > 0:
        logger.info(f"Заменено дат: {replaced_count}")
    
    return corrected_dates


def adjust_weekly_dates(dates_series: pd.Series, date_format: str = "%Y-%m-%d") -> list:
    """
    Для недельных отчётов:
    1. Находит максимальную дату
    2. Вычисляет начало недели (max_date - 6 дней)
    3. Все даты < начала недели заменяет на начало недели
    
    Args:
        dates_series: Series с датами
        date_format: Формат даты
    
    Returns:
        Список скорректированных дат
    """
    # Конвертируем в datetime
    parsed_dates = pd.to_datetime(dates_series, errors='coerce')
    
    # Находим максимальную дату
    max_date = parsed_dates.max()
    
    if pd.isna(max_date):
        logger.warning("Не удалось определить максимальную дату")
        return dates_series.tolist()
    
    # Вычисляем начало недели (макс - 6 дней)
    week_start = max_date - timedelta(days=6)
    
    max_date_str = max_date.strftime(date_format)
    week_start_str = week_start.strftime(date_format)
    
    logger.info(f"Недельный отчёт: {week_start_str} - {max_date_str}")
    
    # Заменяем все даты до начала недели на начало недели
    corrected_dates = []
    for date_val in parsed_dates:
        if pd.isna(date_val):
            corrected_dates.append(None)
        elif date_val < week_start and date_val > week_start - timedelta(days=1):
            corrected_dates.append(week_start_str)
            logger.debug(f"Дата {date_val.strftime(date_format)} изменена на {week_start_str}")
        else:
            corrected_dates.append(date_val.strftime(date_format))
    
    return corrected_dates


def is_weekly_report(df: pd.DataFrame) -> bool:
    """
    Определяет, является ли отчёт недельным или дневным.
    """
    date_columns = ["Дата продажи", "Дата списания", "Дата"]
    
    for col in date_columns:
        if col in df.columns:
            unique_dates = df[col].nunique()
            # Если больше 2 уникальных дат, считаем недельным
            return unique_dates > 7
    
    return True


def classify_excel_file(file_path: Path) -> Optional[str]:
    """
    Определяет тип Excel файла по его содержимому.
    
    Returns:
        'main_data' | 'reklama' | 'storage' | None
    """
    try:
        df = pd.read_excel(file_path, nrows=10)
        df.columns = df.columns.str.strip()
        
        if "ID кампании" in df.columns and len(df.columns) < 10:
            return "reklama"
        elif "Номер склада" in df.columns and 20 < len(df.columns) < 30:
            return "storage"
        elif len(df.columns) > 50:
            return "main_data"
        else:
            logger.warning(f"Неизвестный формат файла: {file_path.name}")
            return None
            
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {file_path.name}: {e}")
        return None


def process_data_file(file_path: Path, output_path: Path) -> None:
    """
    Обрабатывает файл с данными о продажах, корректирует даты.
    """
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    
    if "Дата продажи" not in df.columns:
        logger.warning(f"Колонка 'Дата продажи' не найдена в {file_path.name}")
        df.to_excel(output_path, index=False)
        return
    
    # Сортируем по дате
#    df = df.sort_values(by="Дата продажи").reset_index(drop=True)
    
    is_weekly = is_weekly_report(df)
    logger.info(f"Обработка {'недельного' if is_weekly else 'дневного'} отчёта: {file_path.name}")
    
    if is_weekly:
        # Недельный: все даты < (max_date - 6) → (max_date - 6)
        df["Дата продажи"] = adjust_weekly_dates(df["Дата продажи"])
    else:
        # Дневной: все даты до максимальной → максимальная дата
        df["Дата продажи"] = adjust_dates_to_most_frequent(df["Дата продажи"])
    
    df.to_excel(output_path, index=False)
    logger.info(f"✅ Обработан файл данных: {file_path.name}")


def process_reklama_file(file_path: Path, output_path: Path) -> None:
    """
    Обрабатывает файл с рекламными данными, корректирует даты.
    """
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    
    if "Дата списания" not in df.columns:
        logger.warning(f"Колонка 'Дата списания' не найдена в {file_path.name}")
        df.to_excel(output_path, index=False)
        return
    
    # Сортируем по дате
    df = df.sort_values(by="Дата списания").reset_index(drop=True)
    
    is_weekly = is_weekly_report(df)
    logger.info(f"Обработка {'недельного' if is_weekly else 'дневного'} отчёта рекламы: {file_path.name}")
    
    # Извлекаем дату и время отдельно
    dates_with_time = df["Дата списания"].astype(str)
    dates_only = []
    times_only = []
    
    for dt_str in dates_with_time:
        if pd.isna(dt_str) or dt_str == 'nan':
            dates_only.append(None)
            times_only.append("00:00")
        else:
            parts = dt_str.split()
            dates_only.append(parts[0] if len(parts) > 0 else None)
            times_only.append(parts[1] if len(parts) > 1 else "00:00")
    
    dates_series = pd.Series(dates_only)
    
    if is_weekly:
        # Недельный: все даты < (max_date - 6) → (max_date - 6)
        corrected_dates_only = adjust_weekly_dates(dates_series)
    else:
        # Дневной: все даты до максимальной → максимальная дата
        corrected_dates_only = adjust_dates_to_most_frequent(dates_series)
    
    # Объединяем обратно с временем
    df["Дата списания"] = [
        f"{date} {time}" if date else None
        for date, time in zip(corrected_dates_only, times_only)
    ]
    
    df.to_excel(output_path, index=False)
    logger.info(f"✅ Обработан файл рекламы: {file_path.name}")


def process_storage_file(file_path: Path, output_path: Path) -> None:
    """
    Обрабатывает файл с данными о складе, корректирует даты.
    """
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    
    if "Дата" not in df.columns:
        logger.warning(f"Колонка 'Дата' не найдена в {file_path.name}")
        df.to_excel(output_path, index=False)
        return
    
    # Сортируем по дате
    df = df.sort_values(by="Дата").reset_index(drop=True)
    
    is_weekly = is_weekly_report(df)
    logger.info(f"Обработка {'недельного' if is_weekly else 'дневного'} отчёта склада: {file_path.name}")
    
    if is_weekly:
        # Недельный: все даты < (max_date - 6) → (max_date - 6)
        df["Дата"] = adjust_weekly_dates(df["Дата"])
    else:
        # Дневной: все даты до максимальной → максимальная дата
        df["Дата"] = adjust_dates_to_most_frequent(df["Дата"])
    
    df.to_excel(output_path, index=False)
    logger.info(f"✅ Обработан файл склада: {file_path.name}")
    

def organize_and_process_data(data_dir: Path = Path("data")) -> None:
    """
    Обрабатывает Excel файлы из корня data/ и распределяет по подпапкам.
    После обработки удаляет исходные файлы.
    
    Структура:
    data/
    ├── main_data/     (файлы продаж - обработанные)
    ├── reklama/       (файлы рекламы - обработанные)
    ├── storage/       (файлы склада - обработанные)
    ├── file1.xlsx     (исходные файлы)
    └── file2.xlsx
    """
    if not data_dir.exists():
        logger.error(f"Папка {data_dir} не найдена")
        return
    
    # Создаём структуру подпапок
    main_data_dir = data_dir / "main_data"
    reklama_dir = data_dir / "reklama"
    storage_dir = data_dir / "storage"
    
    for folder in [main_data_dir, reklama_dir, storage_dir]:
        folder.mkdir(parents=True, exist_ok=True)
    
    # Ищем все Excel файлы ТОЛЬКО в корне data/
    excel_files = [f for f in data_dir.glob("*.xlsx") if f.is_file()]
    
    if not excel_files:
        logger.warning(f"Excel файлы не найдены в корне {data_dir}")
        return
    
    print(f"\n📂 Найдено файлов для обработки: {len(excel_files)}\n")
    
    stats = {"main_data": 0, "reklama": 0, "storage": 0, "unknown": 0}
    processed_files = []  # список успешно обработанных файлов
    
    for file_path in excel_files:
        # Пропускаем временные файлы Excel
        if file_path.name.startswith("~$"):
            continue
        
        file_type = classify_excel_file(file_path)
        
        try:
            if file_type == "main_data":
                output_path = main_data_dir / file_path.name
                process_data_file(file_path, output_path)
                stats["main_data"] += 1
                processed_files.append(file_path)
                
            elif file_type == "reklama":
                output_path = reklama_dir / file_path.name
                process_reklama_file(file_path, output_path)
                stats["reklama"] += 1
                processed_files.append(file_path)
                
            elif file_type == "storage":
                output_path = storage_dir / file_path.name
                process_storage_file(file_path, output_path)
                stats["storage"] += 1
                processed_files.append(file_path)
                
            else:
                stats["unknown"] += 1
                
        except Exception as e:
            logger.error(f"Ошибка при обработке {file_path.name}: {e}")
    
    # Удаляем успешно обработанные файлы
    if processed_files:
        print(f"\n🗑️  Удаление исходных файлов ({len(processed_files)})...\n")
        for file_path in processed_files:
            try:
                file_path.unlink()
                logger.info(f"Удалён: {file_path.name}")
            except Exception as e:
                logger.error(f"Не удалось удалить {file_path.name}: {e}")
    
    # Выводим статистику
    print("\n" + "="*50)
    print("📊 СТАТИСТИКА ОБРАБОТКИ:")
    print("="*50)
    print(f"✅ Файлы продаж:    {stats['main_data']}")
    print(f"✅ Файлы рекламы:   {stats['reklama']}")
    print(f"✅ Файлы склада:    {stats['storage']}")
    if stats['unknown'] > 0:
        print(f"⚠️  Неопознанные:    {stats['unknown']}")
    print(f"🗑️  Удалено файлов:  {len(processed_files)}")
    print("="*50 + "\n")