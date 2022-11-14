import heapq
import math
import random
from collections import defaultdict
from datetime import datetime
from time import sleep
from typing import Callable, Optional
from typing import Generic, Union
from typing import TypeVar

from screeninfo import Monitor

from Times import now

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

    def __init__(self, x: int, y: int = None):
        if type(x) is not int and type(x) is not float:
            x, y = x
        self.x, self.y = x, y

    def __str__(self):
        return "({}, {})".format(self.x, self.y)

    def __repr__(self):
        return "{} {}".format(self.x, self.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, x):
        return Point(self.x * x, self.y * x)

    def __truediv__(self, x):
        return Point(self.x / x, self.y / x)

    def __iter__(self):
        for p in [self.x, self.y]:
            yield p

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        if type(other) is tuple or type(other) is list:
            x, y = other[0], other[1]
        else:
            x, y = other.x, other.y
        return self.x == x and self.y == y

    def distance(self, point):
        return math.sqrt((self.x - point.x) ** 2 + (self.y - point.y) ** 2)

    def distance_manhattan(self, point):
        return abs(point.x - self.x) + abs(point.y - self.y)

    def slope(self, point: "Point") -> float:
        """ Return number of y for one x """
        return (point.y - self.y) / (point.x - self.x)

    def intercept(self, point: "Point") -> float:
        """ Return y position for x=0
            f(0) = this = y"""
        return self.slope(point) * -self.x + self.y

    def equation(self, point: "Point") -> Callable[[int], float]:
        # f(x) = ax + b = this = y
        return lambda x: self.slope(point) * x + self.intercept(point)

    def points_between(self, point: "Point") -> set["Point"]:
        points = set()
        for x in range(min(self.x, point.x) + 1, abs(self.x - point.x)):
            points.add(Point(min(self.x, point.x) + x, point.y))
        for y in range(min(self.y, point.y) + 1, abs(self.y - point.y)):
            points.add(Point(point.y, min(self.y, point.y) + y))
        return points

    # def bresenham(self, point: "Point", lower_y_towards_higher_y=True) -> list["Point"]:
    #     a, b = self, point
    #     if lower_y_towards_higher_y and a.y < b.y:
    #         a, b = b, a
    #     x0 = a.x
    #     y0 = a.y
    #     x1 = b.x
    #     y1 = b.y
    #     dx = x1 - x0
    #     dy = y1 - y0
    #     x_sign = 1 if dx > 0 else -1
    #     y_sign = 1 if dy > 0 else -1
    #     dx = abs(dx)
    #     dy = abs(dy)
    #     if dx > dy:
    #         xx, xy, yx, yy = x_sign, 0, 0, y_sign
    #     else:
    #         dx, dy = dy, dx
    #         xx, xy, yx, yy = 0, y_sign, x_sign, 0
    #     d = 2 * dy - dx
    #     y = 0
    #     points = []
    #     for x in range(dx + 1):
    #         points.append(Point(x0 + x * xx + y * yx, y0 + x * xy + y * yy))
    #         if d >= 0:
    #             y += 1
    #             d -= 2 * dx
    #         d += 2 * dy
    #     # if lower_y_towards_higher_y and a.y < b.y:
    #     #     return points[::-1]
    #     return points

    def bresenham(self, point: "Point", lower_y_towards_higher_y=False) -> list["Point"]:
        """ A close approximation to a straight line between two points.
            As it uses only integer addition, subtraction and bit shifting, all of which are very cheap operations"""
        print("bresenham", self, point)
        p1, p2 = self, point
        reverse = False
        if lower_y_towards_higher_y and p2.y < p1.y:
            reverse = True
            p1, p2 = p2, p1
        x0, y0, x1, y1 = p1.x, p1.y, p2.x, p2.y
        delta_x, delta_y = abs(x1 - x0), abs(y1 - y0)
        sign_x, sign_y = 1 if x0 < x1 else -1, 1 if y0 < y1 else -1
        delta_diff = delta_x - delta_y

        points = []
        cursor_x = x0
        cursor_y = y0
        while True:
            points.append(Point(cursor_x, cursor_y))
            if cursor_x == x1 and cursor_y == y1:
                break
            err = 2 * delta_diff
            if err > -delta_y:
                delta_diff -= delta_y
                cursor_x += sign_x
            if err < delta_x:
                delta_diff += delta_x
                cursor_y += sign_y
        if reverse:
            return points[::-1]
        return points


