import copy
from datetime import datetime
import json
import random
import re
import socket
from collections.abc import Iterable
from time import sleep
from typing import Callable, Optional, TypeVar, Sequence

from colorama import Back, Fore, Style, init
import pytest
import requests
from requests.exceptions import ChunkedEncodingError, SSLError
from requests_html import HTMLSession
from urllib3.exceptions import NewConnectionError, MaxRetryError
from Jsons import text_to_json

colors = ["RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN"]


class QuestionsAnswers:
    """ A class that able to train question and answer.
    The constructor takes a dict[str, Sequence[str]] as argument where keys represent questions, and the corresponding values represent their respective answers.
    Questions & Answers are colored to faster memoize them. Given a same questions_answers sample, they always have the same color. """

    def __init__(self, questions_answers: dict[str, Sequence[str]]):
        assert len(questions_answers) > 0, "questions_answers is empty"
        assert (isinstance(questions_answers, dict) and
                all(bool(isinstance(k, str) and isinstance(v, Sequence) and all(isinstance(item, str) for item in v))
                    for k, v in questions_answers.items())), "questions_answers doesn't match a type of dict[str, Sequence[str]]"
        self.questions_answers_origin: dict[str, Sequence[str]] = copy.deepcopy(questions_answers)
        self.questions_answers: dict[str, Sequence[str]] = questions_answers

    def filter(self, items_filter: Callable[[str, Sequence[str]], bool]):
        self.questions_answers = {k: v for (k, v) in self.questions_answers.items() if items_filter(k, v)}

    def _question(self) -> str:
        return random.choice(list(self.questions_answers.keys()))

    def _answer(self, question: str, response: str, contain_to_validate=False) -> bool:
        """ Pop the answer if the response is correct.
            Min 3 letters accepted when contain_to_validate is activated. """
        answers = self.questions_answers[question]
        try:
            if contain_to_validate:
                # StopIteration blocks
                if len(response) < 3:
                    index = next(index for (index, answer) in enumerate(answers) if response.lower() == answer.lower())
                else:
                    index = next(index for (index, answer) in enumerate(answers) if response.lower() in answer.lower())
            else:
                # ValueError
                index = list(map(lambda x: x.lower(), answers)).index(response.lower())
            self.questions_answers[question].pop(index)
            return True
        except (ValueError, StopIteration):
            return False

    def reverse_dict(self):
        reversed_dict = {}
        for key, values in self.questions_answers.items():
            for value in values:
                reversed_dict.setdefault(value, []).append(key)
        self.questions_answers = reversed_dict

    def training(self, just_one_to_validate: bool = False, keys_to_pickup: Optional[int] = None, contain_to_validate=False):
        """ Train for the Q/A
            Press "." to show all questions and answers
            Press "+" to swap Q/A to A/Q
            Press "q" to quit
        """
        if keys_to_pickup is not None:
            pickup_keys = random.sample(list(self.questions_answers_origin.keys()),
                                        min(len(self.questions_answers_origin), keys_to_pickup))
            self.questions_answers = {k: self.questions_answers_origin[k] for k in pickup_keys}
        # Questions are sorted to obtain the same color for a same given questions_answers dict
        sorted_questions = sorted(self.questions_answers)
        questions_answers_training = copy.deepcopy(self.questions_answers)
        while True:
            question = self._question()
            answer = self.questions_answers[question]
            answer_recovery = sorted(answer)
            answers_color = colors[sorted_questions.index(question) % len(colors)]
            response = ""
            printc("{} |{}|".format(question, len(answer)), color=answers_color)
            i = 0
            while i <= len(answer):
                response = input("\t")
                i += 1
                if response == ".":
                    for (q, answers) in sorted(questions_answers_training.items()):
                        print("{}\n\t{}".format(q.replace("\n", ""), "\n\t".join([a.replace("\n", "") for a in answers])))
                    i -= 1
                    continue
                elif response == "q":
                    self.questions_answers[question] = answer_recovery
                    print("End training")
                    return
                elif response == "+":
                    self.questions_answers = questions_answers_training
                    self.reverse_dict()
                    sorted_questions = sorted(self.questions_answers)
                    questions_answers_training = copy.deepcopy(self.questions_answers)
                    break
                    # return self.training(just_one_to_validate, keys_to_pickup, contain_to_validate)
                correct = self._answer(question, response, contain_to_validate)
                if correct:
                    print("\tok")
                    if just_one_to_validate:
                        [printc(a.replace("\n", ""), color=answers_color, end="   ") for a in sorted(answer_recovery)]
                        break
                else:
                    [printc(a.replace("\n", ""), color=answers_color, end="   ") for a in sorted(answer_recovery)]
                    print("\n")
                    break
            """ Recovery the question's answers after they have been pop. """
            if all(r != char for r in response for char in "q+."):
                self.questions_answers[question] = answer_recovery

    def exam(self, reset_if_wrong=False, just_one=False, contain_to_validate=False):
        """ Knowledge evaluation on the Q/A """
        out_of = len(self.questions_answers) if just_one else sum(map(len, self.questions_answers.values()))
        score = 0
        for _ in range(len(self.questions_answers)):
            question = self._question()
            answer = self.questions_answers[question]
            answer_recovery = sorted(answer)
            print(question)
            for _ in range(len(answer)):
                response = input("\t")
                correct = self._answer(question, response, contain_to_validate)
                if correct:
                    score += 1
                    print("{:>20}/{}".format(score, out_of))
                    if just_one:
                        break
                else:
                    [print(a, end="   ") for a in sorted(answer_recovery)]
                    if reset_if_wrong:
                        print("RESTART {}/{}\n".format(score, out_of))
                        self.questions_answers = copy.deepcopy(self.questions_answers_origin)
                        return self.exam(reset_if_wrong, just_one, contain_to_validate)
                    else:
                        break
            del self.questions_answers[question]
            print()
        print("SUCCESS {}/{}".format(score, out_of))
        self.questions_answers = copy.deepcopy(self.questions_answers_origin)


