WAX_APPROVE_URL = "https://all-access.wax.io/"


# def name_to_whitelist_wax_name(name: str):
#     if name == "ogvy":
#         return "o.gvy"
#     if name == "b4nvi":
#         return name
#     elif name == "pyyfu":
#         return name
#     elif name == "o.gvy":
#         return "o.gvy"
#     elif name == "progk":
#         return name
#     elif name == "xvzwu":
#         return name
#     elif name == "jd1.2.c":
#         return "jd1.2.c"
#     elif name == "n11k2.c":
#         return "n11k2.c"
#     raise ValueError(name + " base_name_to_whitelist_name is not a base account from me")


# def base_wam_name_to_whitelist_name(name: str):
#     if name == "ogvy.wam":
#         return "o.gvy.wam"
#     if name == "b4nvi.wam":
#         return name
#     elif name == "pyyfu.wam":
#         return name
#     elif name == "o.gvy.wam":
#         return name
#     elif name == "progk.wam":
#         return name
#     elif name == "xvzwu.wam":
#         return name
#     elif name == "jd1.2.c.wam":
#         return name
#     elif name == "n11k2.c":
#         return name
#     else:
#         raise ValueError("base_wam_name_to_whitelist_name is not a base account from me")


def whitelist_wam_account(name, memo=None):
    whitelist = [
        "b4nvi.wam",

        "pyyfu.wam",
        "o.gvy.wam",
        "progk.wam",

        "xvzwu.wam",
        "jd1.2.c.wam",
        "n11k2.c.wam",

        "g32ke.c.wam",
        "oj3.e.c.wam",
        "e33ke.c.wam",
    ]
    if memo is None:
        return name in whitelist
    return name == "waxonbinance" and memo == 101666816

