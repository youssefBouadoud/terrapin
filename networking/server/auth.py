import hashlib
import os
import json
import time
import uuid

import jwt

SECRET_KEY = os.environ['SECRET_KEY']


class AuthenticationService:
    def __init__(self):
        self.users = {}  # Dictionary to store user credentials {username: (hashed_password, salt)}

        # Load user credentials from file if present
        if os.path.exists("users.json"):
            with open("users.json", "r") as f:
                self.users = json.load(f)

    def register_user(self, username, password):
        # Generate salt and hash password
        salt = os.urandom(32)
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

        self.users[username] = {
            "hash": hashed_password.hex(),
            "salt": salt.hex(),
        }
        self._save_users_to_file()  # Save users to file
        return True

    def verify_password(self, password, stored_hash, salt):
        input_hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), 100000)
        if stored_hash == input_hashed_password.hex():
            return True

    def authenticate_user(self, username, password):
        if username in self.users and self.verify_password(password, self.users[username]["hash"],
                                                           self.users[username]["salt"]):
            jwt_token = self.generate_jwt(username)
            return True, jwt_token
        else:
            return False, None

    def generate_jwt(self, username, expiration_seconds=3600):
        payload = {
            "username": username,
            "iat": int(time.time()),
            "exp": int(time.time() + expiration_seconds)
        }

        jwt_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return jwt_token

    def verify_jwt(self, jwt_token):
        try:
            payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=["HS256", ])
            current_time = time.time()
            expiration_time = payload.get("exp")
            if expiration_time and expiration_time < current_time:
                return None

            return payload["username"]
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def _save_users_to_file(self):
        with open("users.json", "w") as f:
            json.dump(self.users, f)


# Example usage:
if __name__ == "__main__":
    auth_service = AuthenticationService()

    # Register a new user
    auth_service.register_user("user123", "password123")

    # Authenticate a user
    token = auth_service.authenticate_user("user123", "password123")[1]
    print(token)
    print(auth_service.verify_jwt(token))
