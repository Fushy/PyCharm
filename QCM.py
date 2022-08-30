import copy
import random
import re
from typing import Callable, Optional

from Colors import printc
from Files import get_lines
from Util import str_to_hashdigits


class QuestionsAnswers:

    def __init__(self, questions_answers: dict[str, list[str]]):
        self.questions_answers = questions_answers
        self.questions_answers_active = copy.deepcopy(self.questions_answers)
        self.hashcode: Optional[int] = None
        self.__hash__()

    def __hash__(self) -> int:
        if self.hashcode is None:
            self.hashcode = str_to_hashdigits(str(hash(QuestionsAnswers) * id(QuestionsAnswers)))
        return self.hashcode

    def filter(self,
               key_filter: Callable[[str, list[str]], bool] = None,
               value_filter: Callable[[str, list[str]], bool] = None):
        if key_filter is None and value_filter is None:
            self.questions_answers_active = self.questions_answers
        elif key_filter is not None and value_filter is not None:
            self.questions_answers_active = {k: v for (k, v) in self.questions_answers.items()
                                             if key_filter(k, v) and value_filter(k, v)}
        elif key_filter is not None:
            self.questions_answers_active = {k: v for (k, v) in self.questions_answers.items() if key_filter(k, v)}
        elif value_filter is not None:
            self.questions_answers_active = {k: v for (k, v) in self.questions_answers.items() if value_filter(k, v)}

    def question(self) -> str:
        return random.choice(list(self.questions_answers_active))

    def answer(self, question: str, response: str) -> bool:
        # Can be simpler by using shuffle on the dict
        answers = self.questions_answers_active[question]
        try:
            index = list(map(lambda x: x.casefold(), answers)).index(response.casefold())
            self.questions_answers_active[question].pop(index)
            return True
        except ValueError:
            return False

    def reverse_dict(self):
        hashtext = str(self.hashcode)
        self.questions_answers = {
            hashtext.join(v) if type(v) is list else v: [k] if type(v) is list else k.split(hashtext)
            for (k, v) in self.questions_answers.items()}
        self.questions_answers_active = {
            hashtext.join(v) if type(v) is list else v: [k] if type(v) is list else k.split(hashtext)
            for (k, v) in self.questions_answers_active.items()}

    def training(self, just_one: bool = False):
        while True:
            question = self.question()
            answer = self.questions_answers_active[question]
            answer_recovery = sorted(answer)
            print(question.replace(str(self.hashcode), "\t"))
            for _ in range(len(answer)):
                response = input("\t")
                correct = self.answer(question, response)
                if correct:
                    print("\tok")
                    if just_one:
                        break
                else:
                    print("\t" + "\t".join(answer_recovery))
                    break
            self.questions_answers_active[question] = answer_recovery

    def exam(self, reset_if_wrong=False, just_one=False):
        out_of = (len(self.questions_answers_active.keys()) if just_one else
                  sum(map(len, self.questions_answers_active.values())))
        score = 0
        for _ in range(len(self.questions_answers_active)):
            question = self.question()
            answer = self.questions_answers_active[question]
            answer_recovery = sorted(answer)
            print(question.replace(str(self.hashcode), "\t"))
            for _ in range(len(answer)):
                response = input("\t")
                correct = self.answer(question, response)
                if correct:
                    score += 1
                    print("\tok\t{}/{}".format(score, out_of))
                    if just_one:
                        break
                else:
                    print("\t" + "\t".join(answer_recovery))
                    if reset_if_wrong:
                        print("RESTART {}/{}\n".format(score, out_of))
                        self.questions_answers_active = copy.deepcopy(self.questions_answers)
                        return self.exam(reset_if_wrong, just_one)
                    else:
                        break
            del self.questions_answers_active[question]
            print()
        self.questions_answers_active = copy.deepcopy(self.questions_answers)
        print("SUCCESS {}/{}".format(score, out_of))


def is_correct_lines(lines: list[str], debug=True) -> bool:
    empty_line = r"\s+"
    questions_answers_pattern = r"[^\t\n\r]+\t[^\t]+"
    incorrect_lines = [(i + 1, lines[i]) for i in range(len(lines)) if
                       re.fullmatch(empty_line, lines[i]) is None and re.fullmatch(questions_answers_pattern,
                                                                                   lines[i]) is None]
    if debug and len(incorrect_lines) > 0:
        printc(str(incorrect_lines), color="red")
    # correct_lines = [re.fullmatch(questions_answers_pattern, line) for line in lines if
    #                  re.fullmatch(empty_line, line) is None]
    # return all(correct_lines)
    return len(incorrect_lines) == 0


def file_to_questions_answers(file_name: str) -> QuestionsAnswers:
    lines = get_lines(file_name)
    assert (is_correct_lines(lines))
    q = {question: answers.split("/") for (question, answers) in
         [(line.split("\t")[0], line.split("\t")[1]) for line in lines]}
    return QuestionsAnswers(q)


