import csv
import os

USERS_FILE = "data/users.csv"
FRIENDS_FILE = "data/friends.csv"



def register_user(username, password):

    if user_exists(username):
        return False

    file_exists = os.path.isfile(USERS_FILE)

    with open(USERS_FILE, "a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([ "username", "password", "points", "currency" ])

        writer.writerow([username, password, 0, 0])

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

def update_user_points(username, points_to_add):

    rows = []

    with open(USERS_FILE, "r") as file:

        reader = csv.DictReader(file)

        for row in reader:

            if row["username"] == username:

                current_points = int(row["points"])
                current_currency = int(row["currency"])

                row["points"] = str(
                    current_points + points_to_add
                )

                row["currency"] = str(
                    current_currency + points_to_add
                )

            rows.append(row)

    with open(USERS_FILE, "w", newline="") as file:

        fieldnames = [
            "username",
            "password",
            "points",
            "currency"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

def get_user_data(username):
    with open(USERS_FILE, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username:
                return row
    return None

def get_all_users():
    with open(USERS_FILE, "r") as file:
        reader = csv.DictReader(file)
        return list(reader)
    

def add_friend(user, friend):

    if user == friend:
        return False

    if not user_exists(friend):
        return False

    file_exists = os.path.isfile(FRIENDS_FILE)

    existing_friends = get_friends(user)

    if friend in existing_friends:
        return False

    with open(FRIENDS_FILE, "a", newline="") as file:

        writer = csv.writer(file)

        if not file_exists:

            writer.writerow([
                "user",
                "friend"
            ])

        # USER -> FRIEND
        writer.writerow([
            user,
            friend
        ])

        # FRIEND -> USER
        writer.writerow([
            friend,
            user
        ])

    return True


def get_friends(user):

    friends = []

    if not os.path.isfile(FRIENDS_FILE):
        return friends

    with open(FRIENDS_FILE, "r") as file:

        reader = csv.DictReader(file)

        for row in reader:

            if row["user"] == user:

                friends.append(
                    row["friend"]
                )

    return friends

def get_friend_leaderboard(username):

    friend_usernames = get_friends(username)

    users = get_all_users()

    friend_data = []

    for user in users:

        if (
            user["username"] in friend_usernames
            or user["username"] == username
        ):

            friend_data.append(user)

    sorted_friends = sorted(
        friend_data,
        key=lambda user: int(user["points"]),
        reverse=True
    )

    return sorted_friends


def remove_friend(user, friend):

    rows = []

    with open(FRIENDS_FILE, "r") as file:

        reader = csv.DictReader(file)

        for row in reader:

            is_pair = (
                row["user"] == user
                and row["friend"] == friend
            )

            reverse_pair = (
                row["user"] == friend
                and row["friend"] == user
            )

            if not is_pair and not reverse_pair:

                rows.append(row)

    with open(FRIENDS_FILE, "w", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=["user", "friend"]
        )

        writer.writeheader()

        writer.writerows(rows)
