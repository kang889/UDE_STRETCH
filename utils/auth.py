import csv
import os

USERS_FILE = "data/users.csv"


def register_user(username, password):

    if user_exists(username):
        return False

    file_exists = os.path.isfile(USERS_FILE)

    with open(USERS_FILE, "a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["username", "password"])

        writer.writerow([username, password])

    return True


def user_exists(username):

    if not os.path.isfile(USERS_FILE):
        return False

    with open(USERS_FILE, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["username"] == username:
                return True

    return False


def validate_login(username, password):

    if not os.path.isfile(USERS_FILE):
        return False

    with open(USERS_FILE, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if (
                row["username"] == username and
                row["password"] == password
            ):
                return True

    return False