class TestQuestionsAnswers:
    def test_question_with_empty_dictionary(self):
        test_questions_answers = {}
        with pytest.raises(AssertionError):
            # questions_answers is empty
            QuestionsAnswers(test_questions_answers)

    def test_constructor_with_valid_input(self):
        test_questions_answers = {"Question 1": ["Answer 1"]}
        qa = QuestionsAnswers(test_questions_answers)
        assert qa.questions_answers == test_questions_answers
        assert qa.questions_answers_origin == {"Question 1": ["Answer 1"]}

    def test_constructor_with_invalid_input(self):
        test_questions_answers = {"Question 1": [1]}
        with pytest.raises(AssertionError):
            # questions_answers doesn't match a type of dict[str, Sequence[str]]
            QuestionsAnswers(test_questions_answers)

    def test_question_with_non_empty_dictionary(self, mocker):
        test_questions_answers = {"Question 1": ["Answer 1", "Answer 2"], "Question 2": ["Answer 3", "Answer 4"]}
        qa = QuestionsAnswers(test_questions_answers)
        mocker.patch('random.choice', return_value="Question 1")
        assert qa._question() == "Question 1"

    def test_answer_with_contain_to_validate_false_is_true(self):
        test_questions_answers = {"Question 1": ["Answer 1", "Answer 2"], "Question 2": ["Answer 3", "Answer 4"]}
        qa = QuestionsAnswers(test_questions_answers)
        assert qa._answer("Question 1", "Answer 1", contain_to_validate=False) is True
        assert qa.questions_answers == {'Question 1': ['Answer 2'], 'Question 2': ['Answer 3', 'Answer 4']}
        assert qa._answer("Question 1", "Answer 2", contain_to_validate=False) is True
        assert qa.questions_answers == {'Question 1': [], 'Question 2': ['Answer 3', 'Answer 4']}
        assert qa.questions_answers_origin == {"Question 1": ["Answer 1", "Answer 2"], "Question 2": ["Answer 3", "Answer 4"]}

    def test_answer_with_contain_to_validate_true_is_true(self):
        test_questions_answers = {"Question 1": ["Answer 1", "Answer 2"], "Question 2": ["Answer 3", "Answer 4"]}
        qa = QuestionsAnswers(test_questions_answers)
        assert qa._answer("Question 1", "Answer", contain_to_validate=True) is True
        assert qa.questions_answers == {"Question 1": ["Answer 2"], "Question 2": ["Answer 3", "Answer 4"]}
        assert qa.questions_answers_origin == {"Question 1": ["Answer 1", "Answer 2"], "Question 2": ["Answer 3", "Answer 4"]}

    def test_answer_with_contain_to_validate_false_is_false(self):
        test_questions_answers = {"Question 1": ["Answer 1", "Answer 2"], "Question 2": ["Answer 3", "Answer 4"]}
        qa = QuestionsAnswers(test_questions_answers)
        assert qa._answer("Question 1", "Wrong Answer") is False
        assert qa.questions_answers == qa.questions_answers_origin == {"Question 1": ["Answer 1", "Answer 2"],
                                                                       "Question 2": ["Answer 3", "Answer 4"]}

    def test_answer_with_contain_to_validate_true_is_false(self):
        test_questions_answers = {"Question 1": ["Answer 1", "Answer 2"], "Question 2": ["Answer 3", "Answer 4"]}
        qa = QuestionsAnswers(test_questions_answers)
        assert qa._answer("Question 1", "Anss", contain_to_validate=True) is False
        assert qa.questions_answers == qa.questions_answers_origin == {"Question 1": ["Answer 1", "Answer 2"],
                                                                       "Question 2": ["Answer 3", "Answer 4"]}

    def test_answer_with_contain_to_validate_true_with_empty_text(self):
        test_questions_answers = {"Question 1": ["Answer 1", "Answer 2"], "Question 2": ["Answer 3", "Answer 4"]}
        qa = QuestionsAnswers(test_questions_answers)
        assert qa._answer("Question 1", "", contain_to_validate=True) is False
        assert qa.questions_answers == qa.questions_answers_origin == {"Question 1": ["Answer 1", "Answer 2"],
                                                                       "Question 2": ["Answer 3", "Answer 4"]}

    def test_reverse_dict(self):
        test_questions_answers = {"Question 1": ["Answer 1", "Answer 2"], "Question 2": ["Answer 3", "Answer 4"]}
        qa = QuestionsAnswers(test_questions_answers)
        qa.reverse_dict()
        assert qa.questions_answers == {"Answer 1": ["Question 1"], "Answer 2": ["Question 1"],
                                        "Answer 3": ["Question 2"], "Answer 4": ["Question 2"]}
        assert qa.questions_answers_origin == {"Question 1": ["Answer 1", "Answer 2"], "Question 2": ["Answer 3", "Answer 4"]}

    def test_reverse_dict_on_training(self, mocker, capsys):
        test_questions_answers = {"Question 1": ["Answer 1", "Answer 2"]}
        qa = QuestionsAnswers(test_questions_answers)
        mocker.patch('random.choice', side_effect=["Question 1", "Answer 1", "Question 1"])
        mocker.patch('builtins.input', side_effect=[".", "+", ".", "+", ".", "q"])
        qa.training()
        assert qa.questions_answers == qa.questions_answers_origin == {"Question 1": ["Answer 1", "Answer 2"]}
        captured = capsys.readouterr()
        assert captured.out == """Question 1 |2|
Question 1
	Answer 1
	Answer 2
Answer 1 |1|
Answer 1
	Question 1
Answer 2
	Question 1
Question 1 |2|
Question 1
	Answer 1
	Answer 2
End training
"""

    def test_filter_with_filter_function_returning_true(self):
        test_questions_answers = {"Question 1": ["Answer 1", "Answer 2"], "Question 2": ["Answer 3", "Answer 4"]}
        qa = QuestionsAnswers(test_questions_answers)
        qa.filter(lambda question, answers: True)
        assert qa.questions_answers == qa.questions_answers_origin == {"Question 1": ["Answer 1", "Answer 2"],
                                                                       "Question 2": ["Answer 3", "Answer 4"]}

    def test_filter_with_filter_function_filtering_question(self):
        test_questions_answers = {"Question 1": ["Answer 1", "Answer 2"], "Question 2": ["Answer 3", "Answer 4"]}
        qa = QuestionsAnswers(test_questions_answers)
        qa.filter(lambda question, answers: "1" in question)
        assert qa.questions_answers == {"Question 1": ["Answer 1", "Answer 2"]}
        assert qa.questions_answers_origin == {"Question 1": ["Answer 1", "Answer 2"], "Question 2": ["Answer 3", "Answer 4"]}

    def test_filter_with_filter_function_filtering_answer(self):
        test_questions_answers = {"Question 1": ["Answer 1", "Answer 2"], "Question 2": ["Answer 3", "Answer 4"]}
        qa = QuestionsAnswers(test_questions_answers)
        qa.filter(lambda question, answers: any(["3" in a for a in answers]))
        assert qa.questions_answers == {"Question 2": ["Answer 3", "Answer 4"]}
        assert qa.questions_answers_origin == {"Question 1": ["Answer 1", "Answer 2"], "Question 2": ["Answer 3", "Answer 4"]}

    def test_training_with_correct_answers(self, mocker, capsys):
        test_questions_answers = {"Question 1": ["Answer 1", "Answer 2"], "Question 2": ["Answer 3", "Answer 4"]}
        qa = QuestionsAnswers(test_questions_answers)
        mocker.patch('random.choice', side_effect=["Question 1", "Question 2", "Question 1"])
        mocker.patch('builtins.input', side_effect=["Answer 1", "Answer 2", "Answer 3", "Answer 4", "q"])
        qa.training()
        assert qa.questions_answers == qa.questions_answers_origin == {"Question 1": ["Answer 1", "Answer 2"],
                                                                       "Question 2": ["Answer 3", "Answer 4"]}
        captured = capsys.readouterr()
        assert captured.out == """Question 1 |2|
	ok
	ok
Question 2 |2|
	ok
	ok
Question 1 |2|
End training
"""

    def test_training_with_uncorrect_answers(self, mocker, capsys):
        test_questions_answers = {"Question 1": ["Answer 1", "Answer 2"], "Question 2": ["Answer 3", "Answer 4"]}
        qa = QuestionsAnswers(test_questions_answers)
        mocker.patch('random.choice', side_effect=["Question 1", "Question 2", "Question 1"])
        mocker.patch('builtins.input', side_effect=["Answer 1", "Answer 3", "Answer 1", "q"])
        qa.training()
        assert qa.questions_answers == qa.questions_answers_origin == {"Question 1": ["Answer 1", "Answer 2"],
                                                                       "Question 2": ["Answer 3", "Answer 4"]}
        captured = capsys.readouterr()
        assert captured.out == """Question 1 |2|
	ok
Answer 1   Answer 2   

Question 2 |2|
Answer 3   Answer 4   

Question 1 |2|
End training
"""

    def test_questions_answers_after_answering_and_printing(self, mocker, capsys):
        test_questions_answers = {"Question 1": ["Answer 1", "Answer 2"]}
        qa = QuestionsAnswers(test_questions_answers)
        mocker.patch('random.choice', return_value="Question 1")
        mocker.patch('builtins.input', side_effect=["Answer 1", ".", "q"])
        qa.training()
        assert qa.questions_answers == {"Question 1": ["Answer 1", "Answer 2"]}
        captured = capsys.readouterr()
        assert captured.out == """Question 1 |2|
	ok
Question 1
	Answer 1
	Answer 2
End training
"""

    def test_questions_answers_after_answering_and_reversing(self, mocker, capsys):
        test_questions_answers = {"Question 1": ["Answer 1", "Answer 2"]}
        qa = QuestionsAnswers(test_questions_answers)
        mocker.patch('random.choice', side_effect=["Question 1", "Answer 1"])
        mocker.patch('builtins.input', side_effect=["Answer 1", "+", "q"])
        qa.training()
        assert qa.questions_answers == {"Answer 1": ["Question 1"], "Answer 2": ["Question 1"]}
        captured = capsys.readouterr()
        assert captured.out == """Question 1 |2|
	ok
Answer 1 |1|
End training
"""


