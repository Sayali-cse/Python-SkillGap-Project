import hashlib


class AuthService:
    """Job: register new users and check the login."""

    def __init__(self, database):
        self.database = database

    def hash_password(self, password):
        # We never save the real password. We save a scrambled (hashed) copy.
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, name, email, password):
        """Returns (True or False, message)."""
        if name == "" or email == "" or password == "":
            return False, "Please fill all the fields."
        if "@" not in email or "." not in email:
            return False, "Please enter a valid email."
        if len(password) < 6:
            return False, "Password must have at least 6 characters."

        old = self.database.fetch("SELECT id FROM users WHERE email = %s", (email,))
        if len(old) > 0:
            return False, "This email is already registered."

        self.database.run("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                          (name, email, self.hash_password(password)))
        return True, "Account created! Now login."

    def login(self, email, password):
        """Returns the user (id, name, email) or None if the login is wrong."""
        rows = self.database.fetch(
            "SELECT id, name, email FROM users WHERE email = %s AND password = %s",
            (email, self.hash_password(password)))
        if len(rows) == 1:
            return rows[0]
        return None
