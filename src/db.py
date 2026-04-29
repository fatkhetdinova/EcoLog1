import sqlite3
import json
import logging

logger = logging.getLogger(__name__)

AVAILABLE_ACTIONS = [
    "Использовал многоразовую бутылку",
    "Отказался от пластика",
    "Сдал вторсырьё",
    "Проехал на велосипеде/общественном транспорте",
    "Потушил свет при выходе",
    "Компостировал отходы",
    "Купил продукты на развес"
]


def init_db(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS eco_entries (
                date TEXT PRIMARY KEY,
                actions_json TEXT NOT NULL,
                waste_level TEXT CHECK(waste_level IN ('мало', 'средне', 'много')),
                water_usage INTEGER CHECK(water_usage BETWEEN 1 AND 5),
                electricity_usage INTEGER CHECK(electricity_usage BETWEEN 1 AND 5),
                notes TEXT
            )
        ''')
        conn.commit()
        conn.close()
        logger.info(f"База данных инициализирована: {db_path}")
        return True
    except Exception as e:
        logger.error(f"Ошибка инициализации БД: {e}")
        return False


def save_entry(db_path, date, actions, waste_level, water_usage, electricity_usage, notes):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        actions_json = json.dumps(actions, ensure_ascii=False)
        cursor.execute('''
            INSERT OR REPLACE INTO eco_entries 
            (date, actions_json, waste_level, water_usage, electricity_usage, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (date, actions_json, waste_level, water_usage, electricity_usage, notes))
        conn.commit()
        conn.close()
        logger.info(f"Сохранена запись за {date}")
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения записи за {date}: {e}")
        return False


def get_entry(db_path, date):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM eco_entries WHERE date = ?', (date,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'date': row[0],
                'actions': json.loads(row[1]),
                'waste_level': row[2],
                'water_usage': row[3],
                'electricity_usage': row[4],
                'notes': row[5]
            }
        return None
    except Exception as e:
        logger.error(f"Ошибка получения записи за {date}: {e}")
        return None


def get_all_entries(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM eco_entries ORDER BY date')
        rows = cursor.fetchall()
        conn.close()
        entries = []
        for row in rows:
            entries.append({
                'date': row[0],
                'actions': json.loads(row[1]),
                'waste_level': row[2],
                'water_usage': row[3],
                'electricity_usage': row[4],
                'notes': row[5]
            })
        return entries
    except Exception as e:
        logger.error(f"Ошибка получения всех записей: {e}")
        return []


def get_entries_for_period(db_path, start_date, end_date):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM eco_entries 
            WHERE date BETWEEN ? AND ? 
            ORDER BY date
        ''', (start_date, end_date))
        rows = cursor.fetchall()
        conn.close()
        return [{
            'date': r[0],
            'actions': json.loads(r[1]),
            'waste_level': r[2],
            'water_usage': r[3],
            'electricity_usage': r[4],
            'notes': r[5]
        } for r in rows]
    except Exception as e:
        logger.error(f"Ошибка получения записей за период: {e}")
        return []