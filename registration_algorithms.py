import pandas as pd
from datetime import timedelta


def base(df):
    registration_number = 1
    first_timestamp = df.loc[0, 'date_registration']
    current_class = df.loc[0, 'registration_class']

    df['registrations_id'] = 0

    for i in range(len(df)):
        if df.loc[i, 'registration_class'] != current_class:
            # Изменился registration_class
            registration_number += 1
            current_class = df.loc[i, 'registration_class']
            first_timestamp = df.loc[i, 'date_registration']

        elif df.loc[i, 'date_registration'] - first_timestamp > timedelta(minutes=30):
            # Превышен интервал в 30 минут
            registration_number += 1
            first_timestamp = df.loc[i, 'date_registration']

        # Присваиваем текущий номер регистрации
        df.loc[i, 'registrations_id'] = registration_number

    return df


def sliding_window(df, window_size=1, max_interval=timedelta(minutes=30)):
    # Функция для определения корректного registration_class на основе скользящего окна
    def get_correct_class(row_index):
        start = max(0, row_index - window_size)
        end = min(len(df), row_index + window_size + 1)
        window = df.iloc[start:end]

        # Исключаем записи, которые превышают максимальный интервал
        window = window[window['date_registration'] - df.loc[row_index, 'date_registration'] <= max_interval]

        if len(window) > 2:
            most_common_class = window['registration_class'].mode()[0]
            return most_common_class
        return df.loc[row_index, 'registration_class']

    # Применяем функцию скользящего окна к каждому ряду
    df['registration_class'] = df.index.map(get_correct_class)

    # Инициализируем первый номер регистрации и первую временную метку
    registration_number = 1
    first_timestamp = df.loc[0, 'date_registration']
    current_class = df.loc[0, 'registration_class']

    df['registrations_id'] = 0

    for i in range(len(df)):
        if df.loc[i, 'registration_class'] != current_class:
            registration_number += 1
            current_class = df.loc[i, 'registration_class']
            first_timestamp = df.loc[i, 'date_registration']

        elif df.loc[i, 'date_registration'] - first_timestamp > max_interval:
            registration_number += 1
            first_timestamp = df.loc[i, 'date_registration']

        df.loc[i, 'registrations_id'] = registration_number

    return df


def threshold(df, confidence_threshold=0.8, max_interval=timedelta(minutes=30)):
    df = df.sort_values(by=['date_registration']).reset_index(drop=True)

    registration_number = 1
    first_timestamp = df.loc[0, 'date_registration']
    current_class = df.loc[0, 'registration_class']

    df['registrations_id'] = 0

    for i in range(len(df)):
        if df.loc[i, 'registration_class'] != current_class and df.loc[i, 'confidence'] >= confidence_threshold:
            registration_number += 1
            current_class = df.loc[i, 'registration_class']
            first_timestamp = df.loc[i, 'date_registration']

        elif df.loc[i, 'date_registration'] - first_timestamp > max_interval:
            registration_number += 1
            first_timestamp = df.loc[i, 'date_registration']

        df.loc[i, 'registrations_id'] = registration_number
        df.loc[i, 'flag'] = df.loc[i, 'date_registration'] - first_timestamp

    return df


def sliding_window_and_treshold(df, window_size=2, max_interval=timedelta(minutes=30)):
    # Функция для определения корректного registration_class на основе скользящего окна и уверенности
    def get_correct_class(row_index):
        start = max(0, row_index - window_size)
        end = min(len(df), row_index + window_size + 1)
        window = df.iloc[start:end]

        # Исключаем записи, которые превышают максимальный интервал
        window = window[window['date_registration'] - df.loc[row_index, 'date_registration'] <= max_interval]

        if len(window) > 0:
            weighted_classes = window.groupby('registration_class')['confidence'].sum()
            most_confident_class = weighted_classes.idxmax()
            return most_confident_class
        return df.loc[row_index, 'registration_class']

    # Применяем функцию скользящего окна к каждому ряду
    df['registration_class'] = df.index.map(get_correct_class)

    # Инициализируем первый номер регистрации и первую временную метку
    registration_number = 1
    first_timestamp = df.loc[0, 'date_registration']
    current_class = df.loc[0, 'registration_class']

    # Создаем пустые столбцы для регистрации и продолжительности регистрации
    df['registrations_id'] = 0

    # Проходим по каждой строке DataFrame
    for i in range(len(df)):
        if df.loc[i, 'registration_class'] != current_class:
            registration_number += 1
            current_class = df.loc[i, 'registration_class']
            first_timestamp = df.loc[i, 'date_registration']

        elif df.loc[i, 'date_registration'] - first_timestamp > max_interval:
            registration_number += 1
            first_timestamp = df.loc[i, 'date_registration']

        df.loc[i, 'registrations_id'] = registration_number
        df.loc[i, 'flag'] = df.loc[i, 'date_registration'] - first_timestamp

    return df


if __name__ == "__main__":
    # Пример использования
    data = {
        'name': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15'],
        'registration_class': ['cat', 'cat', 'dog', 'cat', 'cat', 'cat', 'cat', 'dog', 'cat', 'cat', 'dog', 'cat',
                               'dog', 'cat', 'cat'],
        'date_registration': [
            '2023-07-01 09:00:00',
            '2023-07-01 09:05:00',
            '2023-07-01 09:06:00',
            '2023-07-01 09:07:00',
            '2023-07-01 09:16:00',
            '2023-07-01 09:25:00',
            '2023-07-01 09:50:00',
            '2023-07-01 10:00:00',
            '2023-07-02 09:10:00',
            '2023-07-02 09:45:00',
            '2023-07-03 10:00:00',
            '2023-07-03 10:05:00',
            '2023-07-03 10:06:00',
            '2023-07-03 10:07:00',
            '2023-07-03 10:09:00'
        ],
        'confidence': [0.8, 0.8, 0.9, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8,]
    }

    df = pd.DataFrame(data)
    df['date_registration'] = pd.to_datetime(df['date_registration'])

    df = sliding_window_and_treshold(df)
    print(df)