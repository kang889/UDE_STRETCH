"""
Checks simple stretch completion rules.
"""


def is_valid_stretch(stretch):
    """
    Check if selected stretch exists.
    """
    return stretch is not None


def can_complete_stretch(stretch):
    """
    Check if stretch can be marked complete.
    """
    return is_valid_stretch(stretch)


def get_completion_message(stretch):
    """
    Return completion message for stretch.
    """
    if stretch is None:
        return "Stretch not found."

    return f"You completed {stretch['name']}!"