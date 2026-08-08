import pandas as pd

df = pd.DataFrame({
    "col1": [21,42,44],
    "col2": [121,142,144],
    "col3": [321,342,344],
})

print(df.head())

mf = df[['col1','col3']]

print(mf.head())
