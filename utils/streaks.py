from datetime import date, datetime, timedelta

from utils.supabase_client import supabase


def get_user_streak(username):

    response = supabase.table("streaks") \
        .select("*") \
        .eq("username", username) \
        .execute()

    if response.data:

        return int(
            response.data[0]["streak"]
        )

    return 0


def update_streak(username):

    today = str(date.today())

    response = supabase.table("streaks") \
        .select("*") \
        .eq("username", username) \
        .execute()

    # =========================
    # NEW USER
    # =========================

    if not response.data:

        supabase.table("streaks").insert({

            "username": username,

            "last_date": today,

            "streak": 1

        }).execute()

        return

    # =========================
    # EXISTING USER
    # =========================

    user_data = response.data[0]

    last_date = datetime.strptime(

        user_data["last_date"],

        "%Y-%m-%d"

    ).date()

    streak = int(
        user_data["streak"]
    )

    today_date = date.today()

    # SAME DAY
    if last_date == today_date:

        return

    # CONTINUE STREAK
    elif last_date == today_date - timedelta(days=1):

        streak += 1

    # RESET STREAK
    else:

        streak = 1

    supabase.table("streaks") \
        .update({

            "last_date": today,

            "streak": streak

        }) \
        .eq("username", username) \
        .execute()