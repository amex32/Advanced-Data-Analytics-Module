# ==============================
# IMPORT LIBRARIES
# ==============================
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==============================
# NUMPY (Numerical Operations)
# ==============================
print("----- NUMPY -----")

# Create array
arr = np.array([10, 20, 30, 40, 50])
print("Array:", arr)

# Basic operations
print("Mean:", np.mean(arr))
print("Sum:", np.sum(arr))
print("Max:", np.max(arr))
print("Min:", np.min(arr))

# Reshape array
arr2 = np.arange(1, 10).reshape(3, 3)
print("2D Array:\n", arr2)

# ==============================
# PANDAS (Data Handling)
# ==============================
print("\n----- PANDAS -----")

# Create DataFrame
data = {
    "Name": ["A", "B", "C", "D", "E"],
    "Marks": [85, 90, 78, 92, 88],
    "Age": [20, 21, 19, 22, 20]
}

df = pd.DataFrame(data)

# Display data
print("DataFrame:\n", df)

# Basic operations
print("\nHead:\n", df.head())
print("\nInfo:")
print(df.info())

print("\nDescribe:\n", df.describe())

# Filtering
print("\nStudents with Marks > 85:\n", df[df["Marks"] > 85])

# Add new column
df["Grade"] = ["B", "A", "C", "A", "B"]
print("\nUpdated DataFrame:\n", df)

# ==============================
# MATPLOTLIB (Visualization)
# ==============================
print("\n----- MATPLOTLIB -----")

# Line Plot
plt.figure()
plt.plot(df["Name"], df["Marks"])
plt.title("Marks Line Chart")
plt.xlabel("Students")
plt.ylabel("Marks")
plt.show()

# Bar Chart
plt.figure()
plt.bar(df["Name"], df["Marks"])
plt.title("Marks Bar Chart")
plt.xlabel("Students")
plt.ylabel("Marks")
plt.show()

# Scatter Plot
plt.figure()
plt.scatter(df["Age"], df["Marks"])
plt.title("Age vs Marks")
plt.xlabel("Age")
plt.ylabel("Marks")
plt.show()

# Histogram
plt.figure()
plt.hist(df["Marks"])
plt.title("Marks Distribution")
plt.xlabel("Marks")
plt.ylabel("Frequency")
plt.show()