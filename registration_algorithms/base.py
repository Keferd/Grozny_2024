import pandas as pd
from datetime import timedelta


def add_registration(df):
    registration_number = 1
    first_timestamp = df.loc[0, 'date_registration']
    current_class = df.loc[0, 'registration_class']

    df['registrations_id'] = 0
    df['flag'] = timedelta(0)

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


if __name__ == "__main__":
    # Пример использования
    data = {
        'name': ['abv1', 'abv2', 'abv3', 'abv4', 'abv5', 'abv6', 'abv7', 'abv8', 'abv9', 'abv10'],
        'registration_class': ['cat', 'cat', 'cat', 'cat', 'cat', 'cat', 'cat', 'dog', 'cat', 'cat'],
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
            '2023-07-02 09:45:00'
        ]
    }

    df = pd.DataFrame(data)
    df['date_registration'] = pd.to_datetime(df['date_registration'])

    df = add_registration(df)
    print(df)
