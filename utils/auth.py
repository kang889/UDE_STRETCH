from utils.supabase_client import supabase


# =========================
# USER SYSTEM
# =========================

def register_user(username, password):

    existing = supabase.table("users") \
        .select("*") \
        .eq("username", username) \
        .execute()

    if existing.data:
        return False

    supabase.table("users").insert({

        "username": username,
        "password": password,
        "points": 0,
        "currency": 0

    }).execute()

    return True


def user_exists(username):

    response = supabase.table("users") \
        .select("*") \
        .eq("username", username) \
        .execute()

    return len(response.data) > 0


def validate_login(username, password):

    response = supabase.table("users") \
        .select("*") \
        .eq("username", username) \
        .eq("password", password) \
        .execute()

    return len(response.data) > 0


# =========================
# USER DATA
# =========================

def get_user_data(username):

    response = supabase.table("users") \
        .select("*") \
        .eq("username", username) \
        .execute()

    if response.data:

        return response.data[0]

    return None


def get_all_users():

    response = supabase.table("users") \
        .select("*") \
        .execute()

    return response.data


# =========================
# POINT SYSTEM
# =========================

def update_user_points(username, points_to_add):

    user = get_user_data(username)

    current_points = int(
        user["points"]
    )

    current_currency = int(
        user["currency"]
    )

    new_points = (
        current_points
        + points_to_add
    )

    new_currency = (
        current_currency
        + points_to_add
    )

    supabase.table("users") \
        .update({

            "points": new_points,
            "currency": new_currency

        }) \
        .eq("username", username) \
        .execute()


# =========================
# FRIEND SYSTEM
# =========================

def add_friend(user, friend):

    if user == friend:
        return False

    if not user_exists(friend):
        return False

    existing = supabase.table("friends") \
        .select("*") \
        .eq("user", user) \
        .eq("friend", friend) \
        .execute()

    if existing.data:
        return False

    # USER -> FRIEND

    supabase.table("friends").insert({

        "user": user,
        "friend": friend

    }).execute()

    # FRIEND -> USER

    supabase.table("friends").insert({

        "user": friend,
        "friend": user

    }).execute()

    return True


def get_friends(user):

    response = supabase.table("friends") \
        .select("*") \
        .eq("user", user) \
        .execute()

    friends = []

    for row in response.data:

        friends.append(
            row["friend"]
        )

    return friends


def remove_friend(user, friend):

    supabase.table("friends") \
        .delete() \
        .eq("user", user) \
        .eq("friend", friend) \
        .execute()

    supabase.table("friends") \
        .delete() \
        .eq("user", friend) \
        .eq("friend", user) \
        .execute()


# =========================
# FRIEND LEADERBOARD
# =========================

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

        key=lambda user: int(
            user["points"]
        ),

        reverse=True
    )

    return sorted_friends