def is_correct_lines(lines: list[str], debug=True) -> bool:
    questions_answers_pattern = r"[^\t\n\r]+\t[^\t\n\r]+[\n\r]"
    incorrect_lines = [(i + 1, lines[i]) for i in range(len(lines)) if re.fullmatch(questions_answers_pattern, lines[i]) is None]
    if debug and len(incorrect_lines) > 0:
        printc(str(incorrect_lines), color="red")
    return len(incorrect_lines) == 0


def file_to_questions_answers(file_name: str) -> QuestionsAnswers:
    lines = get_lines(file_name)
    assert (is_correct_lines(lines))
    q_n_a = {question: answers.split("/") for (question, answers) in
             [(line.split("\t")[0], line.split("\t")[1]) for line in lines]}
    return QuestionsAnswers(q_n_a)


# LIB #


import json as json_api

T = TypeVar("T")
E = TypeVar("E")
json_base = list[dict[T, E]]
json_T = dict[T, E]


def get_lines(file_name: str, encoding="utf-8") -> Optional[list[str]]:
    try:
        with open(file_name, 'r', encoding=encoding) as file:
            return file.readlines()
    except FileNotFoundError:
        return None


def printc(text: str, color="green", background_color=None, attributes: Iterable[str] = ("NORMAL",), end="\n") -> None:
    init()
    style = getattr(Fore, color.upper()) if color != "" else ""
    if background_color:
        style += getattr(Back, background_color.upper())
    if attributes:
        " ".join([getattr(Style, attribute.upper()) for attribute in attributes])
    print("{}{}{}".format(style, text, Style.RESET_ALL), end=end)


