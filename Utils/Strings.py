def quote(obj, simple=False):
    return "\"" + str(obj) + "\"" if not simple else "'" + str(obj).replace("'", "\'") + "'"
