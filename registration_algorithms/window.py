import pandas as pd
from datetime import timedelta


def add_registration(df, window_size=1, max_interval=timedelta(minutes=30)):
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
    df['flag'] = timedelta(0)

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
        ]
    }

    df = pd.DataFrame(data)
    df['date_registration'] = pd.to_datetime(df['date_registration'])

    df = add_registration(df)
    print(df)
