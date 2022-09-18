import math
import random
from datetime import datetime
from time import sleep
from typing import Callable, Optional
from typing import Generic, Union
from typing import TypeVar

from Times import now
from Util import get_first_deeply_value

T = TypeVar("T")


class Condition:
    def __init__(self, **kwargs):
        self.update(kwargs=kwargs)

    def __str__(self):
        return str(self.__dict__)

    def update(self, **kwargs):
        self.__dict__.update(kwargs)

    def is_done(self):
        # print(za
        return all(self.__dict__.values())


class Point:
    """ Numerical points """
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x, self.y = x, y

    def __str__(self):
        return "({}, {})".format(self.x, self.y)

    def __repr__(self):
        return "{} {}".format(self.x, self.y)

    def distance(self, point):
        return math.sqrt((self.x - point.x) ** 2 + (self.y - point.y) ** 2)

    def slope(self, point: "Point") -> float:
        return (point.y - self.y) / (point.x - self.x)

    def intercept(self, point: "Point") -> float:
        return -self.slope(point) * self.x + self.y

    def equation(self, point: "Point") -> Callable[[int], float]:
        return lambda x: self.slope(point) * x + self.intercept(point)

    def points_between(self, point: "Point") -> set["Point"]:
        points = set()
        for x in range(min(self.x, point.x) + 1, abs(self.x - point.x)):
            points.add(Point(min(self.x, point.x) + x, point.y))
        for y in range(min(self.y, point.y) + 1, abs(self.y - point.y)):
            points.add(Point(point.y, min(self.y, point.y) + y))
        return points


class Rectangle:
    top_left: Point
    right_bottom: Point
    x0: int
    y0: int
    x1: int
    y1: int
    w: int
    h: int

    def __init__(self,
                 x0: Point | int,
                 y0: Point | int,
                 x1: Optional[int] = None,
                 y1: Optional[int] = None,
                 w=None,
                 h=None):
        if type(x0) is Point and type(y0) is Point:
            self.top_left = x0
            self.right_bottom = y0
            self.x0 = self.top_left.x
            self.y0 = self.top_left.y
            self.x1 = self.right_bottom.x
            self.y1 = self.right_bottom.y
            self.w = self.x1 - self.x0
            self.h = self.y1 - self.y0
        elif type(x0) is int and type(y0) is int and w is not None and h is not None:
            self.top_left = Point(x0, y0)
            self.right_bottom = Point(x0 + w, y0 + h)
            self.x0 = x0
            self.y0 = y0
            self.x1 = x0 + w
            self.y1 = y0 + h
            self.w = w
            self.h = h
        elif type(x0) is int and type(y0) is int and type(x1) is int and type(y1) is int:
            self.top_left = Point(x0, y0)
            self.right_bottom = Point(x1, y1)
            self.x0 = x0
            self.y0 = y0
            self.x1 = x1
            self.y1 = y1
            self.w = x1 - x0
            self.h = y1 - y0


class DatedObj(Generic[T]):
    def __init__(self, obj: T = None):
        if obj is None:
            self.dated = None
            self.value = None
        else:
            self.dated: T = datetime.now()
            self.value: datetime = obj

    def __lt__(self, other):
        value = get_first_deeply_value(self.value)
        other_value = get_first_deeply_value(other.value)
        if value < other_value:
            return True
        elif value == other_value and self.dated < other.dated:
            return True
        return False

    def __gt__(self, other):
        value = get_first_deeply_value(self.value)
        other_value = get_first_deeply_value(other.value)
        if value > other_value:
            return True
        elif value == other_value and self.dated > other.dated:
            return True
        return False

    def __repr__(self):
        return "({}: {:.2f}s)".format(self.value, (now() - self.dated).total_seconds())


