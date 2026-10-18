import json
import os


class Storage:
    """Base class: every storage must have a save() method."""

    def save(self, record):
        pass


class JsonStorage(Storage):
    """Saves the full result in a JSON file."""

    def __init__(self, filename):
        self.filename = filename

    def save(self, record):
        data = []
        if os.path.exists(self.filename):          # old results exist?
            with open(self.filename) as f:
                data = json.load(f)
        data.append(record)                        # add the new result
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=4)


class CsvStorage(Storage):
    """Saves a one-line summary in a CSV file."""

    def __init__(self, filename):
        self.filename = filename

    def save(self, record):
        is_new_file = not os.path.exists(self.filename)
        with open(self.filename, "a") as f:
            if is_new_file:
                f.write("date,name,role,readiness_percent\n")
            f.write(f'{record["date"]},{record["name"]},{record["role"]},{record["overall_percent"]}\n')


class MySqlStorage(Storage):
    """Saves the result in the MySQL database (visible in phpMyAdmin).
    It is another Storage, so app.py can use it like the others."""

    def __init__(self, database):
        self.database = database

    def save(self, record):
        # 1. one row in the results table
        result_id = self.database.run(
            "INSERT INTO results (user_id, role, overall_percent, taken_on) "
            "VALUES (%s, %s, %s, NOW())",
            (record["user_id"], record["role"], record["overall_percent"]))

        # 2. one row for each skill in the skill_results table
        for r in record["results"]:
            self.database.run(
                "INSERT INTO skill_results (result_id, skill, score, total, level_name, "
                "required_name, gap, priority) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (result_id, r["skill"], r["score"], r["total"], r["level_name"],
                 r["required_name"], r["gap"], r["priority"]))
