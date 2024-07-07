from pprint import pprint

import pandas as pd
from datetime import timedelta
import math
import random


def base(df: pd.DataFrame) -> pd.DataFrame:
    registration_number = 1
    first_timestamp = df.loc[0, 'creation_time']
    current_class = df.loc[0, 'class_name']

    df['registrations_id'] = 0
    df["registration_class"] = df["class_name"]

    for i in range(len(df)):
        if df.loc[i, 'class_name'] != current_class:
            # Изменился class_name
            registration_number += 1
            current_class = df.loc[i, 'class_name']
            first_timestamp = df.loc[i, 'creation_time']

        elif df.loc[i, 'creation_time'] - first_timestamp > timedelta(minutes=30):
            # Превышен интервал в 30 минут
            registration_number += 1
            first_timestamp = df.loc[i, 'creation_time']

        # Присваиваем текущий номер регистрации
        df.loc[i, 'registrations_id'] = registration_number
        df.loc[i, 'registration_class'] = current_class

    return df


def sliding_window(df, window_size=1, max_interval=timedelta(minutes=30)):
    # Функция для определения корректного class_name на основе скользящего окна
    def get_correct_class(row_index):
        start = max(0, row_index - window_size)
        end = min(len(df), row_index + window_size + 1)
        window = df.iloc[start:end]

        # Исключаем записи, которые превышают максимальный интервал
        window = window[window['creation_time'] - df.loc[row_index, 'creation_time'] <= max_interval]

        if len(window) > 2:
            most_common_class = window['class_name'].mode()[0]
            return most_common_class
        return df.loc[row_index, 'class_name']

    # Применяем функцию скользящего окна к каждому ряду
    df['registration_class'] = df.index.map(get_correct_class)

    # Инициализируем первый номер регистрации и первую временную метку
    registration_number = 1
    first_timestamp = df.loc[0, 'creation_time']
    current_class = df.loc[0, 'registration_class']

    df['registrations_id'] = 0

    for i in range(len(df)):
        if df.loc[i, 'registration_class'] != current_class:
            registration_number += 1
            current_class = df.loc[i, 'registration_class']
            first_timestamp = df.loc[i, 'creation_time']

        elif df.loc[i, 'creation_time'] - first_timestamp > max_interval:
            registration_number += 1
            first_timestamp = df.loc[i, 'creation_time']

        df.loc[i, 'registrations_id'] = registration_number

    return df


def threshold(df, confidence_threshold=0.8, max_interval=timedelta(minutes=30)):
    df = df.sort_values(by=['creation_time']).reset_index(drop=True)

    registration_number = 1
    first_timestamp = df.loc[0, 'creation_time']
    current_class = df.loc[0, 'class_name']

    df['registrations_id'] = 0
    df["registration_class"] = df["class_name"]

    for i in range(len(df)):
        if df.loc[i, 'class_name'] != current_class and df.loc[i, 'confidence'] >= confidence_threshold:
            registration_number += 1
            current_class = df.loc[i, 'class_name']
            first_timestamp = df.loc[i, 'creation_time']

        elif df.loc[i, 'creation_time'] - first_timestamp > max_interval:
            registration_number += 1
            first_timestamp = df.loc[i, 'creation_time']

        df.loc[i, 'registrations_id'] = registration_number
        df.loc[i, 'registration_class'] = current_class
    return df


def sliding_window_and_treshold(df, window_size=2, max_interval=timedelta(minutes=30)):
    # Функция для определения корректного class_name на основе скользящего окна и уверенности
    def get_correct_class(row_index):
        start = max(0, row_index - window_size)
        end = min(len(df), row_index + window_size + 1)
        window = df.iloc[start:end]

        # Исключаем записи, которые превышают максимальный интервал
        window = window[window['creation_time'] - df.loc[row_index, 'creation_time'] <= max_interval]

        if len(window) > 0:
            weighted_classes = window.groupby('class_name')['confidence'].sum()
            most_confident_class = weighted_classes.idxmax()
            return most_confident_class
        return df.loc[row_index, 'class_name']

    # Применяем функцию скользящего окна к каждому ряду
    df['registration_class'] = df.index.map(get_correct_class)

    # Инициализируем первый номер регистрации и первую временную метку
    registration_number = 1
    first_timestamp = df.loc[0, 'creation_time']
    current_class = df.loc[0, 'registration_class']

    # Создаем пустые столбцы для регистрации и продолжительности регистрации
    df['registrations_id'] = 0

    # Проходим по каждой строке DataFrame
    for i in range(len(df)):
        if df.loc[i, 'registration_class'] != current_class:
            registration_number += 1
            current_class = df.loc[i, 'registration_class']
            first_timestamp = df.loc[i, 'creation_time']

        elif df.loc[i, 'creation_time'] - first_timestamp > max_interval:
            registration_number += 1
            first_timestamp = df.loc[i, 'creation_time']

        df.loc[i, 'registrations_id'] = registration_number

    return df


