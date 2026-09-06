import fitdecode
import pandas as pd

with fitdecode.FitReader('data/23567118490_ACTIVITY.fit') as fit:
    for g in fit:
        if isinstance(g, fitdecode.FitDataMessage) and g.name == 'record':
            print(g.fields[0][0])


for i in s.columns:
    print('stuff is surely happening')


print('Reading FIT file...')

