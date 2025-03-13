# Веселов С.С.
import csv
import io
import requests
from collections import defaultdict

url = "https://ejudge.179.ru/tasks/python/2022b/attachments/ejudge2.csv"


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


def calculate_team_results(data):
    """Рассчитывает результаты для каждой команды.

    Для каждой команды подсчитывает количество решённых задач и штрафное время.
    Штрафное время рассчитывается как время сдачи задачи в минутах плюс
    20 минут за каждую неудачную попытку.

    Args:
        data (list[dict]): Список словарей, где каждый словарь представляет строку из CSV-файла.
                          Ожидаемые ключи: 'User_Name', 'Prob', 'Stat_Short', 'Dur_Hour', 'Dur_Min'.

    Returns:
        dict: Словарь, где ключ — название команды (str), а значение — словарь с ключами:
              - 'solved' (int): Количество решённых задач.
              - 'penalty' (int): Суммарное штрафное время в минутах.
    """
    team_results = defaultdict(lambda: {"solved": 0, "penalty": 0})
    # Количество неудачных попыток по задачам
    team_attempts = defaultdict(lambda: defaultdict(int))

    for row in data:
        # Используем User_Name вместо Team
        team_name = row.get("User_Name", "").strip()
        problem = row.get("Prob", "").strip()
        status = row.get("Stat_Short", "").strip()
        dur_hour = int(row.get("Dur_Hour", 0))
        dur_min = int(row.get("Dur_Min", 0))

        # Пропускаем строки, где название команды отсутствует или пустое
        if not team_name:
            continue

        # Пропускаем строки, где User_Name не соответствует формату команды (например, не содержит двоеточия)
        if ":" not in team_name:
            continue

        # Пропускаем решения с ошибкой компиляции
        if status == "CE":
            continue

        # Время сдачи в минутах
        submission_time = dur_hour * 60 + dur_min

        if status == "OK":
            # Если задача уже была решена, пропускаем
            if team_attempts[team_name][problem] == -1:
                continue

            # Увеличиваем количество решённых задач
            team_results[team_name]["solved"] += 1

            # Добавляем штрафное время: время сдачи + 20 минут за каждую неудачную попытку
            penalty_time = submission_time + 20 * \
                team_attempts[team_name][problem]
            team_results[team_name]["penalty"] += penalty_time

            # Помечаем задачу как решённую
            team_attempts[team_name][problem] = -1
        else:
            # Увеличиваем количество неудачных попыток, если задача ещё не решена
            if team_attempts[team_name][problem] != -1:
                team_attempts[team_name][problem] += 1

    return team_results


def print_results(team_results):
    """Выводит результаты командной олимпиады.

    Args:
        team_results (dict): Словарь, где ключ — название команды (str), а значение — словарь с ключами:
                             - 'solved' (int): Количество решённых задач.
                             - 'penalty' (int): Суммарное штрафное время в минутах.
    """
    # Сортируем команды по убыванию решённых задач, затем по возрастанию штрафного времени, затем по названию
    sorted_teams = sorted(
        team_results.items(),
        key=lambda x: (-x[1]["solved"], x[1]["penalty"], x[0])
    )

    print("Результаты командной олимпиады:")
    for team, result in sorted_teams:
        print(f"{team}: {result['solved']} {result['penalty']}")


def main():
    """Основная функция программы."""
    data = load_data(url)

    # Рассчитываем результаты для каждой команды
    team_results = calculate_team_results(data)

    # Выводим результаты
    print_results(team_results)


if __name__ == "__main__":
    main()
