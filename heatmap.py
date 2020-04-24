import seaborn as sns; sns.set()  # for plot styling
from sklearn.cluster import KMeans
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt


data = pd.read_csv("normalize.csv")


data1 = data[['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20']] #Subsetting the data

print(data.describe())

cor = data1.corr() #Calculate the correlation of the above variables
sns.heatmap(cor, square = True) #Plot the correlation as heat map
plt.show()
#
#feature_cols = ['2','3', '5', '6', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17']