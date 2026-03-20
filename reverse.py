# reverse a string
import re

s="keerthana"
print(s[::-1])


# palindrome
s="madam"
print(s == s [::-1])


# printing vowels letters
s="Renu"
vowels="".join(r for r in s if r in "aeiou")
print(vowels)

#counting no.of vowels
s="renu"
count=sum(1 for c in s if c in "aeiou")
print(count)



text = "Order ID: 98765"
numbers = re.findall(r'\d+', text)
print(numbers[0])














