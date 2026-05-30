from flask import Flask, render_template, redirect, url_for, session, request

from data.stretches import get_all_stretches, get_stretch_by_id
from data.leaderboard import get_mock_leaderboard, get_reward_badge
from utils.scoring import calculate_points, calculate_total_points
from utils.stretch_rules import can_complete_stretch, get_completion_message
from utils.auth import register_user, validate_login


app = Flask(__name__, static_folder="public", static_url_path="")

# Needed for Flask session storage.
app.secret_key = "ude-stretch-prototype-secret"


@app.route("/")
def home():
    if "username" not in session:
        return redirect(url_for("login"))
    """
    Show homepage with all stretch options.
    """
    stretches = get_all_stretches()
    completed_stretches = session.get("completed_stretches", [])

    total_points = calculate_total_points(completed_stretches, stretches)
    username = session.get("username", "Guest")

    return render_template(
        "index.html",
        stretches=stretches,
        completed_stretches=completed_stretches,
        total_points=total_points,
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
    """
    stretch = get_stretch_by_id(stretch_id)

    if not can_complete_stretch(stretch):
        return redirect(url_for("home"))

    completed_stretches = session.get("completed_stretches", [])

    if stretch_id not in completed_stretches:
        completed_stretches.append(stretch_id)

    session["completed_stretches"] = completed_stretches

    all_stretches = get_all_stretches()
    total_points = calculate_total_points(completed_stretches, all_stretches)
    points_earned = calculate_points(stretch)
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
    """
    Show leaderboard and reward badge.
    """
    stretches = get_all_stretches()
    completed_stretches = session.get("completed_stretches", [])

    total_points = calculate_total_points(completed_stretches, stretches)
    leaderboard = get_mock_leaderboard(total_points)
    reward_badge = get_reward_badge(total_points)

    return render_template(
        "leaderboard.html",
        leaderboard=leaderboard,
        total_points=total_points,
        reward_badge=reward_badge,
    )


@app.route("/reset")
def reset_progress():
    """
    Clear prototype progress.
    """
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)