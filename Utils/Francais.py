from collections import OrderedDict

""" https://www.scribbr.fr/elements-linguistiques/determinant/
Le déterminant permet de présenter le nom.
Il le précède et compose avec lui le groupe nominal.
Un adjectif ou un autre déterminant peuvent se placer entre le déterminant et le nom.
"""
déterminants = OrderedDict({
    "articles": {
        "indéfinis": ["un", "une", "des"],
        "définis": ["le", "l’", "la", "les"],
        "définis contractés": ["au", "du", "à la", "de la", "aux", "des"],
        "partitifs": ["du", "de l’", "de la", "des"],
    },
    "démonstratifs": ["ce", "cet", "cette", "ces"],
    "possessifs": ["mon", "ton", "son", "ma", "ta", "sa", "mes", "tes", "ses", "notre", "votre", "leur", "nos", "vos", "leurs"],
    "exclamatifs et interrogatifs": ["quel", "quelle", "quels", "quelles"],
    "numéraux": ["un", "deux", "trois", "quatre", "premier", "deuxième", "troisième", "quatrième"],
    "relatifs": ["lequel", "laquelle", "lesquels", "lesquelles", "duquel", "de laquelle", "desquels", "desquelles", "auquel", "à laquelle", "auxquels", "auxquelles"],
    "indéfinis": ["certain", "quelque", "aucun", "nul", "chaque", "différent", "plusieurs"],
})

""" https://www.scribbr.fr/elements-linguistiques/les-adjectifs/
Les adjectifs en français sont qualifiés de « qualificatifs », car ils permettent de donner des informations sur le nom auquel ils se rapportent.
Ils s’accordent en genre et en nombre avec le nom qu’ils qualifient.
"""