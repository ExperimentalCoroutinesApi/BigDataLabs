# Веселов С.С.
import pandas as pd
import matplotlib.pyplot as plt


def load_data(filepath):
    """Загружает данные из CSV файла.

    Args: 
        filepath: Путь к CSV файлу.
    Return: 
        DataFrame с загруженными данными.
    """
    return pd.read_csv(filepath)


def solve_task1(data):
    """Обрабатывает данные для задачи 1: строит график скорости от времени и детектирует превышение скорости.

    Args: 
        data: DataFrame с данными.
    """
    # Преобразуем timestamp в читаемый формат
    data['datetime'] = pd.to_datetime(data['timestamp'], unit='s')

    # Построение графика
    plt.figure(figsize=(10, 5))
    plt.plot(data['datetime'], data['speed'], label='Скорость (км/ч)')

    # Детектирование превышения скорости
    overspeed = data[data['speed'] > 60]
    if not overspeed.empty:
        for _, row in overspeed.iterrows():
            print(
                f"Превышение скорости на {row['speed'] - 60} км/ч в {row['datetime']}")
        plt.scatter(overspeed['datetime'], overspeed['speed'],
                    color='red', label='Превышение скорости')

    plt.title('График скорости от времени')
    plt.xlabel('Время')
    plt.ylabel('Скорость (км/ч)')
    plt.legend()
    plt.grid(True)
    plt.show()


import pandas as pd
import matplotlib.pyplot as plt
import ast

def solve_task2(data, terminal_id):
    """Обрабатывает данные для задачи 2: строит график по данным can_data и детектирует заправки.

    Args:
        data (pd.DataFrame): DataFrame с данными.
        terminal_id (str): ID терминала для фильтрации данных.
    """
    # Проверяем тип данных в столбце terminal_id
    if not pd.api.types.is_string_dtype(data['terminal_id']):
        # Если terminal_id не строка, преобразуем его в строку
        data['terminal_id'] = data['terminal_id'].astype(str)
    
    # Фильтрация данных по terminal_id
    filtered_data = data[data['terminal_id'] == terminal_id]
    
    if filtered_data.empty:
        print(f"Нет данных для terminal_id: {terminal_id}")
        return
    
    # Преобразуем can_data из строки в словарь
    try:
        filtered_data['can_data'] = filtered_data['can_data'].apply(ast.literal_eval)
    except (ValueError, SyntaxError) as e:
        print(f"Ошибка при преобразовании can_data: {e}")
        return
    
    # Извлекаем данные LLS_0
    filtered_data['LLS_0'] = filtered_data['can_data'].apply(lambda x: x.get('LLS_0', None))
    
    # Проверяем, есть ли данные для LLS_0
    if filtered_data['LLS_0'].isnull().all():
        print("Нет данных для LLS_0 в can_data.")
        return
    
    # Преобразуем timestamp в читаемый формат
    filtered_data['datetime'] = pd.to_datetime(filtered_data['timestamp'], unit='s')
    
    # Построение графика
    plt.figure(figsize=(20, 5))
    plt.plot(filtered_data['datetime'], filtered_data['LLS_0'], label='Уровень топлива (LLS_0)', marker='o')
    
    # Детектирование заправок (предположим, что заправка - это резкое увеличение уровня топлива)
    filtered_data['fuel_diff'] = filtered_data['LLS_0'].diff()
    refills = filtered_data[filtered_data['fuel_diff'] > 50]  # Пример порога для детектирования заправки
    
    if not refills.empty:
        for _, row in refills.iterrows():
            print(f"Заправка обнаружена в {row['datetime']}")
    
    plt.title(f'График уровня топлива от времени для terminal_id: {terminal_id}')
    plt.xlabel('Время')
    plt.ylabel('Уровень топлива (LLS_0)')
    plt.legend()
    plt.grid(True)
    plt.show()


def main():
    """Основная функция для выполнения задач."""

    filepath = 'S:/bigdata/lab4/data4.csv'
    data = load_data(filepath)

    # Задача 1
    solve_task1(data)

    # Задача 2
    terminal_id = '433100526928099' # Не бейте за магические числа, пишу этот код в 1:15, нет сил)
    solve_task2(data, terminal_id)


if __name__ == "__main__":
    main()
