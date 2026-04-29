"""
Модуль управления данными: экспорт, импорт, бэкапы
"""

import json
import csv
import zipfile
import shutil
import os
from datetime import datetime
from pathlib import Path
import logging
from src.db import get_all_entries, init_db, save_entry

logger = logging.getLogger(__name__)


def export_to_csv(db_path, output_path):
    """
    Экспорт данных в CSV файл
    """
    entries = get_all_entries(db_path)
    if not entries:
        print("Нет данных для экспорта")
        return False

    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as csvfile:
            fieldnames = ['date', 'actions_count', 'waste_level', 'water_usage',
                          'electricity_usage', 'notes']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for entry in entries:
                writer.writerow({
                    'date': entry['date'],
                    'actions_count': len(entry['actions']),
                    'waste_level': entry['waste_level'],
                    'water_usage': entry['water_usage'],
                    'electricity_usage': entry['electricity_usage'],
                    'notes': entry['notes']
                })

        logger.info(f"Экспорт в CSV выполнен: {output_path}")
        print(f"✅ Экспортировано в {output_path}")
        return True
    except Exception as e:
        logger.error(f"Ошибка экспорта в CSV: {e}")
        print(f"❌ Ошибка: {e}")
        return False


def export_to_json(db_path, output_path):
    """
    Экспорт полных записей в JSON файл
    """
    entries = get_all_entries(db_path)
    if not entries:
        print("Нет данных для экспорта")
        return False

    try:
        with open(output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(entries, jsonfile, ensure_ascii=False, indent=2)

        logger.info(f"Экспорт в JSON выполнен: {output_path}")
        print(f"✅ Экспортировано в {output_path}")
        return True
    except Exception as e:
        logger.error(f"Ошибка экспорта в JSON: {e}")
        print(f"❌ Ошибка: {e}")
        return False


def backup_database(db_path, backup_dir):
    """
    Создание резервной копии базы данных
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{timestamp}.sqlite"
        backup_path = Path(backup_dir) / backup_name

        shutil.copy2(db_path, backup_path)
        logger.info(f"Создана резервная копия: {backup_path}")
        print(f"💾 Резервная копия создана: {backup_name}")
        return str(backup_path)
    except Exception as e:
        logger.error(f"Ошибка создания бэкапа: {e}")
        print(f"❌ Ошибка создания бэкапа: {e}")
        return None


def export_to_zip(db_path, backup_dir, output_zip=None):
    """
    Экспорт всех данных в ZIP-архив
    """
    if output_zip is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_zip = f"ecolog_export_{timestamp}.zip"

    try:
        # Создаём временную папку
        temp_dir = Path("temp_export")
        temp_dir.mkdir(exist_ok=True)

        # Экспортируем CSV
        csv_path = temp_dir / "export.csv"
        export_to_csv(db_path, csv_path)

        # Экспортируем JSON
        json_path = temp_dir / "export.json"
        export_to_json(db_path, json_path)

        # Копируем базу данных
        db_copy = temp_dir / "database.sqlite"
        shutil.copy2(db_path, db_copy)

        # Создаём ZIP архив
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in temp_dir.iterdir():
                zipf.write(file, file.name)

        # Очищаем временную папку
        shutil.rmtree(temp_dir)

        logger.info(f"Экспорт в ZIP выполнен: {output_zip}")
        print(f"✅ Создан архив: {output_zip}")
        return output_zip
    except Exception as e:
        logger.error(f"Ошибка создания ZIP: {e}")
        print(f"❌ Ошибка: {e}")
        return None


def import_from_zip(zip_path, db_path):
    """
    Импорт данных из ZIP-архива
    """
    try:
        temp_dir = Path("temp_import")
        temp_dir.mkdir(exist_ok=True)

        # Распаковываем
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(temp_dir)

        # Ищем JSON файл
        json_files = list(temp_dir.glob("*.json"))
        if not json_files:
            print("❌ В архиве не найден JSON файл")
            return False

        # Загружаем данные из JSON
        with open(json_files[0], 'r', encoding='utf-8') as f:
            entries = json.load(f)

        # Восстанавливаем базу данных
        for entry in entries:
            save_entry(
                db_path,
                entry['date'],
                entry['actions'],
                entry['waste_level'],
                entry['water_usage'],
                entry['electricity_usage'],
                entry['notes']
            )

        # Очищаем временную папку
        shutil.rmtree(temp_dir)

        logger.info(f"Импорт из ZIP выполнен: {zip_path}")
        print(f"✅ Импортировано {len(entries)} записей")
        return True
    except Exception as e:
        logger.error(f"Ошибка импорта из ZIP: {e}")
        print(f"❌ Ошибка: {e}")
        return False