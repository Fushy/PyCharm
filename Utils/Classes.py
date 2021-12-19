import random


class Coord:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "({}, {})".format(self.x, self.y)


class OpenPack:
    def __init__(self, pack_price: float, patterns: list[list[int, dict[str, float]]], alone: dict[str, float] = None,
                 bend: dict[str, list[str, int]] = None):
        """
        :type patterns
            Contient la liste des patterns d'ouverture des paquets
            Le premier element de la liste est le nombre de paquet ouvert
            Le deuxieme element de la liste est un dictionnaire contenant les odds par nom de rareté
        """
        self.bend = bend
        self.patterns = patterns
        self.pack_price = pack_price
        self.alone = alone
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
        # return "pack_open {} {}$ nft_open {}\nnft_per_pack {}\nnft_values {}\nnft_total {}".format(
        #     self.pack_open, self.total_price, self.nft_open, self.nft_per_pack, self.nft_values, self.nft_total)
        return "pack_open {} {}$ nft_open {}\nnft_per_pack {}\nnft_values {}\n".format(
            self.pack_open, self.total_price, self.nft_open, self.nft_per_pack, self.nft_values)

    def estimate(self, n):
        self.open_packs(n)
        self.craft()
        self.calculate()
        print(self)


if __name__ == '__main__':
    # say("go")
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
