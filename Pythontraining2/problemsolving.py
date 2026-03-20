#Q1. Print numbers from 1 to 10 using a for loop

for i in range(1,11): 
    print(i)

#Q2. print numbers from 10 down to 1 using a while loop

i = 10
while i >= 1:
    print(i)
    i = i - 1

#print the multiplication table of 5 using a for loop

a = 5
for i in range(1,11):
    print(5,"X" ,i ,"=", i*5)

#write a program that prints only even numbers between 1 and 20 using a while loop

i = 2
while i<=20:
    print(i)   
    i = i+2    

#Make a pattern using nested loop

i = 10
for i in range(1,i+1):
    for j in range(i):
        print("*",end=" ")
    print()    

import pandas as op
a = op.DataFrame([1,2,3],columns=['column_name'])    
print(a)