def is_iter_but_not_str(element):
    """ If iterable object and not str"""
    if isinstance(element, Iterable) and not isinstance(element, str):
        return True
    return False


def to_correct_json(string) -> str:
    # json_string = str(string).replace("True", "\"True\"").replace("False", "\"False\"").replace("\n", "").replace("\\", "")
    json_string = re.sub(r"(?<=[{,])(.*?):('?)(.*?)('?)(((?<='),)|},{|})", r""""\1":"\3"\5""", string)
    return json_string
    # return str(string).replace("True", "\"True\"").replace("False", "\"False\"").replace("'", "\"").replace("\\", "\\\\")


def text_to_json(json_text: str) -> json_base:
    correct_json = to_correct_json(json_text)
    return json_api.loads(correct_json)


def url_to_json(url: str, timelimit=1) -> Optional[json_base]:
    html_session = HTMLSession()
    try:
        start = datetime.now()
        json_value = None
        while True:
            try:
                if (datetime.now() - start).total_seconds() / 60 >= timelimit:
                    return None
                html_result_text = html_session.get(url)
                html_result_text = html_result_text.text
                if "503 Service Unavailable" in html_result_text or "<Response [403]>" in html_result_text:
                    print("url_to_json error: err Response in html_result_text")
                    sleep(5)
                    continue
                json_value = text_to_json(html_result_text)
                break
            except ChunkedEncodingError or ConnectionError or NewConnectionError or socket.gaierror or json.decoder.JSONDecodeError or requests.exceptions.ConnectTimeout:
                printc("url_to_json ChunkedEncodingError", background_color="red")
                sleep(2)
                return url_to_json(url)
        return json_value
    except MaxRetryError or SSLError:
        return None