# le type doit pouvoir déduire min max et sum, si l'objet est un iterable, la regle est que le premier index recursif soit la valeur
class DatedLists:
    def __init__(self, timer: float):
        self.time_interval: float = timer  # En secondes
        self.objs: list[DatedObj[T]] = []  # Du plus ancien au plus récent
        self.is_updated: bool = False
        self.min: Union[DatedObj[T], None] = None
        self.max: Union[DatedObj[T], None] = None
        self.sum: T = 0

    def __len__(self):
        return len(self.objs)

    def __repr__(self):
        return self.info() + " : " + ", ".join([repr(obj) for obj in self.objs])

    def info(self):
        return (self.update() and "f" or "") + "|{}-{}| {} {}s ".format(self.min, self.max,
                                                                        self.sum,
                                                                        self.time_interval)

    def put(self, obj: T):
        dated = DatedObj(obj)
        if self.min is None or self.max is None:
            self.min = dated
            self.max = dated
        elif obj < self.min.value:
            self.min = dated
        elif obj < self.max.value:
            self.max = dated
        self.objs.append(dated)
        self.sum += get_first_deeply_value(obj)
        self.is_updated = False

    def first(self):
        return self.objs[0]

    def last(self):
        return self.objs[-1]

    def index(self, n):
        return self.objs[n]

    # On parcours toutes les valeurs outdated et on les supprime
    # N'utiliser qu'avant le moment ou on en à besoin que la liste soit mise à jour
    def remove_outdated(self, fun=None, value=None):
        i = 0
        now = datetime.now()
        for dated_obj in self.objs:
            if (now - dated_obj.dated).total_seconds() <= self.time_interval:
                break
            self.sum -= get_first_deeply_value(dated_obj.value)
            if value is not None:
                value = fun(value, dated_obj.value)
            i += 1
        del self.objs[:i]
        self.is_updated = True
        if self.min is not None and len(self.objs) and (now - self.min.dated).total_seconds() > self.time_interval:
            self.min = min(self.objs)
        if self.max is not None and len(self.objs) and (now - self.max.dated).total_seconds() > self.time_interval:
            self.max = max(self.objs)
        return value

    def update(self):
        if self.is_updated is False:
            self.remove_outdated()
            return True
        return False

    def sum_update(self):
        self.update()
        return self.sum

    def values(self):
        self.update()
        return self.objs


class OpenPack:
    def __init__(self, pack_price, patterns, alone=None, bend=None):
        """
        :type patterns
            Contient la liste des patterns d'ouverture des paquets
            Le premier element de la liste est le nombre de paquet ouvert
            Le deuxieme element de la liste est un dictionnaire contenant les odds par nom de rareté
        """
        self.pack_price: float = pack_price
        self.patterns: list[list[int, dict[str, float]]] = patterns
        self.alone: dict[str, float] = alone
        self.bend: dict[str, list[str, int]] = bend
        self.pack_open = 0
        self.total_price = 0
        self.nft_open = {}
        self.nft_total = {}
        self.nft_per_pack = {}
        self.nft_values = {}
        # self.rarity_odds = sorted([(rarity, odds) for (rarity, (odds, bend)) in
        #                            self.rarity_odds_n_bend.items()], key=lambda x: x[1])

    def open_packs(self, n):
        i = 0
        while i < n:
            self.pack_open += 1
            for j in range(len(self.patterns)):
                pattern = self.patterns[j]
                pack_to_open, rarity_n_odds = pattern
                for _ in range(pack_to_open):
                    rng = random.random() * 100
                    sum_luck = 0
                    for name, odds in rarity_n_odds.items():
                        sum_luck += odds
                        if name not in self.nft_open:
                            self.nft_open[name] = 0
                        if rng <= sum_luck:
                            self.nft_open[name] += 1
                            break
            if self.alone is not None:
                for name, odds in self.alone.items():
                    rng = random.random() * 100
                    if name not in self.nft_open:
                        self.nft_open[name] = 0
                    if rng <= odds:
                        self.nft_open[name] += 1
                        if name == "extra_pack":
                            n += 1
                            self.total_price -= self.pack_price
            self.total_price += self.pack_price
            i += 1
        for name, amount in self.nft_open.items():
            self.nft_total[name] = amount

    def craft(self):
        if self.bend is None:
            return
        for rarity, (rarity_needed, order, amount_needed) in self.bend.items():
            if rarity_needed not in self.nft_total:
                if rarity in self.nft_open:
                    self.nft_total[rarity_needed] = self.nft_open[rarity_needed]
                else:
                    self.nft_total[rarity_needed] = 0
            if rarity not in self.nft_total:
                self.nft_total[rarity] = 0
            # if rarity in self.nft_open:
            #     self.nft_total[rarity] += self.nft_open[rarity]
            self.nft_total[rarity] += int(self.nft_total[rarity_needed] / amount_needed)

    def calculate(self):
        for rarity, count in self.nft_total.items():
            if count == 0:
                self.nft_per_pack[rarity] = -1
                price_value = 0
                packet_value = 0
            else:
                price_value = self.total_price / count
                packet_value = (self.total_price / count) / self.pack_price
            if packet_value != int(packet_value):
                packet_value += 1
            packet_value = int(packet_value)
            self.nft_per_pack[rarity] = round(price_value, 2), packet_value
        first_rarity, first_order, first_rarity_needed = self.get_order_rarity(-1)
        # print(first_rarity)
        for i in range(len(set(self.bend)) + 1):
            current_rarity, current_order, rarity_needed = self.get_order_rarity(first_order - i)
            # print("current_rarity", current_rarity)
            # print("-")
            cursor_rarity = first_rarity
            self.nft_values[current_rarity] = self.nft_per_pack[first_rarity][0]
            j = 0
            while cursor_rarity != current_rarity:
                # print("rarity_cursor", cursor_rarity)
                if cursor_rarity not in self.bend:
                    continue
                rarity_needed_to_craft, order, amount = self.bend[cursor_rarity]
                # print("amount", amount)
                self.nft_values[current_rarity] /= amount
                cursor_rarity, cursor_order, cursor_rarity_needed = self.get_order_rarity(first_order - 1 - j)
                j += 1
            self.nft_values[current_rarity] = round(self.nft_values[current_rarity], 2)
            # print()
        self.nft_per_pack = list(
            map(
                lambda x: "{} {}$ {}p".format(x[0], x[1][0], x[1][1]),
                sorted(self.nft_per_pack.items(), key=lambda x: x[1][0], reverse=True)))

    def get_order_rarity(self, n):
        lst = []
        bend = sorted(list(map(lambda x: (x[0], x[1][1], x[1][0]), self.bend.items())), key=lambda x: x[1])
        for rarity, order, rarity_needed in bend:
            lst.append((rarity, order, rarity_needed))
        for rarity, order, rarity_needed in lst:
            if rarity_needed not in self.bend:
                lst = [(rarity_needed, lst[0][1] - 1, "")] + lst
        return lst[n]

    def __str__(self):
        self.total_price = round(self.total_price, 2)
        # return "pack_open {} {}$ nft_open {}\nnft_per_pack {}\nnft_values {}\nnft_total {}".date_format(
        #     self.pack_open, self.total_price, self.nft_open, self.nft_per_pack, self.nft_values, self.nft_total)
        return "pack_open {} {}$ nft_open {}\nnft_per_pack {}\nnft_values {}\n".format(
            self.pack_open, self.total_price, self.nft_open, self.nft_per_pack, self.nft_values)

    def estimate(self, n):
        self.open_packs(n)
        self.craft()
        self.calculate()
        print(self)


