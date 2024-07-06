import pandas as pd
import base
import window


def compare_grouped_dfs(valid_df, alg_df):
    merged_df = pd.merge(valid_df, alg_df, on=['class', 'date_registration_start', 'date_registration_end'],
                         how='inner')
    return len(merged_df) / len(valid_df)


def group_df(df):
    return df.groupby('registrations_id').agg(
        name_folder=('name_folder', 'first'),
        class_name=('registration_class', 'first'),
        date_registration_start=('date_registration', 'min'),
        date_registration_end=('date_registration', 'max')
    ).rename(columns={'class_name': 'class'}).reset_index()


df = pd.read_csv("registration.csv", sep=',')
df['date_registration'] = pd.to_datetime(df['date_registration'])
valid_df = group_df(df)

df = df.drop('registrations_id', axis=1)
base_df = group_df(base.add_registration(df))
window_df = group_df(window.add_registration(df))

print('base:', compare_grouped_dfs(valid_df, base_df))
print('window:', compare_grouped_dfs(valid_df, window_df))
