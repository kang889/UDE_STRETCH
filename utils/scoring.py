"""
Handles stretch point calculation.
"""


def calculate_points(stretch):
    """
    Return points for one completed stretch.
    """
    if stretch is None:
        return 0

    return stretch.get("points", 0)


def calculate_bonus(completed_count, total_stretches):
    """
    Return bonus points if all stretches are completed.
    """
    if completed_count == total_stretches:
        return 20

    return 0


def calculate_total_points(completed_stretches, all_stretches):
    """
    Return total points from completed stretches.
    """
    total = 0

    for stretch in all_stretches:
        if stretch["id"] in completed_stretches:
            total += calculate_points(stretch)

    total += calculate_bonus(len(completed_stretches), len(all_stretches))

    return total