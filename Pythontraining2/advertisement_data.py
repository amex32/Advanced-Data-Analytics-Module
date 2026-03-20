import seaborn as sns
import matplotlib.pyplot as plt 
import pandas as pd
data={'advertisement':[1,2,3,4,6,7,9,10],
     'sales':[5,8,7,8,10,11,12,22],
     'temerature':[22,21,33,35,36,37,39,40]}
df=pd.DataFrame(data)
sns.scatterplot(x="advertisement",y="sales",data=df)
plt.show()

sns.scatterplot(x="advertisement",y="sales",data=df)
plt.title("advertisement and sales scattering chart")
plt.show()
data={'advertisement':[1,2,3,4,6,7,9,10],
     'sales':[5,8,7,8,10,11,12,22],
     'temerature':[22,21,33,35,16,21,20,20]}
coorelation_matrix=df.corr()
sns.heatmap(coorelation_matrix,annot=True,cmap='coolwarm',fmt='.2f')
plt.show()