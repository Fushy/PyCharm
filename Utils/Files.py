import os


def count_lines(file_name):
    return sum([1 for _ in open(file_name)])


def file_exist(path):
    return os.path.exists(path)

def get_current_files():
    cwd = os.getcwd()  # Get the current working directory (cwd)
    files = os.listdir(cwd)  # Get all the files in that directory
    # print("Files in %r: %s" % (cwd, files))
    return files


def file_get_1st_line(file):
    file = open(file, "r")
    line = file.readline()
    file.close()
    return line


def file_write_1st_line(file, value):
    file = open(file, "w")
    file.write(str(value))
    file.close()


def file_append(file, value):
    file = open(file, "a+")
    file.write(value)
    file.close()


def output(*args, log_file=None, end="\n"):
    concat_args = " ".join([arg for arg in args]) + end
    if log_file is None:
        print(concat_args)
    else:
        file = open(log_file, "a+")
        file.write(concat_args)
        file.close()

