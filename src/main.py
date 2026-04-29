"""
Главный модуль приложения EcoLog
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from src.db import init_db, AVAILABLE_ACTIONS
from src.actions import log_daily_action
from src.analytics import (show_history, show_monthly_stats,
                           get_weekly_eco_scores, visualize_progress,
                           generate_insights, check_and_motivate)
from src.data_manager import (export_to_csv, export_to_json,
                              backup_database, export_to_zip, import_from_zip)

# Загрузка конфигурации
load_dotenv()

DB_PATH = os.getenv('DB_PATH', 'eco_log.db')
WASTE_UNIT = os.getenv('WASTE_UNIT', 'liters')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Кроссплатформенные пути
BASE_DIR = Path(__file__).parent.parent
DB_PATH_FULL = BASE_DIR / DB_PATH
BACKUP_DIR = BASE_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)


def display_menu():
    """Отображение главного меню"""
    print("\n" + "=" * 50)
    print("🌿 EcoLog - Экологический дневник")
    print("=" * 50)
    print("1. 📝 Добавить/обновить запись за сегодня")
    print("2. 📜 Показать историю за неделю")
    print("3. 📈 Показать статистику за месяц")
    print("4. 📊 Визуализация прогресса")
    print("5. 💡 Получить инсайты")
    print("6. 🎯 Мотивационное сообщение")
    print("7. 💾 Экспорт данных (ZIP архив)")
    print("8. 📂 Импорт данных из ZIP")
    print("9. 🔄 Создать резервную копию БД")
    print("0. 🚪 Выход")
    print("=" * 50)


def main():
    """Главная функция приложения"""
    print("\n🌱 Добро пожаловать в EcoLog!")

    # Инициализация базы данных
    if not init_db(str(DB_PATH_FULL)):
        print("❌ Ошибка инициализации базы данных")
        sys.exit(1)

    logger.info("Приложение EcoLog запущено")

    while True:
        display_menu()
        choice = input("\nВыберите действие: ").strip()

        try:
            if choice == '1':
                log_daily_action(str(DB_PATH_FULL))
                input("\nНажмите Enter для продолжения...")

            elif choice == '2':
                show_history(str(DB_PATH_FULL), days=7)
                input("\nНажмите Enter для продолжения...")

            elif choice == '3':
                show_monthly_stats(str(DB_PATH_FULL))
                input("\nНажмите Enter для продолжения...")

            elif choice == '4':
                weekly_scores = get_weekly_eco_scores(str(DB_PATH_FULL))
                visualize_progress(weekly_scores)
                input("\nНажмите Enter для продолжения...")

            elif choice == '5':
                insights = generate_insights(str(DB_PATH_FULL))
                print("\n💡 Ваши персональные инсайты:")
                for insight in insights:
                    print(f"   {insight}")
                input("\nНажмите Enter для продолжения...")

            elif choice == '6':
                motivation = check_and_motivate(str(DB_PATH_FULL))
                if motivation:
                    print(f"\n{motivation}")
                else:
                    print("\n📝 Заполните больше дней, чтобы получать мотивацию!")
                input("\nНажмите Enter для продолжения...")

            elif choice == '7':
                print("\n📦 Экспорт данных в ZIP архив...")
                zip_path = export_to_zip(str(DB_PATH_FULL), str(BACKUP_DIR))
                if zip_path:
                    print(f"✅ Архив сохранён: {zip_path}")
                input("\nНажмите Enter для продолжения...")

            elif choice == '8':
                zip_path = input("Введите путь к ZIP файлу: ").strip()
                if zip_path:
                    import_from_zip(zip_path, str(DB_PATH_FULL))
                input("\nНажмите Enter для продолжения...")

            elif choice == '9':
                backup_database(str(DB_PATH_FULL), str(BACKUP_DIR))
                input("\nНажмите Enter для продолжения...")

            elif choice == '0':
                print("\n🌍 Спасибо, что заботитесь о планете! До свидания!")
                logger.info("Приложение завершено")
                break

            else:
                print("❌ Неверный выбор. Попробуйте снова.")

        except Exception as e:
            logger.error(f"Ошибка в главном меню: {e}")
            print(f"\n❌ Произошла ошибка: {e}")
            input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    main()