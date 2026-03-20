import pandas as p
import matplotlib.pyplot as m

data = {
    "Name": ["Anmol",'Anurag','Raja','Rohan'],
    "Marks":[95,95,89,34],
    "Year" :["4th",'3rd','2nd',"1st"]
}

a = p.DataFrame(data)
print(a)

m.figure(figsize=(8, 6))

for c in a['Year'].unique():
    b = a[a['Year'] == c]
    m.scatter(b['Name'], b['Marks'], label=c)

m.xlabel('Students')
m.ylabel('Marks')
m.title('College Students Marks by Year')
m.legend(title='Year')


m.show()