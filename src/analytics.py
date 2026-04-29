"""
Модуль аналитики: расчёт эко-счёта, инсайты, визуализация
"""

from datetime import datetime, timedelta
import logging
from src.db import get_entries_for_period, get_all_entries
from src.actions import calculate_daily_eco_score

logger = logging.getLogger(__name__)


def create_action_filter(action_name):
    """
    Замыкание: возвращает функцию для фильтрации записей по действию
    """

    def filter_by_action(entry):
        return action_name in entry['actions']

    return filter_by_action


def get_weekly_eco_scores(db_path):
    """
    Получение эко-счётов по неделям
    """
    entries = get_all_entries(db_path)
    if not entries:
        return []

    weekly_scores = {}
    for entry in entries:
        date = datetime.strptime(entry['date'], '%Y-%m-%d')
        week_num = date.isocalendar()[1]
        year = date.year
        week_key = f"{year}-W{week_num}"

        if week_key not in weekly_scores:
            weekly_scores[week_key] = []
        weekly_scores[week_key].append(calculate_daily_eco_score(entry))

    result = []
    for week_key, scores in weekly_scores.items():
        avg_score = sum(scores) / len(scores)
        result.append({'week': week_key, 'score': avg_score})

    return result


def visualize_progress(weekly_scores):
    """
    Текстовая визуализация прогресса
    """
    if not weekly_scores:
        print("Нет данных для визуализации")
        return

    print("\n📊 Визуализация прогресса по неделям:")
    for i, week_data in enumerate(weekly_scores[-4:], 1):
        score = week_data['score']
        bars = int(score / 10)
        bar_str = '█' * min(bars, 20) + '░' * (20 - min(bars, 20))
        print(f"Неделя {i}: {bar_str} {score:.0f} баллов")


def generate_insights(db_path):
    """
    Генерация персональных инсайтов
    """
    entries = get_all_entries(db_path)
    if len(entries) < 3:
        return ["📝 Продолжайте заполнять дневник — скоро появятся инсайты!"]

    insights = []

    # Инсайт про пластик
    plastic_filter = create_action_filter("Отказался от пластика")
    plastic_days = list(filter(plastic_filter, entries))
    plastic_percent = len(plastic_days) / len(entries) * 100

    if plastic_days:
        scores_with_plastic = [calculate_daily_eco_score(d) for d in plastic_days]
        avg_score_with = sum(scores_with_plastic) / len(scores_with_plastic)

        other_days = [e for e in entries if not plastic_filter(e)]
        if other_days:
            scores_without = [calculate_daily_eco_score(d) for d in other_days]
            avg_score_without = sum(scores_without) / len(scores_without)
            diff = ((avg_score_with - avg_score_without) / avg_score_without) * 100
            insights.append(f"💡 В дни без пластика ваш эко-счёт выше на {diff:.0f}%!")

    # Инсайт про общественный транспорт
    transport_filter = create_action_filter("Проехал на велосипеде/общественном транспорте")
    transport_days = list(filter(transport_filter, entries))
    if len(transport_days) >= 2:
        insights.append(f"🚲 Вы использовали эко-транспорт в {len(transport_days)} из {len(entries)} дней!")

    return insights if insights else ["👍 Вы на правильном пути! Продолжайте в том же духе!"]


def check_and_motivate(db_path):
    """
    Проверка рекордов и мотивация
    """
    entries = get_all_entries(db_path)
    if len(entries) < 2:
        return None

    recent_week = entries[-7:] if len(entries) >= 7 else entries
    recent_scores = [calculate_daily_eco_score(e) for e in recent_week]
    avg_recent = sum(recent_scores) / len(recent_scores)

    previous_week = entries[-14:-7] if len(entries) >= 14 else entries[:-len(recent_week)]
    if previous_week:
        prev_scores = [calculate_daily_eco_score(e) for e in previous_week]
        avg_prev = sum(prev_scores) / len(prev_scores)

        if avg_recent > avg_prev:
            improvement = ((avg_recent - avg_prev) / avg_prev) * 100
            return f"🎉 Отлично! Ваш эко-счёт вырос на {improvement:.0f}% по сравнению с прошлой неделей!"

    # Проверка рекорда
    max_score = max([calculate_daily_eco_score(e) for e in entries])
    if recent_scores[-1] == max_score and max_score > 0:
        return f"🏆 Поздравляем! Это ваш новый рекорд — {max_score} баллов!"

    return None


def show_history(db_path, days=7):
    """
    Показать историю за последние N дней
    """
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    entries = get_entries_for_period(db_path, start_date, end_date)

    if not entries:
        print(f"\nНет записей за последние {days} дней")
        return

    print(f"\n📜 История за последние {days} дней:\n")
    print("-" * 70)

    for entry in entries:
        score = calculate_daily_eco_score(entry)
        actions_count = len(entry['actions'])
        print(f"📅 {entry['date']} | Баллов: {score:3d} | Действий: {actions_count} | "
              f"Отходы: {entry['waste_level']}")
        if entry['notes']:
            print(f"   📝 {entry['notes']}")
        print("-" * 70)


def show_monthly_stats(db_path):
    """
    Показать статистику за месяц
    """
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    entries = get_entries_for_period(db_path, start_date, end_date)

    if not entries:
        print("\nНет записей за последний месяц")
        return

    scores = [calculate_daily_eco_score(e) for e in entries]
    avg_score = sum(scores) / len(scores)

    total_actions = sum(len(e['actions']) for e in entries)
    unique_actions = set()
    for entry in entries:
        unique_actions.update(entry['actions'])

    print("\n📈 Статистика за месяц:")
    print(f"   Дней с записями: {len(entries)}")
    print(f"   Средний эко-счёт: {avg_score:.1f}")
    print(f"   Всего действий: {total_actions}")
    print(f"   Уникальных привычек: {len(unique_actions)}")