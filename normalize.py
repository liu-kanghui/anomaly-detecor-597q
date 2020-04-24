from sklearn import preprocessing
import pandas as pd

data = pd.read_csv("data_sel.csv")
x = data.values #returns a numpy array
min_max_scaler = preprocessing.MinMaxScaler()
x_scaled = min_max_scaler.fit_transform(x)
df = pd.DataFrame(x_scaled)


df.to_csv('deta_sel_normalize.csv', index=False, float_format='%g')