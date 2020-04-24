import seaborn as sns; sns.set()  # for plot styling
from sklearn.cluster import KMeans
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
from sklearn.externals import joblib #jbolib

# input your training csv 
data = pd.read_csv("deta_sel_normalize.csv")

# choose the features column you want to use for training
feature_cols = ['0','1']

# you want all rows, and the feature_cols' columns
X = data[feature_cols].to_numpy()

kmeans = KMeans(n_clusters=2)
kmeans.fit(X)
y_kmeans = kmeans.predict(X)

# model is saved to  folder /save
joblib.dump(kmeans, 'save/kmeans.pkl')


#读取Model
# clf3 = joblib.load('save/clf.pkl')

#测试读取后的Model
# print(clf3.predict(X[0:1]))

 ######################## uncomment to make clustering plot ############## 
# plt.scatter(X[:, 0], X[:, 1], c=y_kmeans, s=50, cmap='rainbow')

# centers = kmeans.cluster_centers_
# plt.scatter(centers[:, 0], centers[:, 1], c='black', s=200, alpha=0.5);

# for adding labels
# fig = plt.figure()
# fig.suptitle('k-mean cluster', fontsize=20)
# plt.xlabel('num_different_services_accessed', fontsize=18)
# plt.ylabel('num_SYN_flags', fontsize=16)

# plt.show()


def train(feature_array):
    X = pd.DataFrame(feature_array)
    # 2,3,5,6,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24

    kmeans = KMeans(n_clusters=2, random_state=0).fit(X)

    val = kmeans.predict([predict])

    labels = kmeans.labels_

    indices = None
    if 1 in labels:
        # print (list(labels).index(1))
        indices = [i for i, x in enumerate(labels) if x == 1]

    return indices, val
