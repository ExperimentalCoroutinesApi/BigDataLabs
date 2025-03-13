# Веселов С.С.
import csv
import io
import requests
from collections import defaultdict

url = "https://ejudge.179.ru/tasks/python/2022b/attachments/ejudge1.csv"


def load_data(url=url):
    """Скачивает данные по ссылке и возвращает их в виде списка словарей.

    Args:
        url (str): Ссылка на CSV-файл.

    Returns:
        list[dict]: Список словарей, где каждый словарь представляет строку из CSV-файла.
    """
    response = requests.get(url)
    response.raise_for_status()  # Проверяем, что запрос успешен

    # Используем io.BytesIO для работы с данными в памяти
    with io.BytesIO(response.content) as file:
        # Читаем CSV-файл с кодировкой utf-8 и разделителем ';'
        reader = csv.DictReader(
            io.TextIOWrapper(file, encoding='utf-8'),
            delimiter=';',
            quotechar='"'
        )
        data = [row for row in reader]

    return data


def solve_task1(data):
    """Решает первую задачу: подсчитывает общее число участников и статистику по языкам программирования.

    Args:
        data (list[dict]): Данные из CSV-файла.

    Returns:
        tuple: Кортеж из двух элементов:
            - total_participants (int): Общее число участников.
            - lang_counts (dict): Словарь, где ключ — язык программирования, а значение — число участников, использующих этот язык.
    """
    # Множества для хранения уникальных участников и языков
    participants = set()  # Уникальные участники
    lang_users = defaultdict(set)  # Участники, использующие каждый язык

    for row in data:
        user_id = row.get('User_Id', '').strip()
        user_login = row.get('User_Login', '').strip()
        user_inv = row.get('User_Inv', '').strip()
        lang = row.get('Lang', '').strip()
        score = row.get('Score', '').strip()

        # Пропускаем скрытых пользователей
        if user_inv == 'I':
            continue

        # Пропускаем строки с нулевым баллом или Compilation Error
        if score == '-1' or score == '0':
            continue

        # Учитываем участника
        # Уникальный идентификатор участника
        user_key = f"{user_id}_{user_login}"
        participants.add(user_key)

        # Учитываем язык программирования
        lang_users[lang].add(user_key)

    # Общее число участников
    total_participants = len(participants)

    # Подсчет числа участников для каждого языка
    lang_counts = {lang: len(users) for lang, users in lang_users.items()}

    return total_participants, lang_counts


def solve_task2(data):
    """Решает вторую задачу: подсчитывает сумму баллов для каждого участника.

    Args:
        data (list[dict]): Данные из CSV-файла.

    Returns:
        dict: Словарь, где ключ — имя пользователя, а значение — сумма баллов.
    """
    user_scores = defaultdict(lambda: defaultdict(int))

    for row in data:
        user_name = row.get('User_Name', '').strip()
        prob = row.get('Prob', '').strip()
        score = row.get('Score', '').strip()

        # Пропускаем строки, где имя пользователя отсутствует или пустое
        if not user_name:
            continue

        # Пропускаем строки с Compilation Error
        if score == '-1':
            continue

        # Преобразуем балл в число
        try:
            score = int(score)
        except ValueError:
            continue  # Пропускаем строки, где балл не является числом

        # Обновляем максимальный балл для задачи
        if score > user_scores[user_name][prob]:
            user_scores[user_name][prob] = score

    # Суммируем баллы по всем задачам для каждого пользователя
    total_scores = {user: sum(scores.values())
                    for user, scores in user_scores.items()}

    return total_scores


def print_task1_results(total_participants, lang_counts):
    """Выводит результаты первой задачи: общее число участников и статистику по языкам программирования.

    Args:
        total_participants (int): Общее число участников.
        lang_counts (dict): Словарь, где ключ — язык программирования, а значение — число участников, использующих этот язык.
    """
    # Сортируем языки по убыванию числа участников, затем по названию
    sorted_langs = sorted(lang_counts.items(), key=lambda x: (-x[1], x[0]))

    print("Результаты первой задачи:")
    print(f"Total: {total_participants}")
    for lang, count in sorted_langs:
        print(f"{lang}: {count}")


def print_task2_results(total_scores):
    """Выводит результаты второй задачи: список участников с их суммарными баллами.

    Args:
        total_scores (dict): Словарь, где ключ — имя пользователя, а значение — сумма баллов.
    """
    # Сортируем пользователей по убыванию суммы баллов, затем по имени
    sorted_users = sorted(total_scores.items(), key=lambda x: (-x[1], x[0]))

    print("\nРезультаты второй задачи:")
    for user, score in sorted_users:
        print(f"{user}: {score}")


def main():
    """Основная функция программы. Загружает данные, решает задачи и выводит результаты."""
    data = load_data(url)

    # Решение первой задачи
    total_participants, lang_counts = solve_task1(data)
    print_task1_results(total_participants, lang_counts)

    # Решение второй задачи
    total_scores = solve_task2(data)
    print_task2_results(total_scores)


if __name__ == "__main__":
    main()
