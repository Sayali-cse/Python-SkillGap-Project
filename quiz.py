import random


class QuizGenerator:
    """Job: make a random quiz, so every student gets different questions."""

    def __init__(self, questions, roles, per_skill=3):
        self.questions = questions
        self.roles = roles
        self.per_skill = per_skill          # questions picked for each skill

    def create_quiz(self, role):
        quiz = []
        skills = self.roles[self.roles["role"] == role]["skill"]

        for skill in skills:
            # all questions of this role and skill
            bank = self.questions[(self.questions["role"] == role) &
                                  (self.questions["skill"] == skill)]
            picked = bank.sample(n=self.per_skill).reset_index(drop=True)   # random pick

            for i in range(len(picked)):
                options = [picked["option_a"][i], picked["option_b"][i],
                           picked["option_c"][i], picked["option_d"][i]]
                correct = picked["option_" + picked["answer"][i].lower()][i]
                random.shuffle(options)         # mix the order of options

                quiz.append({"skill": skill,
                             "question": picked["question"][i],
                             "options": options,
                             "correct": correct})
        return quiz
