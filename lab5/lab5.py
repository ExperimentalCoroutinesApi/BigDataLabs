import pandas as pd
import matplotlib.pyplot as plt
import ast


def load_data(filepath):
    """Загружает данные из CSV файла."""
    data = pd.read_csv(filepath)
    # Сортируем данные по временной метке
    data = data.sort_values(by='timestamp')
    return data


def detect_windows(data, threshold_liters=5, merge_threshold_seconds=300, detect_refill=True):
    """Детектирует окна с ростом или снижением уровня топлива и объединяет близкие окна.

    Args:
        data (pd.DataFrame): DataFrame с данными.
        threshold_liters (float): Порог для детектирования (в литрах).
        merge_threshold_seconds (int): Максимальная разница в секундах между окнами для объединения.
        detect_refill (bool): Если True, детектирует заправки (рост уровня топлива). Если False, детектирует сливы (снижение уровня топлива).
    Return:
        Список кортежей (начало окна, конец окна, суммарное изменение).
    """
    windows = []
    start_idx = None
    total_change = 0

    for i in range(1, len(data)):
        diff = data['LLS_0_liters'].iloc[i] - data['LLS_0_liters'].iloc[i - 1]

        # Рост или снижение уровня топлива
        if (detect_refill and diff > 0) or (not detect_refill and diff < 0):
            if start_idx is None:
                start_idx = i - 1
            # Суммируем абсолютное значение изменения
            total_change += abs(diff)
        else:
            if start_idx is not None and total_change >= threshold_liters:
                # Убедимся, что начало окна меньше конца
                if data['datetime'].iloc[start_idx] < data['datetime'].iloc[i - 1]:
                    windows.append((start_idx, i - 1, total_change))
            start_idx = None
            total_change = 0

    if start_idx is not None and total_change >= threshold_liters:
        # Убедимся, что начало окна меньше конца
        if data['datetime'].iloc[start_idx] < data['datetime'].iloc[len(data) - 1]:
            windows.append((start_idx, len(data) - 1, total_change))

    merged_windows = []
    if windows:
        current_window = windows[0]

        for window in windows[1:]:
            start_idx, end_idx, total_change = window
            prev_start, prev_end, prev_change = current_window

            if (data['datetime'].iloc[start_idx] - data['datetime'].iloc[prev_end]).total_seconds() <= merge_threshold_seconds:
                current_window = (prev_start, end_idx,
                                  prev_change + total_change)
            else:
                merged_windows.append(current_window)
                current_window = window

        merged_windows.append(current_window)

    return merged_windows


def solve_task(data, terminal_id, draw_refill=True, draw_drain=True, refill_threshold_liters=5, drain_threshold_liters=5, refill_merge_threshold_seconds=300, drain_merge_threshold_seconds=300):
    """Обрабатывает данные: строит график и детектирует заправки и/или сливы.

    Args:
        data (pd.DataFrame): DataFrame с данными.
        terminal_id (str): ID терминала для фильтрации данных.
        draw_refill (bool): Если True, рисует заправки на графике.
        draw_drain (bool): Если True, рисует сливы на графике.
        refill_threshold_liters (float): Порог для детектирования заправки (в литрах).
        drain_threshold_liters (float): Порог для детектирования слива (в литрах).
        refill_merge_threshold_seconds (int): Максимальная разница в секундах между окнами для объединения заправок.
        drain_merge_threshold_seconds (int): Максимальная разница в секундах между окнами для объединения сливов.
    """
    if not pd.api.types.is_string_dtype(data['terminal_id']):
        data['terminal_id'] = data['terminal_id'].astype(str)

    filtered_data = data[data['terminal_id'] == terminal_id]

    if filtered_data.empty:
        print(f"Нет данных для terminal_id: {terminal_id}")
        return

    try:
        filtered_data['can_data'] = filtered_data['can_data'].apply(
            ast.literal_eval)
    except (ValueError, SyntaxError) as e:
        print(f"Ошибка при преобразовании can_data: {e}")
        return

    filtered_data['LLS_0'] = filtered_data['can_data'].apply(
        lambda x: x.get('LLS_0', None))

    if filtered_data['LLS_0'].isnull().all():
        print("Нет данных для LLS_0 в can_data.")
        return

    filtered_data['LLS_0_interpolated'] = filtered_data['LLS_0'].interpolate(
        method='linear')
    filtered_data['LLS_0_liters'] = filtered_data['LLS_0_interpolated'] * 0.01

    filtered_data['datetime'] = pd.to_datetime(
        filtered_data['timestamp'], unit='s')

    plt.figure(figsize=(20, 5))
    plt.plot(filtered_data['datetime'], filtered_data['LLS_0_liters'],
             label='Уровень топлива (литры)', color='blue', marker='o')

    if draw_refill:
        refill_windows = detect_windows(filtered_data, threshold_liters=refill_threshold_liters,
                                        merge_threshold_seconds=refill_merge_threshold_seconds, detect_refill=True)
        for window in refill_windows:
            start_idx, end_idx, total_change = window
            plt.plot(filtered_data['datetime'].iloc[start_idx:end_idx + 1],
                     filtered_data['LLS_0_liters'].iloc[start_idx:end_idx + 1],
                     color='green', label='Заправка' if start_idx == refill_windows[0][0] else "")
            print(
                f"Заправка обнаружена с {filtered_data['datetime'].iloc[start_idx]} по {filtered_data['datetime'].iloc[end_idx]}, суммарный рост: {total_change:.2f} литров")

    if draw_drain:
        drain_windows = detect_windows(filtered_data, threshold_liters=drain_threshold_liters,
                                       merge_threshold_seconds=drain_merge_threshold_seconds, detect_refill=False)
        for window in drain_windows:
            start_idx, end_idx, total_change = window
            plt.plot(filtered_data['datetime'].iloc[start_idx:end_idx + 1],
                     filtered_data['LLS_0_liters'].iloc[start_idx:end_idx + 1],
                     color='red', label='Слив' if start_idx == drain_windows[0][0] else "")
            print(
                f"Слив обнаружен с {filtered_data['datetime'].iloc[start_idx]} по {filtered_data['datetime'].iloc[end_idx]}, суммарное снижение: {total_change:.2f} литров")

    plt.title(
        f'График уровня топлива от времени для terminal_id: {terminal_id}')
    plt.xlabel('Время')
    plt.ylabel('Уровень топлива (литры)')
    plt.legend()
    plt.grid(True)
    plt.show()


def main():
    # Список путей к файлам
    filepaths = [
        'S:/bigdata/lab5/1.csv',
        'S:/bigdata/lab5/2.csv',
        'S:/bigdata/lab5/3.csv',
        'S:/bigdata/lab5/4.csv',
        'S:/bigdata/lab5/5.csv'
    ]

    # Список terminal_id
    terminal_ids = [
        '433100526944851',
        '433100526945556',
        '433100526950621',
        '433427026902051',
        '433100526950514'
    ]

    # Загружаем данные для каждого файла
    data_list = [load_data(filepath) for filepath in filepaths]

    # Обрабатываем данные для каждого terminal_id
    for data, terminal_id in zip(data_list, terminal_ids):
        solve_task(data=data, terminal_id=terminal_id)


if __name__ == "__main__":
    main()
