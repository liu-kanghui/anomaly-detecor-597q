import pandas as pd 

data = pd.read_csv("test.csv")

data = data.drop(['1','4' , '7'], axis=1)

data.to_csv('all_numeric.csv', index=False, float_format='%g')