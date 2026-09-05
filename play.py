import pandas as pd
from  pathlib import Path
print(Path().absolute())
df = pd.read_csv("data/output/5k_pb_29m34_ACTIVITY-fit.csv", parse_dates=["timestamp"] )

print(df.shape)
print(df.columns.to_list())
print(df.tail())
print('max distance', df['distance'].max())
