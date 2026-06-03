from flask import Flask, render_template, redirect, url_for, session, request

from data.stretches import get_all_stretches, get_stretch_by_id
from data.leaderboard import get_reward_badge
from utils.scoring import calculate_points
from utils.stretch_rules import can_complete_stretch, get_completion_message
from utils.auth import register_user, validate_login, update_user_points, get_user_data, get_all_users, add_friend, get_friends, get_friend_leaderboard, remove_friend
from utils.levels import get_level_info
from utils.streaks import get_user_streak, update_streak


app = Flask(__name__, static_folder="public", static_url_path="")

# Needed for Flask session storage.
app.secret_key = "ude-stretch-prototype-secret"


@app.route("/")
def home():

    if "username" not in session:
        return redirect(url_for("login"))

    username = session.get("username")
    stretches = get_all_stretches()
    user_data = get_user_data(username)
    total_points = user_data["points"]
    currency = user_data["currency"]
    completed_stretches = session.get(
        "completed_stretches",
        []
    )

    return render_template(
        "index.html",
        stretches=stretches,
        completed_stretches=completed_stretches,
        total_points=total_points,
        currency=currency,
        username=username,
    )


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if validate_login(username, password):

            session["username"] = username

            return redirect(url_for("home"))

        return render_template(
            "login.html",
            error="Incorrect login details."
        )

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        success = register_user(username, password)

        if success:
            return render_template(
                "register_success.html"
            )

        return render_template(
            "register.html",
            error="Username already exists."
        )

    return render_template("register.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


@app.route("/stretch/<stretch_id>")
def stretch_page(stretch_id):
    if "username" not in session:
        return redirect(url_for("login"))
    """
    Show selected stretch instructions.
    """
    stretch = get_stretch_by_id(stretch_id)

    if stretch is None:
        return redirect(url_for("home"))

    return render_template("stretch.html", stretch=stretch)

@app.route("/complete/<stretch_id>")
def complete_stretch(stretch_id):
    """
    Mark selected stretch as completed.
    Award points only once per stretch per login session.
    """

    if "username" not in session:
        return redirect(url_for("login"))

    stretch = get_stretch_by_id(stretch_id)

    if not can_complete_stretch(stretch):
        return redirect(url_for("home"))

    username = session.get("username")

    completed_stretches = session.get(
        "completed_stretches",
        []
    )

    points_earned = 0

    if stretch_id not in completed_stretches:
        completed_stretches.append(stretch_id)

        points_earned = calculate_points(stretch)

        update_user_points(
            username,
            points_earned
        )

        update_streak(username)

    session["completed_stretches"] = completed_stretches

    user_data = get_user_data(username)
    total_points = user_data["points"]

    message = get_completion_message(stretch)

    return render_template(
        "complete.html",
        stretch=stretch,
        message=message,
        points_earned=points_earned,
        total_points=total_points,
    )

@app.route("/leaderboard")
def leaderboard_page():
    users = get_all_users()
    leaderboard = sorted(
        users,
        key=lambda user: int(user["points"]),
        reverse=True
    )

    username = session.get("username")
    user_data = get_user_data(username)
    total_points = user_data["points"]
    reward_badge = get_reward_badge(
        int(total_points)
    )

    return render_template(
        "leaderboard.html",
        leaderboard=leaderboard,
        total_points=total_points,
        reward_badge=reward_badge,
    )


@app.route("/friend-leaderboard")
def friend_leaderboard_page():

    if "username" not in session:
        return redirect(url_for("login"))

    username = session.get("username")

    leaderboard = get_friend_leaderboard(
        username
    )

    user_data = get_user_data(username)

    total_points = user_data["points"]

    reward_badge = get_reward_badge(
        int(total_points)
    )

    return render_template(
        "leaderboard.html",
        leaderboard=leaderboard,
        total_points=total_points,
        reward_badge=reward_badge,
    )


@app.route("/rewards")
def rewards_page():

    if "username" not in session:
        return redirect(url_for("login"))

    username = session.get("username")

    user_data = get_user_data(username)

    currency = user_data["currency"]

    return render_template(
        "rewards.html",
        username=username,
        currency=currency,
    )

@app.route("/friends", methods=["GET", "POST"])
def friends_page():

    if "username" not in session:
        return redirect(url_for("login"))

    username = session.get("username")

    error = None

    if request.method == "POST":

        friend_username = request.form["friend_username"]

        success = add_friend(
            username,
            friend_username
        )

        if not success:

            error = (
                "Unable to add friend."
            )

    friends = get_friends(username)

    return render_template(
        "friends.html",
        username=username,
        friends=friends,
        error=error,
    )


@app.route("/remove-friend/<friend>")
def remove_friend_page(friend):

    if "username" not in session:
        return redirect(url_for("login"))

    username = session.get("username")

    remove_friend(
        username,
        friend
    )

    return redirect(
        url_for("friends_page")
    )

@app.route("/streak")
def streak_page():

    if "username" not in session:
        return redirect(url_for("login"))

    username = session.get("username")

    streak = get_user_streak(username)

    return render_template(

        "streak.html",

        streak=streak
    )


@app.route("/profile")
def profile_page():

    username = session.get("username")

    user_data = get_user_data(username)

    streak = get_user_streak(username)
    
    level_data = get_level_info(
        int(user_data["points"])
    )

    return render_template(

    "profile.html",

    user=user_data,

    level_data=level_data,

    streak=streak
)


if __name__ == "__main__":
    app.run(debug=True)

