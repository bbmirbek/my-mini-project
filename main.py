from pathlib import Path

from src.input.user_input import input_brand, input_period
from src.core.file_processor import process_all_excel_files
from src.core.data_organizer import organize_and_process_data
from src.utils.constants import brands

def main():
    print("="*60)
    print("  📊 СИСТЕМА ОБРАБОТКИ ДАННЫХ WB")
    print("="*60 + "\n")
    
    # Организуем и обрабатываем данные
    print("Обработка и распределение файлов...\n")
    organize_and_process_data(data_dir=Path("data"))

    brand_name = input_brand()
    start_time, end_time = input_period()

    if (brand_name == "all"):
        for brand in brands:
            if brand == "all":
                continue
            process_all_excel_files(brand, start_time, end_time)
    else:
        process_all_excel_files(brand_name, start_time, end_time)


if __name__ == "__main__":
    main()
