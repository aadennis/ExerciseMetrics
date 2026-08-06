import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

df = pd.read_csv('data/output/3August_ACTIVITY-fit.csv')

cols = [
    "speed",
    "cadence_spm",
    "step_length",
    "stance_time",
    "vertical_oscillation",
    "vertical_ratio"
]

print(df[cols].corr().round(3))

print(df[cols].corr()["speed"].sort_values(ascending=False))



sns.pairplot(
    df[["speed", "step_length", "cadence_spm", "stance_time"]],
    corner=True
)
plt.show()



X = df[['step_length', 'cadence_spm']]
y = df['speed']

model = LinearRegression()
model.fit(X, y)

print("R²:", model.score(X, y))
print("Coefficients:", model.coef_)

print(df[['speed',
          'step_length',
          'cadence_spm',
          'stance_time']].corr().round(3))

print(df['cadence_spm'].describe())