if __name__ == '__main__':
    a = Point(0, 0)
    b = Point(5, 5)
    print(a, b)
    print(a.slope(b))
    print(a.intercept(b))
    print(a.equation(b)(2))
    print(a.points_between(b))

    a = DatedLists(6)
    a.put((1, "point"))
    sleep(1)
    a.put((2, "b"))
    sleep(1)
    a.put((3, "c"))
    sleep(1)
    a.put((4, "d"))
    sleep(1)
    a.put((5, "e"))
    sleep(1)
    a.put((6, "f"))
    sleep(1)
    a.put((7, "g"))
    sleep(1)
    a.put((8, "h"))
    sleep(1)
    a.put((9, "i"))
    sleep(1)
    a.put((10, "j"))
    print(a.first())
    # print("min", point.min)
    # print()
    # print("max", point.max)
    # print()
    # print("sum", point.sum)
    # print()
    print(a)
    # print(point)

    # godslegend = OpenPack(
    #     9.99,
    #     [
    #         [2, {"Base": 56, "Rare": 28, "Epic": 10, "Legendary": 4, "Mythic": 0, "Divine": 0, "Eternal": 0}],
    #         [1, {"Rare": 56 + 28, "Epic": 10, "Legendary": 4, "Mythic": 0, "Divine": 0, "Eternal": 0}],
    #     ], {"extra_pack": 2},
    #     bend={"Rare": ["Base", 1, 5],
    #           "Epic": ["Rare", 2, 3],
    #           "Legendary": ["Epic", 3, 3],
    #           "Mythic": ["Legendary", 4, 3],
    #           "Divine": ["Mythic", 5, 3],
    #           "Eternal": ["Divine", 6, 3]})
    # realmnftgame = OpenPack(
    #     24.95,
    #     [
    #         [5, {"1 star": 26, "2 star": 35, "3 star": 32, "4 star": 5.5, "5 star": 1.5}]
    #     ], {"beta_access": 1.5},
    #     bend={"2 star": ["1 star", 1, 3],
    #           "3 star": ["2 star", 2, 3],
    #           "4 star": ["3 star", 3, 3],
    #           "5 star": ["4 star", 4, 3]})
    # godslegend.estimate(1_000_000)
    # realmnftgame.estimate(1_000_000)
