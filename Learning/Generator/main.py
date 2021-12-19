# Using yield will result in a generator object.
# Lors d'un next sur un generator, le code du générateur est parcouru du dernier yield rencontré jusqu'au prochain yield
# Si il n'y a plus de yield trouvé, jette une erreur
# Un generateur ne peut etre parcouru qu'une seule fois
from time import sleep
from typing import Iterable


def csv_reader(file_name):
    for line in open(file_name, "r"):
        yield line


def infinite_sequence():
    num = 0
    while True:
        num += 1
        yield num


def chained_list(array: Iterable):
    while True:
        for element in array:
            yield element


# print(csv_reader("../techcrunch.csv"))

generator = chained_list(("a", "b", "c"))

print(next(generator))
print(next(generator))
print(next(generator))
print(next(generator))

for e in generator:
    print(e)
    sleep(0.25)

