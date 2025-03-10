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
from random import randint, sample
from yaml import load, SafeLoader

from config import QUESTION_COUNT, RANDOMIZE_CHOICES
from utils import VictoryException, GoodAnswerException, BadAnswerException, \
    FiftyException, PhoneException, PublicException


class Question:
    """
    Represents a single quiz question.
    """
    def __init__(self, data):
        """
        Initializes the Question object with the given data and index.
        """
        self.text = data["question"]
        self.answers = []
        self.display_answers = []
        self.correct_answer = 0
        self.fifty_fifty = set()
        self.phone = None
        self.public = None
        if RANDOMIZE_CHOICES:
            iterator = enumerate(sample(data["choices"], 4))
        else:
            iterator = enumerate(data["choices"])

        for i, choice in iterator:
            self.answers.append(choice["txt"])
            if choice.get("correct", False):
                self.correct_answer = i
                self.fifty_fifty.add(i)
        while len(self.fifty_fifty) != 2:
            self.fifty_fifty.add(randint(0, 100) % 4)
        self.display_answers = list(self.answers)

    def is_right_answer(self, answer):
        """
        Returns True if the given answer is correct, False otherwise.
        """
        return answer == self.correct_answer

    def __repr__(self):
        """
        Returns a string representation of the Question object.
        """
        result = f"Question: {self.text}\n"
        result += f"  - Answers: {self.answers}\n"
        result += f"  - Correct answer: {self.answers[self.correct_answer]}\n"
        result += f"  - Fifty fifty: {self.fifty_fifty}"
        return result

    def use_fifty(self):
        """
        Removes two incorrect answers from the list of answers.
        """
        for i in range(4):
            if i not in self.fifty_fifty:
                self.display_answers[i] = "---"

    def use_phone(self):
        """
        Simulates a phone call to a friend to get help with the answer.
        """
        while True:
            idx = randint(0, 3)
            if self.display_answers[idx] != "---":
                break
        if idx == self.correct_answer:
            v = randint(40, 100)
        else:
            v = randint(0, 70)
        # Unfortunately the phone emoji is not available in the font
        # "\u2706" was good but is unknown on target system
        self.display_answers[idx] += f" \u2706:{v}%"
        self.phone = idx, v

    def use_public(self):
        """
        Asks the audience for help with the answer.
        """
        if "---" in self.display_answers:
            self.public = [0, 0, 0, 0]
            self.public[self.correct_answer] = randint(40, 90)
            for i in range(4):
                if i == self.correct_answer or \
                        self.display_answers[i] == "---":
                    continue
                self.public[i] = 100 - self.public[self.correct_answer]
        else:
            self.public = [randint(0, 30) for _ in range(4)]
            self.public[self.correct_answer] += 100 - sum(self.public)

        for i in range(4):
            if self.display_answers[i] == "---":
                continue
            self.display_answers[i] += f" {self.public[i]}%"


class QuestionList:
    """
    Manages a list of quiz questions and provides lifelines.
    """
    def __init__(self):
        """
        Initializes the QuestionList object.
        """
        self.questions = []
        self.current_question = 0

        self.fifty_used = False
        self.phone_used = False
        self.public_used = False

        self.reset()

    def reset(self):
        """
        Resets the list of questions and lifelines.
        """
        self.questions = []
        self.current_question = 0
        self._read_yaml(Path("questions.yaml"))

        self.fifty_used = False
        self.phone_used = False
        self.public_used = False

    def _read_yaml(self, yaml_file: Path) -> None:
        """
        Reads the questions from the given YAML file.
        """
        # Read the YAML file
        with yaml_file.open("r") as f:
            data = load(f, Loader=SafeLoader)  # Load the YAML file
        # pick randomly some items
        data = sample(
            data,
            # Protect against too few items
            min(len(data), QUESTION_COUNT)
        )
        for item in data:
            self.questions.append(Question(item))
            # print(Question(item))

    def is_fifty_used(self) -> bool:
        """
        Returns True if the fifty-fifty lifeline has been used,
        False otherwise.
        """
        return self.fifty_used

    def use_fifty(self):
        """
        Uses the fifty-fifty lifeline to remove two incorrect answers.
        """
        if self.fifty_used:
            return
        self.fifty_used = True
        self.get_current_question().use_fifty()
        raise FiftyException(self.get_current_question(), None)

    def is_phone_used(self) -> bool:
        """
        Returns True if the phone a friend lifeline has been used,
        False otherwise.
        """
        return self.phone_used

    def use_phone(self):
        """
        Uses the phone a friend lifeline to get help with the answer.
        """
        if self.phone_used:
            return
        self.phone_used = True
        self.get_current_question().use_phone()
        raise PhoneException(self.get_current_question(), None)

    def is_public_used(self) -> bool:
        """
        Returns True if the ask the audience lifeline has been used,
        False otherwise.
        """
        return self.public_used

    def use_public(self):
        """
        Uses the ask the audience lifeline to get help with the answer.
        """
        if self.public_used:
            return
        self.public_used = True
        self.get_current_question().use_public()
        raise PublicException(self.get_current_question(), None)

    def current_question_idx(self) -> int:
        """
        Returns the index of the current question.
        """
        return self.current_question

    def get_current_question(self) -> Question:
        """
        Returns the current question.
        """
        if self.current_question >= len(self.questions):
            raise VictoryException()
        return self.questions[self.current_question]

    def validate_answer(self, answer) -> bool:
        """
        Validates the given answer and returns True if it is correct,
        False otherwise.
        """
        question = self.get_current_question()
        if question.answers[answer] == "---":
            return False
        if self.get_current_question().is_right_answer(answer):
            self.current_question += 1
            raise GoodAnswerException(question, answer)
        self.current_question = 0
        raise BadAnswerException(question, answer)
