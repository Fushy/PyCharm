import random

# QCM = {Question1: [(choix1, reponse1), ..., (choixN, reponseN)],
# ..., QuestionN: [(choix1, reponse1), ..., (choixN, reponseN)]}

qcm = {
    "Le passage à l'échelle horizontal (horizontal scaling ou scaling out) correspond à augmenter le nombre de "
    "machines d'un cluster": [
        ("Vrai", True), ("Faux", False)
    ],
    "Une approche classique IaaS n'utilise pas de serveur de virtualisation": [
        ("Vrai", False), ("Faux", True)
    ],
    "Dans un contexte de cloud computing, le concept de multinenancy est lié à la notion de partitionnement virtuel "
    "des données": [
        ("Vrai", False), ("Faux", True)
    ],
    "Pour faire passer un cluster de machines à l'échelle, il est possible d'adopter un passage vertical et un "
    "passage horizontal (respectivement scaling up et scaling out)": [
        ("Vrai", True), ("Faux", False)
    ],
    "Dans une approche PaaS, le fournisseur du service de cloud gère le système d'exploitation (OS) pour "
    "l'utilisateur": [
        ("Vrai", True), ("Faux", False)
    ],
    "L'opération de shuffle du framework MapReduce est totalement transparente pour le programmeur": [
        ("Vrai", False), ("Faux", True)
    ],
    "Le composant HDFS du projet Apache Hadoop est un système de gestion de base de données du type NoSQL": [
        ("Vrai", True), ("Faux", True)
    ],
    "L'opération collect du framework Spark est lazy": [
        ("Vrai", False), ("Faux", True)
    ],
    "Les actions en Spark sont des opérations lazy": [
        ("Vrai", False), ("Faux", True)
    ],
    "Le framework MepReduce gère les aspects suivants": [
        ("gestion des pannes des machines du cluster", True),
        ("le partitionnement des données fournies en entrée", True),
        ("l'indexation des données", False),
        ("la planification de l'exécution des programmes sur les machines du cluster", False),
        ("la communication inter-machine au sein du cluster", False)
    ],
    "Quelles sont les solutions suivantes qui facilitent la rédaction de jobs MapReduce (Google ou Hadoop)": [
        ("Pig Latin", True),
        ("SPOF", False),
        ("RDF", False),
        ("Sawzall", True),
        ("Cypher", False)
    ],
    "Le système de fichier distribué GFS du framework MapReduce de Google": [
        ("est adapté à la gestion de fichiers (< à quelques Mo)", False),
        ("suit une architecture Peer to Peer", False),
        ("est adapté à gérer de gros fichier (> des centaines de Mo)", True),
        ("gère l'indexation", False)
    ],
    "L'opération count en Spark est": [
        ("Lazy", False),
        ("une action", True),
        ("une transformation", False),
        ("valide qu'avec l'API Dataframe", False)
    ],
    "Avec l'API Dataset, on peut questionner les données": [
        ("avec le DSL de Spark", True),
        ("en RDF", False),
        ("avec SQL", True),
        ("en programmation fonctionnelle", True)
    ],
    "Le composant GraphX de Spark adopte le modèle de données": [
        ("property graph", True),
        ("document", True),
        ("BSP", True),
        ("RDF", False)
    ]
}

for question in qcm.items():
    if len(question[1]) > 2:
        random.shuffle(question[1])

note = 0
noteMax = len(qcm)
while len(qcm) > 0:
    item = list(qcm.items())[random.randint(0, len(qcm) - 1)]
    cle = item[0]
    valeur = item[1]
    string = [str(i) + " " + str(valeur[i][0]) for i in range(len(valeur))]
    reponse = input(item[0] + "\n" + str(string) + "\n")
    if reponse == "":
        for val in valeur:
            if not val[1]:
                print("Bon")
                note += 1 / len(valeur)
            else:
                print("Faux")
        print(valeur)
        qcm.pop(cle)
        continue

    for i in range(len(valeur)):
        if len(valeur) > 2:
            if valeur[i][1] and str(i) in reponse:
                print("Bon")
                note += 1 / len(valeur)
            elif not valeur[i][1] and str(i) not in reponse:
                print("Bon")
                note += 1 / len(valeur)
            else:
                print("Faux")
        else:
            if valeur[i][1]:
                if str(i) in reponse:
                    print("Bon")
                    note += 1
                else:
                    print("Faux")
    if len(valeur) > 2:
        print(valeur)
    qcm.pop(cle)
    print(note)
    print()
input((str(note) + "/" + str(noteMax)))
