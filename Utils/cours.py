# https://realpython.com/python-data-classes/#alternatives-to-data-classes
from collections import namedtuple

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
