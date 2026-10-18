import pandas as pd


class DataLoader:
    """Job: read the CSV files and give data to others."""

    def __init__(self, questions_file, roles_file):
        self.questions = pd.read_csv(questions_file)
        self.roles = pd.read_csv(roles_file)

    def get_role_names(self):
        return list(self.roles["role"].unique())

    def get_skills(self, role):
        rows = self.roles[self.roles["role"] == role]
        return list(rows["skill"])

    def get_required_levels(self, role):
        # Example result: {"SQL": 3, "Statistics": 2, "Pandas": 3}
        rows = self.roles[self.roles["role"] == role].reset_index(drop=True)
        required = {}
        for i in range(len(rows)):
            required[rows["skill"][i]] = int(rows["required_level"][i])
        return required
