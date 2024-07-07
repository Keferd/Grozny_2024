from utils import get_folder_name
def get_submit_dataframe(df_orig):
    df = df_orig.copy()
    df["folder_name"] = df["folder_name"].apply(lambda row: get_folder_name(path=row))
    df = df.groupby('registrations_id').agg(
        name_folder=('folder_name', 'first'),
        class_name=('class_name', 'first'),
        date_registration_start=('creation_time', 'min'),
        date_registration_end=('creation_time', 'max'),
        count=('max_count', 'max')
    ).rename(columns={'class_name': 'class'}).reset_index()
    df = df.drop('registrations_id', axis=1)

    return df