if __name__ == '__main__':
    Mondstadt = {
        "Brightcrown Mountains": ["Brightcrown Canyon", "Stormterror's Lair"],
        "Galesong Hill": ["Cape Oath", "Dadaupa Gorge", "Falcon Coast", "Musk Reef", "Windrise"],
        "Starfell Valley": ["Cider Lake", "Mondstadt", "Starfell Lake", "Starsnatch Cliff",
                            "Stormbearer Mountains", "Stormbearer Point", "Thousand Winds Temple", "Whispering Woods"],
        "Windwail Highland": ["Dawn Winery", "Springvale", "Wolvendom"],
        "Dragonspine": ["Entombed City - Ancient Palace", "Entombed City - Outskirts", "Skyfrost Nail",
                        "Snow-Covered Path", "Starglow Cavern", "Wyrmrest Valley"],
    }
    # q = QuestionsAnswers(Mondstadt)
    # q.reverse_dict()
    # q.training()
    # q.exam(reset_if_wrong=True)
    q = file_to_questions_answers("anglais.txt")
    q.training()

# old
# QCM = {Question1: [(choix1, reponse1), ..., (choixN, reponseN)],
# ..., QuestionN: [(choix1, reponse1), ..., (choixN, reponseN)]}

# qcm = {
#     "Le passage à l'échelle horizontal (horizontal scaling ou scaling out) correspond à augmenter le nombre de "
#     "machines d'un cluster": [
#         ("Vrai", True), ("Faux", False)
#     ],
#     "Une approche classique IaaS n'utilise pas de serveur de virtualisation": [
#         ("Vrai", False), ("Faux", True)
#     ],
#     "Dans un contexte de cloud computing, le concept de multinenancy est lié à la notion de partitionnement virtuel "
#     "des données": [
#         ("Vrai", False), ("Faux", True)
#     ],
#     "Pour faire passer un cluster de machines à l'échelle, il est possible d'adopter un passage vertical et un "
#     "passage horizontal (respectivement scaling up et scaling out)": [
#         ("Vrai", True), ("Faux", False)
#     ],
#     "Dans une approche PaaS, le fournisseur du service de cloud gère le système d'exploitation (OS) pour "
#     "l'utilisateur": [
#         ("Vrai", True), ("Faux", False)
#     ],
#     "L'opération de shuffle du framework MapReduce est totalement transparente pour le programmeur": [
#         ("Vrai", False), ("Faux", True)
#     ],
#     "Le composant HDFS du projet Apache Hadoop est un système de gestion de base de données du type NoSQL": [
#         ("Vrai", True), ("Faux", True)
#     ],
#     "L'opération collect du framework Spark est lazy": [
#         ("Vrai", False), ("Faux", True)
#     ],
#     "Les actions en Spark sont des opérations lazy": [
#         ("Vrai", False), ("Faux", True)
#     ],
#     "Le framework MepReduce gère les aspects suivants": [
#         ("gestion des pannes des machines du cluster", True),
#         ("le partitionnement des données fournies en entrée", True),
#         ("l'indexation des données", False),
#         ("la planification de l'exécution des programmes sur les machines du cluster", False),
#         ("la communication inter-machine au sein du cluster", False)
#     ],
#     "Quelles sont les solutions suivantes qui facilitent la rédaction de jobs MapReduce (Google ou Hadoop)": [
#         ("Pig Latin", True),
#         ("SPOF", False),
#         ("RDF", False),
#         ("Sawzall", True),
#         ("Cypher", False)
#     ],
#     "Le système de fichier distribué GFS du framework MapReduce de Google": [
#         ("est adapté à la gestion de fichiers (< à quelques Mo)", False),
#         ("suit une architecture Peer to Peer", False),
#         ("est adapté à gérer de gros fichier (> des centaines de Mo)", True),
#         ("gère l'indexation", False)
#     ],
#     "L'opération count en Spark est": [
#         ("Lazy", False),
#         ("une action", True),
#         ("une transformation", False),
#         ("valide qu'avec l'API Dataframe", False)
#     ],
#     "Avec l'API Dataset, on peut questionner les données": [
#         ("avec le DSL de Spark", True),
#         ("en RDF", False),
#         ("avec SQL", True),
#         ("en programmation fonctionnelle", True)
#     ],
#     "Le composant GraphX de Spark adopte le modèle de données": [
#         ("property graph", True),
#         ("document", True),
#         ("BSP", True),
#         ("RDF", False)
#     ]
# }
#
# for question in qcm.items():
#     if len(question[1]) > 2:
#         random.shuffle(question[1])
#
# note = 0
# noteMax = len(qcm)
# while len(qcm) > 0:
#     item = list(qcm.items())[random.randint(0, len(qcm) - 1)]
#     cle = item[0]
#     valeur = item[1]
#     string = [str(i) + " " + str(valeur[i][0]) for i in range(len(valeur))]
#     reponse = input(item[0] + "\n" + str(string) + "\n")
#     if reponse == "":
#         for val in valeur:
#             if not val[1]:
#                 print("Bon")
#                 note += 1 / len(valeur)
#             else:
#                 print("Faux")
#         print(valeur)
#         qcm.pop(cle)
#         continue
#
#     for i in range(len(valeur)):
#         if len(valeur) > 2:
#             if valeur[i][1] and str(i) in reponse:
#                 print("Bon")
#                 note += 1 / len(valeur)
#             elif not valeur[i][1] and str(i) not in reponse:
#                 print("Bon")
#                 note += 1 / len(valeur)
#             else:
#                 print("Faux")
#         else:
#             if valeur[i][1]:
#                 if str(i) in reponse:
#                     print("Bon")
#                     note += 1
#                 else:
#                     print("Faux")
#     if len(valeur) > 2:
#         print(valeur)
#     qcm.pop(cle)
#     print(note)
#     print()
# input((str(note) + "/" + str(noteMax)))