def bresenham2(start, end):
    """
    Bresenham's Line Generation Algorithm
    https://www.youtube.com/watch?v=76gp2IAazV4
    """
    # step 1 get end-points of line
    (x0, y0) = start
    (x1, y1) = end
    # step 2 calculate difference
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    m = dy / dx
    # step 3 perform test to check if pk < 0
    flag = True
    line_pixel = []
    line_pixel.append(Point(x0, y0))
    step = 1
    if x0 > x1 or y0 > y1:
        step = -1
    mm = False
    if m < 1:
        x0, x1, y0, y1 = y0, y1, x0, x1
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        mm = True
    p0 = 2 * dx - dy
    x = x0
    y = y0
    for i in range(abs(y1 - y0)):
        if flag:
            x_previous = x0
            p_previous = p0
            p = p0
            flag = False
        else:
            x_previous = x
            p_previous = p
        if p >= 0:
            x = x + step
        p = p_previous + 2 * dx - 2 * dy * (abs(x - x_previous))
        y = y + 1
        if mm:
            line_pixel.append(Point(y, x))
        else:
            line_pixel.append(Point(x, y))
    return line_pixel


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
        x0, y0, x1, y1, w, h = map(lambda x: int(x) if type(x) == float else x, (x0, y0, x1, y1, w, h))
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
        else:
            raise AttributeError("init Rectangle not defined")

    def move_origin(self, point: Point):
        x0 = self.x0 + point.x
        y0 = self.y0 + point.y
        x1 = self.x1 + point.x
        y1 = self.y1 + point.y
        return Rectangle(x0, y0, x1, y1)


import Util


class DatedObj(Generic[T]):
    def __init__(self, obj: T = None):
        if obj is None:
            self.dated = None
            self.value = None
        else:
            self.dated: T = datetime.now()
            self.value: datetime = obj

    def __lt__(self, other):
        value = Util.get_first_deeply_value(self.value)
        other_value = Util.get_first_deeply_value(other.value)
        if value < other_value:
            return True
        elif value == other_value and self.dated < other.dated:
            return True
        return False

    def __gt__(self, other):
        value = Util.get_first_deeply_value(self.value)
        other_value = Util.get_first_deeply_value(other.value)
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
        self.sum += Util.get_first_deeply_value(obj)
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
            self.sum -= Util.get_first_deeply_value(dated_obj.value)
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


def test_DatedLists():
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


def test_pack():
    godslegend = OpenPack(
        9.99,
        [
            [2, {"Base": 56, "Rare": 28, "Epic": 10, "Legendary": 4, "Mythic": 0, "Divine": 0, "Eternal": 0}],
            [1, {"Rare": 56 + 28, "Epic": 10, "Legendary": 4, "Mythic": 0, "Divine": 0, "Eternal": 0}],
        ], {"extra_pack": 2},
        bend={"Rare": ["Base", 1, 5],
              "Epic": ["Rare", 2, 3],
              "Legendary": ["Epic", 3, 3],
              "Mythic": ["Legendary", 4, 3],
              "Divine": ["Mythic", 5, 3],
              "Eternal": ["Divine", 6, 3]})
    realmnftgame = OpenPack(
        24.95,
        [
            [5, {"1 star": 26, "2 star": 35, "3 star": 32, "4 star": 5.5, "5 star": 1.5}]
        ], {"beta_access": 1.5},
        bend={"2 star": ["1 star", 1, 3],
              "3 star": ["2 star", 2, 3],
              "4 star": ["3 star", 3, 3],
              "5 star": ["4 star", 4, 3]})
    godslegend.estimate(1_000_000)
    realmnftgame.estimate(1_000_000)


grid = """.x...........
.............
.............
M..x.o.o.x..W
...x.o.o.x...
....o...o....
.x.oo...oo.x.""".replace("\n", "")


# grid = {(0, 0): 1, (1, 0): 0, (2, 0): 0, (3, 0): 0, (4, 0): 0, (5, 0): 0, (6, 0): 0, (7, 0): 0, (8, 0): 0, (9, 0): 0, (10, 0): 0, (11, 0): 0, (12, 0): 1, (0, 1): 0, (1, 1): 0, (2, 1): 0, (3, 1): 1, (4, 1): 6, (5, 1): 0, (6, 1): 0, (7, 1): 0, (8, 1): 0, (9, 1): 1, (10, 1): 0, (11, 1): 0, (12, 1): 0, (0, 2): 0, (1, 2): 0, (2, 2): 1, (3, 2): 0, (4, 2): 0, (5, 2): 0, (6, 2): 0, (7, 2): 0, (8, 2): 5, (9, 2): 0, (10, 2): 1, (11, 2): 0, (12, 2): 0, (0, 3): 0, (1, 3): 0, (2, 3): 0, (3, 3): 0, (4, 3): 0, (5, 3): 3, (6, 3): 6, (7, 3): 5, (8, 3): 0, (9, 3): 4, (10, 3): 0, (11, 3): 0, (12, 3): 0, (0, 4): 1, (1, 4): 0, (2, 4): 0, (3, 4): 0, (4, 4): 2, (5, 4): 3, (6, 4): 0, (7, 4): 6, (8, 4): 5, (9, 4): 0, (10, 4): 6, (11, 4): 0, (12, 4): 1, (0, 5): 0, (1, 5): 0, (2, 5): 0, (3, 5): 0, (4, 5): 3, (5, 5): 0, (6, 5): 0, (7, 5): 0, (8, 5): 6, (9, 5): 0, (10, 5): 0, (11, 5): 0, (12, 5): 0, (0, 6): 1, (1, 6): 0, (2, 6): 6, (3, 6): 0, (4, 6): 0, (5, 6): 0, (6, 6): 0, (7, 6): 0, (8, 6): 0, (9, 6): 0, (10, 6): 0, (11, 6): 0, (12, 6): 1}


