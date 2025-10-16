#!/bin/zsh
set -euo pipefail

# перейти в папку проекта (куда положен этот файл)
cd -- "$(dirname "$0")"

# Проверка Python 3
if ! command -v python3 >/dev/null 2>&1; then
  osascript -e 'display alert "Python 3 не найден" message "Установите Python 3 (brew install python или python.org) и запустите снова."'
  exit 1
fi

# Виртуальное окружение (создастся при первом запуске)
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate

# Установка зависимостей (если есть файл)
python -m pip install -U pip
if [ -f "requirements.txt" ]; then
  python -m pip install -r requirements.txt
fi

# Гарантируем папку для отчётов
mkdir -p reports

# Запуск вашего скрипта
python main.py

# Открыть готовые отчеты в Finder
open reports || true

# Чтобы окно Терминала не закрывалось мгновенно
read -k 1 "?Готово. Нажмите любую клавишу, чтобы закрыть…"
