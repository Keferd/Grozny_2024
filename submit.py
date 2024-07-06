def get_submit_csv(df):
    return df.groupby('registrations_id').agg(
        name_folder=('name_folder', 'first'),
        class_name=('registration_class', 'first'),
        date_registration_start=('date_registration', 'min'),
        date_registration_end=('date_registration', 'max'),
        count=('max_count', 'max')
    ).rename(columns={'class_name': 'class'}).reset_index()
