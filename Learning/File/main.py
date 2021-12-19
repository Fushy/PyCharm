def file_reader(file_name):
    file = open(file_name)
    lines = file.read().split("\n")
    for line in lines:
        print(line)








def file_reader_lazy(file_name):
    for line in open(file_name):
        print(line, end="")


