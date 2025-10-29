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
    
    if (end < start):
        logging.error("Дата окончания раньше даты начала")
        return False
    
    return True


def input_brand():
    name = input("Введите имя бренда: ").strip()
    name = name.lower()

    while not name in brands:
        name = input("Введите правильное имя бренда: ").strip()
    
    return name


def input_period():
    period_str = input("Введите период (dd.mm.yyyy - dd.mm.yyyy): ").strip()

    while not check_period(period_str):
        period_str = input("Введите правильный период (dd.mm.yyyy - dd.mm.yyyy): ").strip()
    
    m = re.match(r"\s*(\d{2}\.\d{2}\.\d{4})\s*-\s*(\d{2}\.\d{2}\.\d{4})\s*", period_str)

    start = datetime.strptime(m.group(1), "%d.%m.%Y")
    end = datetime.strptime(m.group(2), "%d.%m.%Y")

    return start, end
