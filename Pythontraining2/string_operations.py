a = " today the weather is clear"
print(len(a))
print(a.find('a')) #locating the index of a value 
print(a[-1]) #indexing string
print(a[1:-3]) #slicing string
print("a" in "da") #membership string
print(a.lower()) #lowercase string
print(a.upper()) #uppercase string
print(a[::-1]) #prints string in reverse order
print(a.capitalize()) #capitalize string
print(a.title()) #capitalize every word
print(a.strip()) #removes outer whitespaces 
print(a.replace("goo","ba")) #replaces one value with another value
print(a.count('a')) #counts the occurence of a value
print(a.startswith(" "))
print(a.lstrip().startswith(" "))
print(a.lstrip().startswith("t"))
print(a.rstrip().startswith("t"))
print(a.split())
