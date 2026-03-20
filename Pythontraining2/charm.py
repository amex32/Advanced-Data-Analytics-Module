import matplotlib.pyplot as plt

x = [1,2,3,4,5]
y = [10,20,25,30,40]

#plt.plot(x,y)
#plt.show()

'''plt.figure(figsize=(4,3))

plt.plot(x,y,color='blue',marker='o',linestyle='--',linewidth=2,markersize=12)

plt.title("St. Andrews Institute of Technology and Management")
plt.xlabel("number")
plt.ylabel("Data Analytics")
plt.show()'''

'''x = [1,2,3,4,5]
y = [10,20,30,40,50]
z = [20,40,60,80,100]
plt.plot(x,y,label="Sales 2025")
plt.plot(x,z,label="Sales 2026")
plt.title("YoY Sales")
plt.xlabel("Months")
plt.ylabel("Sales")

plt.legend()
plt.show()'''

'''x = ['A','B','C','D','E']
Y = [10,20,30,40,50]

plt.title("YoY Sales")
plt.xlabel("Months")
plt.ylabel("Sales")

plt.bar(x,y,color='Black')
#plt.title('Bar Chart Example')
plt.show()'''

'''import random
a = [random.randint(1,20) for _ in range(500)]

plt.hist(a,bins=20,color="black",data="45")
plt.title("Histogram")
plt.show()'''

x = [1, 2, 3, 4, 5]
y1 = [100, 2, 200, 100, 1000]
y2 = [10, 500, 40, 50, 60]
y3 = [1000, 200, 300, 400, 500]
plt.figure(figsize=(12, 8))
plt.subplot(2, 2, 1)
plt.plot(x, y1, label = 'sales 2024', color = 'red', marker = 'o', linestyle = '--', linewidth = 2, markersize = 8)
plt.title("Line Chart")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.legend()
plt.subplot(2, 2, 2)
plt.bar(x,y1, color='blue')
plt.title("Bar Chart")
plt.subplot(2, 2, 3)
categories = ['A', 'B', 'C', 'D', 'E']
sales = [100, 600, 200, 100, 1000]
plt.pie(sales, labels=categories, autopct='%1.1f%%', startangle=140)
plt.title("Pie Chart")
plt.subplot(2, 2, 4)
plt.scatter(y1, y2, color='black', marker='o', s=100)
plt.title("Scatter Plot")
plt.tight_layout()
plt.show()

import pandas as pd
data = {
    'Month' : ['Jan','Feb','Mar','Apr'],
    'Sales' : [12000,11000,13000,25000],
}

a = pd.DataFrame(data)




