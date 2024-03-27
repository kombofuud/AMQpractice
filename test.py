import json
import fileinput
import random

numbers = [1]*10
for i in range(20):
    randomVar = random.choices(list(range(10)),weights = numbers)
    numbers[randomVar[0]]*=2

numbers.sort(reverse = True)
print(numbers)
