class HistoryReader:
    """Job: read the old results of a user from the database."""

    def __init__(self, database):
        self.database = database

    def get_history(self, user_id):
        return self.database.fetch(
            "SELECT role, overall_percent, taken_on FROM results "
            "WHERE user_id = %s ORDER BY id DESC", (user_id,))
