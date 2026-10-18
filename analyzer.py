class LevelClassifier:
    """Job: change a percentage into a level (1 = Basic, 2 = Intermediate, 3 = Advanced)."""

    names = {1: "Basic", 2: "Intermediate", 3: "Advanced"}

    def classify(self, percent):
        if percent >= 80:
            return 3
        elif percent >= 40:
            return 2
        else:
            return 1


class StrictClassifier(LevelClassifier):
    """Example of Open/Closed: a new rule is a NEW class.
    To use it, write SkillAnalyzer(StrictClassifier(), ...) in app.py. Nothing else changes."""

    def classify(self, percent):
        if percent >= 90:
            return 3
        elif percent >= 60:
            return 2
        else:
            return 1


class GapAnalyzer:
    """Job: decide the learning priority from the gap."""

    def priority(self, gap):
        if gap >= 2:
            return "High"
        elif gap == 1:
            return "Medium"
        else:
            return "No gap"


class SkillAnalyzer:
    """Job: check the answers and prepare the result.
    The classifier and gap analyzer are given from outside (Dependency Inversion)."""

    def __init__(self, classifier, gap_analyzer):
        self.classifier = classifier
        self.gap_analyzer = gap_analyzer

    def analyze(self, quiz, answers, required):
        results = []
        for skill in required:
            # count correct answers of this skill
            score = 0
            total = 0
            for i in range(len(quiz)):
                if quiz[i]["skill"] == skill:
                    total = total + 1
                    if answers[i] == quiz[i]["correct"]:
                        score = score + 1

            percent = round(score * 100 / total)
            level = self.classifier.classify(percent)
            gap = required[skill] - level
            if gap < 0:
                gap = 0

            results.append({"skill": skill,
                            "score": score,
                            "total": total,
                            "percent": percent,
                            "level": level,
                            "level_name": self.classifier.names[level],
                            "required": required[skill],
                            "required_name": self.classifier.names[required[skill]],
                            "gap": gap,
                            "priority": self.gap_analyzer.priority(gap)})
        return results

    def overall_percent(self, results):
        score = 0
        total = 0
        for r in results:
            score = score + r["score"]
            total = total + r["total"]
        return round(score * 100 / total)

    def verdict(self, percent):
        if percent >= 80:
            return "Job Ready 🚀"
        elif percent >= 50:
            return "Almost There 👍"
        else:
            return "Needs Training 📚"