def json_base_to_json_ok(dictionaries: json_base | dict,
                         keys_aim: list[T],
                         keys_path_to_start: list[T] = None,
                         condition: Callable[[json_T], bool] = None,
                         doublons=True) -> json_T:
    """
    On remplace les indices de la liste de base en la transformant en un dictionnaire où
    les clefs seront les valeurs associées à la clef donnée en paramètre des dictionnaires de la liste.
    S'il y a plusieurs keys, tous les champs doivent avoir le même pattern
    """
    result = {}
    if keys_path_to_start is not None:
        for key in keys_path_to_start:
            dictionaries = dictionaries[key]
    if type(dictionaries) is dict:
        dictionaries = [dictionaries]
    for dictionary in dictionaries:
        key_cursor = dictionary
        for k in keys_aim[:-1]:
            key_cursor = key_cursor[k]
        key = key_cursor[keys_aim[-1]]
        if condition is not None and not condition(dictionary):
            continue
        if doublons and key in result:
            if type(result[key]) is not list:
                result[key] = [result[key]]
            result[key].append(dictionary)
        else:
            result[key] = dictionary
    return result


if __name__ == '__main__':
    # # tft_db = url_to_json("https://raw.communitydragon.org/latest/cdragon/tft/fr_fr.json")
    # tft_db = url_to_json("https://raw.communitydragon.org/latest/cdragon/tft/en_us.json")
    # champions = json_base_to_json_ok(tft_db, ["name"], ["sets", "9", "champions"])
    # tft_champions = defaultdict(list)
    # for champion, values in champions.items():
    #     if "traits" in values:
    #         for trait in values["traits"]:
    #             tft_champions[champion].append(trait)

    tft_champions = {
        'Piltover': ['Ekko', 'Heimerdinger', 'Jayce', 'Orianna', 'Vi'],
        'Rogue': ['Ekko', 'Katarina', 'Zed', 'Viego'],
        'Demacia': ['Garen', 'Jarvan IV', 'Lux', 'Poppy', 'Sona', 'Kayle', 'Galio'],
        'Shadow Isles': ['Gwen', 'Senna', 'Maokai', 'Kalista', 'Viego'],
        'Technogenius': ['Heimerdinger'],
        'Invoker': ['Karma', 'Lissandra', 'Shen', 'Soraka', 'Cassiopeia', 'Galio'],
        'Bastion': ["K'Sante", 'Poppy', 'Shen', 'Taric', 'Maokai', 'Kassadin'],
        'Redeemer': ['Senna'],
        'Multicaster': ['Sona', 'Teemo', "Vel'Koz", 'Taliyah'],
        'Targon': ['Soraka', 'Taric', 'Aphelios']
    }
    qa_tft = QuestionsAnswers(tft_champions)
    # qa_tft.reverse_dict()
    # # qa_tft.filter(items_filter=lambda keys, values: "R" in keys)
    # qa_tft.training(just_one_to_validate=False, contain_to_validate=False)
    # qa_tft.exam(reset_if_wrong=True)

    # qa_english = file_to_questions_answers("anglais.txt")
    while True:
        qa_english = file_to_questions_answers("anglais.txt")
        # qa_tft.training(keys_to_pickup=3)
