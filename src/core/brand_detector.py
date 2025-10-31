import logging
from pathlib import Path
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_brand(df):
    config_root = Path("configs")
    config_list = list(config_root.rglob("*.json"))

    for config_path in config_list:
        brand = config_path.stem

        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        first_row_campaign = df['Кампания'].iloc[0]  # Получаем первую строку
        product_code = first_row_campaign.split(' | ')[0]  # Разделяем по ' | ' и берем первую часть
        product_code_lower = product_code.lower()

        if product_code_lower in data['products']:
            if brand == "alura":
                brand = "ALURA store"
            elif brand == "rossa":
                brand = "ALURA Fashion"
            return brand
        
    logger.warning("Бренд не определен")