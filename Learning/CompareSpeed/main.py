import os

from Times import times


def count_lines_1(file_name):
    return sum((1 for _ in open(file_name)))


def count_lines_2(file_name):
    return sum([1 for _ in open(file_name)])


def count_lines_3(file_name):
    def aux():
        for line in open(file_name):
            yield line

    count = 0
    for _ in aux():
        count += 1
    return count


def count_lines_4(file_name):
    return len(open(file_name).read().split("\n"))


def count_lines_5(file_name):
    file = open(file_name)
    lines = file.read().split("\n")
    count = 0
    for _ in lines:
        count += 1
    return count


# times(lambda _: sum((i * 2 for i in range(1_000_000))))
# times(lambda _: sum([i * 2 for i in range(1_000_000)]))
# times(lambda _: sum((i ** 2 for i in range(1_000_000))))
# times(lambda _: sum([i ** 2 for i in range(1_000_000)]))
# times(count_lines_1, "../techcrunch.csv")
# times(count_lines_2, "../techcrunch.csv")
# times(count_lines_3, "../techcrunch.csv")
# times(count_lines_4, "../techcrunch.csv")
# times(count_lines_5, "../techcrunch.csv")
