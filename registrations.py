import pandas as pd
from datetime import timedelta


def add_registration(df):
    registration_number = 1
    first_timestamp = df.loc[0, 'временная метка']
    current_class = df.loc[0, 'класс']

    df['регистрация'] = 0
    df['продолжительность'] = timedelta(0)

    for i in range(len(df)):
        if df.loc[i, 'класс'] != current_class:
            # Изменился класс
            registration_number += 1
            current_class = df.loc[i, 'класс']
            first_timestamp = df.loc[i, 'временная метка']

        elif df.loc[i, 'временная метка'] - first_timestamp > timedelta(minutes=30):
            # Превышен интервал в 30 минут
            registration_number += 1
            first_timestamp = df.loc[i, 'временная метка']

        # Присваиваем текущий номер регистрации
        df.loc[i, 'регистрация'] = registration_number

        # Рассчитываем продолжительность текущей регистрации (в минутах)
        df.loc[i, 'продолжительность'] = (df.loc[i, 'временная метка'] - first_timestamp).total_seconds() / 60

    return df


if __name__ == "__main__":
    # Пример использования
    data = {
        'имя': ['abv1', 'abv2', 'abv3', 'abv4', 'abv5', 'abv6'],
        'класс': ['A', 'A', 'A', 'B', 'A', 'A'],
        'временная метка': [
            '2023-07-01 09:00:00',
            '2023-07-01 09:25:00',
            '2023-07-01 09:50:00',
            '2023-07-01 10:00:00',
            '2023-07-02 09:10:00',
            '2023-07-02 09:45:00'
        ]
    }

    df = pd.DataFrame(data)
    df['временная метка'] = pd.to_datetime(df['временная метка'])

    df = add_registration(df)
    print(df)