def calculate_probability(time_delta_seconds, initial_probability=1.0, lambda_=0.001):
    probability = 1 - initial_probability * math.exp(-lambda_ * time_delta_seconds)
    return probability


def distribution_method(df: pd.DataFrame) -> pd.DataFrame:

    registration_number = 1
    first_timestamp = df.loc[0, 'creation_time']
    current_class = df.loc[0, 'class_name']

    df['registrations_id'] = 0
    df["registration_class"] = df["class_name"]
    df.loc[0, 'registrations_id'] = registration_number

    for i in range(1, len(df)):
        time_delta = df.loc[i, 'creation_time'] - first_timestamp
        time_delta_seconds = time_delta.total_seconds()

        if time_delta > timedelta(minutes=30):
            # Превышен интервал в 30 минут
            registration_number += 1
            first_timestamp = df.loc[i, 'creation_time']
        else:
            probability = calculate_probability(time_delta_seconds)
            random_value = random.random()

            if df.loc[i, 'class_name'] != current_class and random_value < probability:
                registration_number += 1
                current_class = df.loc[i, 'class_name']
                first_timestamp = df.loc[i, 'creation_time']

        df.loc[i, 'registrations_id'] = registration_number
        df.loc[i, 'registration_class'] = current_class

    return df


def duper_method(df, window_size=2, max_interval=timedelta(minutes=30)):
    def get_correct_class(row_index):
        start = max(0, row_index - window_size)
        end = min(len(df), row_index + window_size + 1)
        window = df.iloc[start:end]

        # Исключаем записи, которые превышают максимальный интервал
        window = window[window['creation_time'] - df.loc[row_index, 'creation_time'] <= max_interval]

        if len(window) > 0:
            weighted_classes = window.groupby('class_name')['confidence'].sum()
            most_confident_class = weighted_classes.idxmax()
            return most_confident_class
        return df.loc[row_index, 'class_name']

    # Применяем функцию скользящего окна к каждому ряду
    df['registration_class'] = df.index.map(get_correct_class)

    # Инициализируем первый номер регистрации и первую временную метку
    registration_number = 1
    first_timestamp = df.loc[0, 'creation_time']
    current_class = df.loc[0, 'registration_class']

    # Создаем пустые столбцы для регистрации и продолжительности регистрации
    df['registrations_id'] = 0

    # Проходим по каждой строке DataFrame
    for i in range(1, len(df)):
        time_delta = df.loc[i, 'creation_time'] - first_timestamp
        time_delta_seconds = time_delta.total_seconds()
        if time_delta > timedelta(minutes=30):
            # Превышен интервал в 30 минут
            registration_number += 1
            first_timestamp = df.loc[i, 'creation_time']
        else:
            probability = calculate_probability(time_delta_seconds)
            random_value = random.random()

            if df.loc[i, 'class_name'] != current_class and random_value < probability:
                registration_number += 1
                current_class = df.loc[i, 'class_name']
                first_timestamp = df.loc[i, 'creation_time']

        df.loc[i, 'registrations_id'] = registration_number

    return df

pd.set_option('display.max_columns', None)

if __name__ == "__main__":
    # Пример использования
    data = {
        'name': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15'],
        'class_name': ['cat', 'cat', 'dog', 'cat', 'cat', 'cat', 'cat', 'dog', 'cat', 'cat', 'dog', 'cat',
                               'dog', 'cat', 'cat'],
        'creation_time': [
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
    df['creation_time'] = pd.to_datetime(df['creation_time'])

    df = distribution_method(df)
    print(df[["class_name", "creation_time", "registration_class", "registrations_id"]])