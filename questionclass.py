from typing import List, TypedDict, Callable, Tuple
import random
import re
import json

import chatapi

print("questionclass.py")


class Question:
    def __init__(self, question: str, explanation: str, weight=1.0, quiz_size: int = 10):
        self.question: str = question
        self.explanation: str = explanation
        self.weight: float = weight
        self.quiz_size: int = quiz_size

    def build_parts(self):
        pass

    def build_question(self) -> str:
        pass

    def rebuild_question(self) -> str:
        pass

    def grade_answer(self, answer: str) -> Tuple[float, str]:
        pass

    def increase_weight(self, quiz_size: int = 10):
        self.weight += quiz_size *  0.1
        self.weight = min(self.weight, quiz_size * 0.50)

    def reduce_weight(self):
        self.weight *= 2/5


class ShortAnswer(Question):
    # explanation should contain information relevant to the question/answer.
    #   This will be used to give the AI context and help educate the user
    # grading_instructions should give instructions on what is most important for an answer to contain
    #   Things like when a user should get a perfect grade, when they should get a low passing grade,
    #   and when they should fail
    def __init__(self, question: str, correct_answer: List[str], explanation: str, grading_instructions: str, weight=1.0):
        super().__init__(question, explanation, weight)
        self.correct_answer: List[str] = correct_answer
        self.grading_instructions: str = grading_instructions

        formatstr = "{ 'grade': 0.85, 'reason': 'The answer missed X, incorrectly stated Y, and failed to explain Z. It did mention A correctly, but lacked clarity in B.' }"
        self.graderprompt: str = f"""
            You're AI Grader. Your job is to critically assess a user’s answer based strictly on the fixed question, explanation, and sample answer provided. 
            Focus only on accuracy and completeness compared to the given standard.
            Use the embedded question, explanation, and correct sample answer to find all factual errors, missing points, or signs of misunderstanding in the user’s response.
            You should remove points for,
            Factual Inaccuracy: The answer contains incorrect information or statements that contradict the provided explanation or sample answer.
            Key Omissions: Essential points, components, steps, or details clearly present in the sample answer or required by the explanation are missing.
            Misunderstanding of Concepts: The answer demonstrates incorrect use of terminology, misapplication of principles, or a superficial understanding contrary to the provided explanation.
            Lack of Specificity/Vagueness: The answer is too general, ambiguous, or lacks the precision required by the question or demonstrated in the sample answer.
            Irrelevant Information: The answer includes details or statements that are off-topic or do not directly address the specific question asked.

            Return your evaluation as a single JSON object with two keys:

            * `grade`: a float between 0.0 and 1.0 based on how closely the user’s answer matches the meaning of the sample.
            * `reason`: a detailed explanation of what was wrong, missing, or unclear in the user’s answer. Be direct and specific. Focus on critical feedback that helps the user improve. Avoid encouragement or vague praise.

            Question: "{question}"

            Question Explanation: {explanation}

            Sample Answer(s): {', '.join(f'"{item}"' for item in correct_answer)}

            Grading Instructions: {grading_instructions}

            Do not be scared to fail the user.
            Users who show a lack of understanding should be given a low grade so they can learn from their mistakes.
            Grading Criteria:
            * Accuracy: Is the answer factually correct?
            * Completeness: Are all key points covered?
            * Understanding: Does it show a clear grasp of the concepts?
            * Clarity: Is it specific and unambiguous?

            Output Format:
            Only return a valid JSON object like this:
            {formatstr}
            """.strip()
        self.grader: chatapi.FlashChat = None

    def setup_grader(self):
        if self.grader is None:
            self.grader = chatapi.FlashChat(self.graderprompt, model="gemini-2.0-flash")

    def build_parts(self):
        return self.question

    def build_question(self) -> str:
        return f"(short answer)({self.weight}) {self.question}"

    def rebuild_question(self) -> str:
        return self.build_question()

    def grade_answer(self, answer: str) -> Tuple[float, str]:
        self.setup_grader()

        response = self.grader.prompt(answer)
        match = re.search(r'\{.*\}', response, re.DOTALL)
        data = json.loads(match.group(0)) if match else None

        if isinstance(data, dict):
            grade = data["grade"]
            super().reduce_weight() if grade > 0.8 else super().increase_weight()
            return data["grade"], data["reason"]

        print(f"ERROR grader response was not a valid json dict, '{response}'")

        return 0, ""


