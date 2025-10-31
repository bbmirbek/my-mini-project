import logging
import re

from src.utils.constants import brands
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_period(user_input):
    m = re.match(r"\s*(\d{2}\.\d{2}\.\d{4})\s*-\s*(\d{2}\.\d{2}\.\d{4})\s*", user_input)
    
    if not m:
        logging.error("Неправильный формат даты")
        return False
    
    start = datetime.strptime(m.group(1), "%d.%m.%Y")
    end = datetime.strptime(m.group(2), "%d.%m.%Y")
    
    try:
        start = datetime.strptime(m.group(1), "%d.%m.%Y")
        end = datetime.strptime(m.group(2), "%d.%m.%Y")
    except ValueError:
        logging.error("Некорректная дата (например, 32.13.2025)")
        return False
    
    if end < start:
        logging.error("Дата окончания раньше даты начала")
        return False
    
    return True


def input_brand() -> str:
    """
    Запрашивает имя бренда с автоматическим определением и подтверждением.
    """
    # Маппинг сокращений на полные названия
    brand_mapping = {
        "alura": "ALURA store",
        "alura store": "ALURA store",
        "rossa": "ALURA Fashion",
        "alura fashion": "ALURA Fashion",
        "aylle": "aylle",
        "baylu": "baylu",
        "all": "all"
    }
    
    valid_brands = ["ALURA store", "ALURA Fashion", "aylle", "baylu", "all"]
    
    while True:
        name = input("Введите имя бренда: ").strip().lower()
        
        # Проверяем, есть ли в маппинге
        if name in brand_mapping:
            suggested_brand = brand_mapping[name]
            
            # Если название уже полное, возвращаем сразу
            if name == suggested_brand.lower():
                return suggested_brand
            
            # Иначе спрашиваем подтверждение
            while True:
                confirmation = input(
                    f"Вы имели в виду '{suggested_brand}'? (да/нет): "
                ).strip().lower()
                
                if confirmation in ['да', 'yes', 'y', 'д']:
                    return suggested_brand
                elif confirmation in ['нет', 'no', 'n', 'н']:
                    print("Попробуйте ещё раз.")
                    break  # Возвращаемся к вводу бренда
                else:
                    print("Пожалуйста, введите 'да' или 'нет'")
        else:
            print(f"❌ Неизвестный бренд. Доступные бренды:")
            for brand in valid_brands:
                print(f"   • {brand}")
            print()


def input_period():
    period_str = input("Введите период (dd.mm.yyyy - dd.mm.yyyy): ").strip()

    while not check_period(period_str):
        period_str = input("Введите правильный период (dd.mm.yyyy - dd.mm.yyyy): ").strip()
    
    m = re.match(r"\s*(\d{2}\.\d{2}\.\d{4})\s*-\s*(\d{2}\.\d{2}\.\d{4})\s*", period_str)

    start = datetime.strptime(m.group(1), "%d.%m.%Y")
    end = datetime.strptime(m.group(2), "%d.%m.%Y")

    return start, end
