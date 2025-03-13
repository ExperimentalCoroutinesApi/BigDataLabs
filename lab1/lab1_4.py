# Веселов С.С.
import csv
from collections import defaultdict
import requests
import zipfile
import io

# Ссылка на архив с данными
url = "https://ejudge.179.ru/tasks/python/2022b/attachments/data-9776-2019-01-21.zip"


def load_data(url):
    """Скачивает и извлекает данные из ZIP-архива.

    Args:
        url (str): Ссылка на ZIP-архив с CSV-файлом.

    Returns:
        list[dict]: Список словарей, где каждый словарь представляет строку из CSV-файла.
                   Ключи словаря — названия столбцов, значения — соответствующие данные.
    """
    response = requests.get(url)
    response.raise_for_status()  # Проверяем, что запрос успешен

    # Открываем ZIP-архив и извлекаем CSV-файл
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        # Предполагаем, что в архиве только один файл
        csv_filename = zip_file.namelist()[0]
        with zip_file.open(csv_filename) as csv_file:
            # Читаем CSV-файл с кодировкой cp1251 и разделителем ';'
            reader = csv.DictReader(
                io.TextIOWrapper(csv_file, encoding='cp1251'),
                delimiter=';',
                quotechar='"'
            )
            data = [row for row in reader]

    return data


def count_access_points(data):
    """Подсчитывает количество точек доступа для каждого района.

    Args:
        data (list[dict]): Список словарей, где каждый словарь представляет строку из CSV-файла.
                          Ожидаемые ключи: 'District', 'NumberOfAccessPoints'.

    Returns:
        dict: Словарь, где ключ — название района (str), а значение — количество точек доступа (int).
    """
    district_counts = defaultdict(int)

    for row in data:
        district = row.get("District", "").strip(
            '"')  # Убираем кавычки из значения
        num_access_points = row.get("NumberOfAccessPoints", "").strip(
            '"')  # Убираем кавычки из значения

        # Пропускаем строки, где название района отсутствует или пустое
        if not district:
            continue

        # Преобразуем количество точек доступа в число
        try:
            num_access_points = int(num_access_points)
        except ValueError:
            # Если значение некорректное, пропускаем строку
            continue

        # Добавляем количество точек доступа для района
        district_counts[district] += num_access_points

    return district_counts


def print_results(district_counts):
    """Выводит результаты подсчёта точек доступа по районам.

    Args:
        district_counts (dict): Словарь, где ключ — название района (str), а значение — количество точек доступа (int).

    Returns:
        None: Функция только выводит результаты на экран.
    """
    # Сортируем районы по убыванию количества точек доступа, затем по названию
    sorted_districts = sorted(
        district_counts.items(),
        key=lambda x: (-x[1], x[0])
    )

    for district, count in sorted_districts:
        print(f"{district}: {count}")


def main():
    """Основная функция программы."""
    data = load_data(url)

    # Подсчитываем количество точек доступа для каждого района
    district_counts = count_access_points(data)

    # Выводим результаты
    print_results(district_counts)


if __name__ == "__main__":
    main()
