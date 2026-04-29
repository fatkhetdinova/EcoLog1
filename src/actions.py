from datetime import datetime
import logging
from src.db import save_entry, get_entry, AVAILABLE_ACTIONS

logger = logging.getLogger(__name__)


def calculate_daily_eco_score(entry):
    actions_score = len(entry['actions']) * 10
    waste_scores = {'мало': 10, 'средне': 0, 'много': -15}
    waste_score = waste_scores.get(entry['waste_level'], 0)
    water_score = (5 - entry['water_usage']) * 3
    electricity_score = (5 - entry['electricity_usage']) * 2
    return actions_score + waste_score + water_score + electricity_score


def log_daily_action(db_path):
    """Фиксация ежедневных экодействий"""

    # Спрашиваем, хочет ли пользователь ввести другую дату
    print("\n📅 Работа с датой:")
    print("  1. Сегодняшняя дата")
    print("  2. Ввести другую дату")
    date_choice = input("Выберите (1-2): ").strip()

    if date_choice == '2':
        date = input("Введите дату (ГГГГ-ММ-ДД), например 2026-04-25: ").strip()
    else:
        date = datetime.now().strftime('%Y-%m-%d')

    existing = get_entry(db_path, date)
    if existing:
        print(f"\n📝 Запись за {date} уже существует. Будет обновлена.")

    print("\n=== 📝 Ежедневный учёт экопривычек ===\n")

    print("Выберите экодействия (вводите номера через пробел):")
    for i, action in enumerate(AVAILABLE_ACTIONS, 1):
        print(f"  {i}. {action}")
    print("  0. Завершить выбор")

    selected_actions = []
    while True:
        choice = input("\nВаш выбор: ").strip()
        if choice == '0':
            break
        try:
            indices = [int(x) for x in choice.split() if x != '0']
            for idx in indices:
                if 1 <= idx <= len(AVAILABLE_ACTIONS):
                    selected_actions.append(AVAILABLE_ACTIONS[idx - 1])
                else:
                    print(f"⚠️ Номер {idx} вне диапазона")
        except ValueError:
            print("❌ Введите числа через пробел")

    selected_actions = list(set(selected_actions))

    print("\n🗑️ Уровень отходов:")
    waste_options = {'1': 'мало', '2': 'средне', '3': 'много'}
    for k, v in waste_options.items():
        print(f"  {k}. {v}")
    waste_choice = input("Выбор (1-3): ").strip()
    waste_level = waste_options.get(waste_choice, 'средне')

    try:
        water_usage = int(input("\n💧 Использование воды (1-5, где 1-минимум, 5-максимум): "))
        water_usage = max(1, min(5, water_usage))
    except ValueError:
        water_usage = 3

    try:
        electricity_usage = int(input("⚡ Использование электричества (1-5, где 1-минимум, 5-максимум): "))
        electricity_usage = max(1, min(5, electricity_usage))
    except ValueError:
        electricity_usage = 3

    notes = input("\n📝 Заметки дня: ").strip()

    save_entry(db_path, date, selected_actions, waste_level,
               water_usage, electricity_usage, notes)

    entry = get_entry(db_path, date)
    score = calculate_daily_eco_score(entry)

    print(f"\n✨ Эко-счёт за {date}: {score} баллов!")
    logger.info(f"Зафиксирован день {date} с эко-счётом {score}")

    return entry