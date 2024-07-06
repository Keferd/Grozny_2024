import pandas as pd
import os
from datetime import datetime, timedelta


def convert_to_datetime(seconds):
    delta = timedelta(seconds=seconds)
    minutes_seconds = str(delta)[2:7]
    time_object = datetime.strptime(minutes_seconds, "%M:%S")
    return time_object


def set_duration(df):
    time_bounds = df.groupby('registrations_id')['creation_time'].agg(['min', 'max']).reset_index()
    time_bounds['duration_seconds'] = (time_bounds['max'] - time_bounds['min']).dt.total_seconds()
    time_bounds['duration'] = time_bounds['duration_seconds'].apply(lambda x: convert_to_datetime(x).strftime("%M:%S"))

    result_df = pd.merge(df, time_bounds[['registrations_id', 'duration']], on='registrations_id', how='left')

    return result_df


def set_max_count(df):
    max_counts = df.groupby('registrations_id')['count'].max().reset_index()
    max_counts.columns = ['registrations_id', 'max_count']

    result_df = pd.merge(df, max_counts, on='registrations_id', how='left')

    return result_df


def get_folder_name(root_path, file_path, filename):
    file_path_without_filename = file_path.replace('\\' + filename, '')
    folder_name = os.path.relpath(file_path_without_filename, root_path)

    if folder_name == "":
        folder_name = os.path.basename(file_path).strip('\\')

    return folder_name
