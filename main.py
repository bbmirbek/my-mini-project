from src.input.user_input import input_brand, input_period
from src.core.file_processor import process_all_excel_files


def main():
    brand_name = input_brand()
    start_time, end_time = input_period()

    process_all_excel_files(brand_name, start_time, end_time)


if __name__ == "__main__":
    main()
