# Веселов С.С.
import pandas as pd
import matplotlib.pyplot as plt
import ast


def load_data(filepath):
    """Загружает данные из CSV файла.

    Args: 
        filepath: Путь к CSV файлу.
    Return: 
        DataFrame с загруженными данными.
    """
    return pd.read_csv(filepath)


def detect_refill_windows(data, threshold_liters=5, merge_threshold_seconds=300):
    """Детектирует окна с ростом уровня топлива и объединяет близкие окна.

    Args:
        data (pd.DataFrame): DataFrame с данными.
        threshold_liters (float): Порог для детектирования заправки (в литрах).
        merge_threshold_seconds (int): Максимальная разница в секундах между окнами для объединения.
    Return:
        Список кортежей (начало окна, конец окна, суммарный рост).
    """
    refill_windows = []
    start_idx = None
    total_increase = 0

    for i in range(1, len(data)):
        # Разница между текущим и предыдущим значением уровня топлива
        diff = data['LLS_0_liters'].iloc[i] - data['LLS_0_liters'].iloc[i - 1]

        if diff > 0:  # Если уровень топлива растет
            if start_idx is None:
                start_idx = i - 1  # Начало окна
            total_increase += diff
        else:
            if start_idx is not None and total_increase >= threshold_liters:
                # Если окно завершено и рост превышает порог
                refill_windows.append((start_idx, i - 1, total_increase))
            start_idx = None
            total_increase = 0

    # Проверяем последнее окно
    if start_idx is not None and total_increase >= threshold_liters:
        refill_windows.append((start_idx, len(data) - 1, total_increase))

    # Объединение близких окон
    merged_windows = []
    if refill_windows:
        current_window = refill_windows[0]

        for window in refill_windows[1:]:
            start_idx, end_idx, total_increase = window
            prev_start, prev_end, prev_increase = current_window

            # Если разница между концом предыдущего окна и началом текущего меньше порога
            if (data['datetime'].iloc[start_idx] - data['datetime'].iloc[prev_end]).total_seconds() <= merge_threshold_seconds:
                # Объединяем окна
                current_window = (prev_start, end_idx, prev_increase + total_increase)
            else:
                merged_windows.append(current_window)
                current_window = window

        merged_windows.append(current_window)

    return merged_windows

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
    
    # Интерполяция данных LLS_0
    filtered_data['LLS_0_interpolated'] = filtered_data['LLS_0'].interpolate(method='linear')
    
    # Перевод в литры (предположим, что 1 единица LLS_0 = 0.1 литра)
    filtered_data['LLS_0_liters'] = filtered_data['LLS_0_interpolated'] * 0.1
    
    # Преобразуем timestamp в читаемый формат
    filtered_data['datetime'] = pd.to_datetime(filtered_data['timestamp'], unit='s')
    
    # Детектирование окон с заправками
    refill_windows = detect_refill_windows(filtered_data, threshold_liters=5, merge_threshold_seconds=300)
    
    # Построение графика
    plt.figure(figsize=(20, 5))
    plt.plot(filtered_data['datetime'], filtered_data['LLS_0_liters'], label='Уровень топлива (литры)', color='blue', marker='o')
    
    # Выделение окон с заправками на графике
    for window in refill_windows:
        start_idx, end_idx, total_increase = window
        plt.plot(filtered_data['datetime'].iloc[start_idx:end_idx + 1], 
                 filtered_data['LLS_0_liters'].iloc[start_idx:end_idx + 1], 
                 color='green', label='Заправка' if start_idx == refill_windows[0][0] else "")
        print(f"Заправка обнаружена с {filtered_data['datetime'].iloc[start_idx]} по {filtered_data['datetime'].iloc[end_idx]}, суммарный рост: {total_increase:.2f} литров")
    
    plt.title(f'График уровня топлива от времени для terminal_id: {terminal_id}')
    plt.xlabel('Время')
    plt.ylabel('Уровень топлива (литры)')
    plt.legend()
    plt.grid(True)
    plt.show()


def main():
    """Основная функция для выполнения задач."""

    filepath = 'S:/bigdata/lab5/data5.csv'
    data = load_data(filepath)

    # Задача 2
    terminal_id = '433100526928099' # Не бейте за магические числа, пишу этот код в 1:15, нет сил)
    solve_task2(data, terminal_id)


if __name__ == "__main__":
    main()
