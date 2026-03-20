import pandas as op
a = op.DataFrame([1,2,3],columns=['column_name'])    
print(a)

abc = {
    'name':['anmol','arti','anushka','kushagra','naveen','Mahima','Rishab'],
    'age':[16,54,34,23,15,24,43],
    'salary':[100000,10,5,900,233,0.5,7]

}

b = op.DataFrame(abc)
print(b)

print(b.head())

print(b.tail())


print(b.shape)

print(b.columns)

print(b.rename(columns={'salary':'payment'}))

print(b.rename(columns={'salary':'payment'},inplace=True))

print(b.describe())

print(b.to_csv("D:\Pythontraining2\data.csv"))

#print(b.to_csv("D:\Pythontraining2\data.csv"))

xyz = {
    'employee name':['anmol','arti','anushka','kushagra','naveen','Mahima','Rishab'],
    'age':[16,54,34,23,15,24,43],
    'salary':[100000,19000,50000,90000,25000,70000,45000],
    'employee id':['434','345','298','455','208','764','821',],
    'Date of Joining':['05-06-2004','15-08-2006','24-09-2010','05-12-2001','06-02-2018','05-03-2017','07-06-2020',],

}


d = op.DataFrame(abc)
print(d)

print(d.head())

print(d.tail())


print(d.shape)

print(d.columns)

print(d.rename(columns={'salary':'payment'}))

print(d.rename(columns={'salary':'payment'},inplace=True))

print(d.describe())

print(d.to_csv("employee_data.csv"))

print(d.to_csv("employee_data.csv",index=False))

print(op.read_csv(r"employee_data.csv"))




