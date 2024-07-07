import pandas as pd
import numpy as np

from ml.detection import detection, get_df_from_predictions
from registration_algorithms import *
from utils import set_max_count, set_duration, get_folder_name
from submit import get_submit_dataframe

# predictions = detection(src_dir="E://hacks//cechnya_ezji//test_data_Minprirodi//traps//51")
# df = get_df_from_predictions(list_predictions=predictions)
# df.to_csv("51_table.csv", index=False)

df = pd.read_csv("main_table.csv", sep=',')
df['creation_time'] = pd.to_datetime(df['creation_time'])

df = base(df)
df = set_max_count(df)
df = set_duration(df)

result_df = get_submit_dataframe(df)
result_df.to_csv("base_new.csv", index=False, sep=',')