class Node:
    def __init__(self):
        self.visited = False
        self.opened = False
        self.pos = None
        self.parent = None
        self.distance = None
        self.walked = False

    def __lt__(self, other):
        return self.distance < other.distance

    def __hash__(self):
        return hash(self.pos)

    def __eq__(self, other):
        return self.pos == other.pos

    def __repr__(self):
        return "({}, {}) {}".format(self.pos.x, self.pos.y, "+")


def pathfinder(start: Point, end: Point, grid: dict[Point, int]) -> list[Point]:
    def backtrace(node: Node):
        path = [node.pos]
        while node.parent:
            node = node.parent
            path.append(node.pos)
        path.reverse()
        return path

    def find_neighbors(point, length=1, diagonal=False):
        neighbors = [(x, y) for x in range(-length, length + 1) for y in range(-length, length + 1)]
        neighbors_walkable = []
        for x, y in neighbors:
            check_point = Point(point.x + x, point.y + y)
            if check_point != point:
                if diagonal:
                    neighbors_walkable.append(check_point)
                elif not diagonal and (point.x == check_point.x or point.y == check_point.y):
                    neighbors_walkable.append(check_point)
        return neighbors_walkable

    def process_node(node: Node, parent: Node):
        if not node.opened:
            if node.distance is None:
                node.distance = node.pos.distance_manhattan(end)
            node.parent = parent
            if not node.opened:
                heapq.heappush(open_list, node)
                node.opened = True
            else:
                open_list.remove(node)
                heapq.heappush(open_list, node)

    def check_neighbors():
        node = heapq.nsmallest(1, open_list)[0]
        if node.pos == end:
            return backtrace(nodes[end])
        open_list.remove(node)
        nodes[node.pos].visited = True
        neighbors = find_neighbors(node.pos)
        for pos in neighbors:
            neighbor = nodes[pos]
            neighbor.pos = pos
            if neighbor.visited or neighbor.pos not in grid or (grid[neighbor.pos] != 0 and neighbor.pos != end):
                continue
            process_node(neighbor, node)
        return None

    root = Node()
    root.pos = start
    nodes: dict[Point, Node] = defaultdict(lambda: Node())
    nodes[root.pos].opened = True
    open_list = [root]
    while len(open_list) > 0:
        path = check_neighbors()
        if path:
            return path
    return []


def test_path():
    matrix = list(map(lambda x: 0 if x == "." else random.randint(1, 5), grid))
    matrix = [matrix[13 * i:13 * (i + 1)] for i in range(7)]
    # grid_dict = {Point(x, y): matrix[y][x] for y in range(len(matrix)) for x in range(len(matrix[0]))}
    # print(grid_dict)
    # print(pathfinder(a, b, grid))
    # grid = Grid(matrix=matrix)
    # start = grid.node(0, 3)
    # end = grid.node(4, 3)
    # finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
    # path, runs = finder.find_path(start, end, grid)
    # print(path, 'operations:', runs, 'path length:', len(path))
    # print(grid.grid_str(path=path, start=start, end=end))
    # print(grid)


def test_point():
    # (6, 5)(8, 1)
    # [6 5, 7 4, 7 3, 8 2, 8 1]
    a = Point(6, 5)
    b = Point(8, 1)
    print(a.bresenham(b, True))
    print(a.bresenham(b))
    # [9 2, 8 2, 7 2, 6 3, 5 3]
    # a = Point(9, 2)
    # b = Point(5, 3)
    # print(a.bresenham(b, True))
    print(a.slope(b))
    print(a.intercept(b))
    print(a.equation(b)(0))
    # print(a.points_between(b))
    # print(a.distance_manhattan(b))
    # print(a.bresenham(b, True))


class hi:
    def __init__(self):
        self.a = None

    def __repr__(self):
        return "{}".format(self.a)


if __name__ == '__main__':
    test_point()
    # hi = hi()
    # hi_dict = {hi: 0}
    # for k, _ in hi_dict.items():
    #     print(k)
    # print(hi)
    # hi.a = [1, 2, 3]
    # for k, _ in hi_dict.items():
    #     print(k)
    # print(hi)
    # a = namedtuple('Student', ['name', 'age', 'DOB'])
