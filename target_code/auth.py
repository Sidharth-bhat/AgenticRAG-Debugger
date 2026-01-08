import hashlib

class UserManager:
    def __init__(self):
        self.users = {}

    def register(self, username, password):
        # We store the password as a hash for security
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        self.users[username] = hashed_pw
        print(f"User {username} registered.")

    def login(self, username, password):
        if username not in self.users:
            return "User not found"
        
        stored_password = self.users[username]
        
        # BUG: We are comparing the RAW password input with the HASHED password in the DB.
        # They will never match!
        if password == stored_password:
            return "Login Successful"
        else:
            return "Invalid Password"