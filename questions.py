#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
questions.py

This module contains classes to handle quiz questions and their
associated functionalities.
It includes the Question class to represent individual questions and
the QuestionList class to manage a list of questions and provide lifelines
such as fifty-fifty, phone a friend, and ask the audience.

Classes:
    Question: Represents a single quiz question.
    QuestionList: Manages a list of quiz questions and provides lifelines.

Exceptions:
    VictoryException: Raised when all questions are answered correctly.
    GoodAnswerException: Raised when a correct answer is given.
    BadAnswerException: Raised when an incorrect answer is given.
    FiftyException: Raised when the fifty-fifty lifeline is used.
    PhoneException: Raised when the phone a friend lifeline is used.
    PublicException: Raised when the ask the audience lifeline is used.
"""


from pathlib import Path
from random import randint
from utils import VictoryException, GoodAnswerException, BadAnswerException, \
    FiftyException, PhoneException, PublicException
from yaml import load, SafeLoader


class Question:
    def __init__(self, data, idx):
        self.text = data["question"]
        self.idx = idx
        self.answers = list()
        self.correct_answer = 0
        self.fifty_fifty = set()
        self.phone = None
        self.public = None
        for i, choice in enumerate(data["choices"]):
            self.answers.append(choice["txt"])
            if choice.get("correct", False):
                self.correct_answer = i
                self.fifty_fifty.add(i)
        while len(self.fifty_fifty) != 2:
            self.fifty_fifty.add(randint(0, 100) % 4)

    def is_right_answer(self, answer):
        return answer == self.correct_answer

    def __repr__(self):
        result = f"Question: {self.text}\n"
        result += f"  - Answers: {self.answers}\n"
        result += f"  - Correct answer: {self.answers[self.correct_answer]}\n"
        result += f"  - Fifty fifty: {self.fifty_fifty}"
        return result

    def use_fifty(self):
        for i in range(4):
            if i not in self.fifty_fifty:
                self.answers[i] = "---"

    def use_phone(self):
        while True:
            idx = randint(0, 3)
            if self.answers[idx] != "---":
                break
        if idx == self.correct_answer:
            v = randint(40, 100)
        else:
            v = randint(0, 70)
        self.answers[idx] += f" \u2706:{v}%"
        self.phone = idx, v

    def use_public(self):
        if "---" in self.answers:
            self.public = [0, 0, 0, 0]
            self.public[self.correct_answer] = randint(40, 90)
            for i in range(4):
                if self.answers[i] == "---" or i == self.correct_answer:
                    continue
                self.public[i] = 100 - self.public[self.correct_answer]
        else:
            self.public = [randint(0, 30) for _ in range(4)]
            self.public[self.correct_answer] += 100 - sum(self.public)

        for i in range(4):
            if self.answers[i] == "---":
                continue
            self.answers[i] += f" {self.public[i]}%"


class QuestionList:
    def __init__(self):
        self.reset()

    def reset(self):
        self.questions = list()
        self.current_question = 0
        self._read_yaml(Path("questions.yaml"))

        self.fifty_used = False
        self.phone_used = False
        self.public_used = False

    def _read_yaml(self, yaml_file: Path) -> None:
        # Read the YAML file
        with yaml_file.open("r") as f:
            data = load(f, Loader=SafeLoader)  # Load the YAML file
        for i, item in enumerate(data):
            self.questions.append(Question(item, i))
            # print(Question(item))

    def is_fifty_used(self) -> bool:
        return self.fifty_used

    def use_fifty(self):
        if self.fifty_used:
            return
        self.fifty_used = True
        self.get_current_question().use_fifty()
        raise FiftyException(self.get_current_question(), None)

    def is_phone_used(self) -> bool:
        return self.phone_used

    def use_phone(self):
        if self.phone_used:
            return
        self.phone_used = True
        self.get_current_question().use_phone()
        raise PhoneException(self.get_current_question(), None)

    def is_public_used(self) -> bool:
        return self.public_used

    def use_public(self):
        if self.public_used:
            return
        self.public_used = True
        self.get_current_question().use_public()
        raise PublicException(self.get_current_question(), None)

    def current_question_idx(self) -> int:
        return self.current_question

    def get_current_question(self) -> Question:
        if self.current_question >= len(self.questions):
            raise VictoryException()
        return self.questions[self.current_question]

    def validate_answer(self, answer) -> bool:
        question = self.get_current_question()
        if question.answers[answer] == "---":
            return False
        if self.get_current_question().is_right_answer(answer):
            self.current_question += 1
            raise GoodAnswerException(question, answer)
        self.current_question = 0
        raise BadAnswerException(question, answer)