class MultipleChoice(Question):
    def __init__(self, question: str, correct_answers: List[str], wrong_answers: List[str], explanation: str, weight=1.0):
        super().__init__(question, explanation, weight)
        self.correct_answer = sorted(correct_answers)
        self.wrong_answers = sorted(wrong_answers)
        self.last_option_set: List[str] = []

    def build_parts(self, shuffle: bool = True, max_question_options=4):
        wrong_options_size = min(max_question_options-1, len(self.wrong_answers))
        options: List[str] = random.sample(self.wrong_answers, k=wrong_options_size)
        options.append(random.choice(self.correct_answer))
        options = (random.sample(options, k=len(options)) if shuffle else sorted(options, reverse=True))
        self.last_option_set = options

        return self.question, options

    def build_question(self, shuffle: bool = True, max_question_options=4) -> str:
        self.build_parts(shuffle, max_question_options)

        full_question = f"(MCQ)({self.weight}) {self.question}\n"
        letter = ord('A')
        for opt in self.last_option_set:
            full_question = f"{full_question}{chr(letter)}. {opt}\n"
            letter += 1
        return full_question

    def rebuild_question(self) -> str:
        if not self.last_option_set:
            self.build_parts()
        full_question = f"(MCQ)({self.weight}) {self.question}\n"
        letter = ord('A')
        for opt in self.last_option_set:
            full_question = f"{full_question}{chr(letter)}. {opt}\n"
            letter += 1
        return full_question

    def grade_answer(self, choice: str) -> Tuple[float, str]:
        if len(choice) != 1:
            print(f"invalid input to grade_answer '{choice}'")
            super().increase_weight()
            return 0.0, ""

        index = ord(choice.upper()) - ord('A')

        if index < 0 or index >= len(self.last_option_set):
            super().increase_weight()
            return 0.0, ""

        answer = self.last_option_set[index]
        is_correct = answer in self.correct_answer
        
        if is_correct:
            super().reduce_weight()
            return 1.0, ""
        else:
            super().increase_weight()
            return 0.0, ""


class TrueFalseQuestion(MultipleChoice):
    def __init__(self, question: str, correct_answers: List[str], wrong_answers: List[str], explanation: str, weight=1.0):
        super().__init__(question, correct_answers, wrong_answers, explanation, weight)

    def build_parts(self, shuffle: bool = False, max_question_options=2):
        return super().build_parts(shuffle=shuffle, max_question_options=max_question_options)

    def build_question(self) -> str:
        return super().build_question(shuffle=False)

    def rebuild_question(self) -> str:
        return super().rebuild_question()


# Use average category question weights to weight each category. AKA category's with
class QuestionBank:
    def __init__(self, questionlist: List[Question]):
        self.qbank: List[Question] = questionlist

    def grab_question(self) -> Question:
        picked = random.choices(self.qbank, weights=[q.weight for q in self.qbank], k=1)[0]
        return picked


if __name__ == '__main__':

    q_text = "What is the primary function of the mitochondria in a eukaryotic cell?"
    correct_ans_list = ["Cellular respiration", "ATP production", "Energy production"]
    expl_text = "Mitochondria are often called the 'powerhouses' of the cell as they generate most of the cell's supply of adenosine triphosphate (ATP), used as a source of chemical energy."

    # Creating an instance of the ShortAnswer class
    sample = ShortAnswer(
        question=q_text,
        correct_answer=correct_ans_list,
        explanation=expl_text,
        grading_instructions="do your best"
    )

    print(sample.build_question())
    user_input = input("answer: ")
    grade, reason = sample.grade_answer(user_input)
    print(f"{grade}, {reason}")

