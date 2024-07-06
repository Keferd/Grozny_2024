import pandas as pd


def set_max_count(df):
    max_counts = df.groupby('registrations_id')['count'].max().reset_index()
    max_counts.columns = ['registrations_id', 'max_count']

    result_df = pd.merge(df, max_counts, on='registrations_id', how='left')

    return result_df
