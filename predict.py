import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
from sklearn.externals import joblib #jbolib


# load previous trained model
kmean = joblib.load('save/kmeans.pkl')

# input your predict csv 
data = pd.read_csv("deta_sel_normalize.csv")

# choose the features column you want to use for predicting
feature_cols = ['0','1']

# you want all rows, and the feature_cols' columns
X = data[feature_cols].to_numpy()

# replace the length with how many prediction you want to make from X 

length = 100
Y = np.arange(length)

predict = kmean.predict(X)

np.savetxt("predict.csv", predict[0:length], delimiter=",", fmt ='%.0f')

plt.plot(Y, predict[1:length], 'go') 

plt.show()