# https://realpython.com/python-data-classes/#alternatives-to-data-classes
import random
from collections import namedtuple

# int("A", 16)

# >>> sample = [timedelta(seconds=generate_sleep_time(120)) for _ in range(200000)]
# >>> print(sum(sample, timedelta(0)) / len(sample))
# Faire un raise ou un return a l'endroi où le code est stoppé si le debug ne fonctionne plus alors que le run fonctionne

# TODO verif type
# if type(browser).__name__ != WebDriver.__name__ and type(browser).__name__ != WebElement.__name__:
#     error_text = "\tget_text_selector browser is not a good type {} {}".format(type(browser), WebDriver, WebElement)
#     if debug: print(error_text)
#     raise ValueError(error_text)

def a():
    # TODO pk des fois il y a (2, (1, 2))
    roles = ["ad", "top", "mid", "jungle"] * 2 + ["support"]
    choice_a = random.randint(0, len(roles))
    choice_b = random.randint(0, len(roles))
    return choice_a == choice_b and a() or choice_a, choice_b


# if __name__ == '__main__':
#     [print("a")]
#     [print("a")] * 3  # le resultat est calculé une fois puis est ajouté 3x, la fonction n'est exécuté qu'une seule fois


class RegularCard:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'(rank={self.rank!r}, suit={self.suit!r})')

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.rank, self.suit) == (other.rank, other.suit)


from dataclasses import dataclass


@dataclass
class DataClassCard:
    rank: str
    suit: str


if __name__ == '__main__':
    a: str = 5   #marche a lexe Python is and will always be a dynamically typed language
    NamedTupleCard = namedtuple('azerty', ['rank', 'suit'])
    NamedTupleCard.rank = 5
    NamedTupleCard.suit = "éa"

    print(NamedTupleCard)
    print(NamedTupleCard.rank)
    print(NamedTupleCard.suit)
    print(NamedTupleCard.mro())
