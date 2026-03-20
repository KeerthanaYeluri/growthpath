class Person():
    def __init__(self, name, age):
        self.name = name
        self.age = age
p1=Person("John", 22)
sentence=f'my name is {p1.name} and my age is {p1.age} years old'
print(sentence)
