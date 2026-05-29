"""
data/stretches.py

Stores the stretch exercises used in the prototype.

This file keeps the stretch content separate from the Flask routes,
so the team can easily add, remove, or edit stretches later without
rewriting the main app logic.
"""

STRETCHES = [
    {
        "id": "neck-side-stretch",
        "name": "Neck Side Stretch",
        "duration": 20,
        "points": 10,
        "sides": ["Left side", "Right side"],
        "description": "A simple seated stretch to reduce neck tension from long sitting.",
        "instructions": [
            "Sit upright with your shoulders relaxed.",
            "Gently tilt your head to one side.",
            "Hold the stretch without forcing your neck.",
            "Return to the centre and repeat on the other side."
        ],
        "correct_conditions": [
            "User remains seated or standing safely.",
            "User holds the stretch for the required timer duration.",
            "User completes both left and right sides.",
            "User clicks the completion button after finishing."
        ],
    },
    {
        "id": "shoulder-rolls",
        "name": "Shoulder Rolls",
        "duration": 20,
        "points": 10,
        "description": "A quick movement to loosen shoulders after desk work or studying.",
        "instructions": [
            "Sit or stand upright.",
            "Slowly roll your shoulders forward in a circular motion.",
            "After a few rolls, reverse the direction.",
            "Keep the movement controlled and comfortable."
        ],
        "correct_conditions": [
            "User keeps the movement slow and controlled.",
            "User rolls shoulders in both directions.",
            "User continues until the timer ends.",
            "User clicks the completion button after finishing."
        ],
    },
    {
        "id": "seated-torso-twist",
        "name": "Seated Torso Twist",
        "duration": 20,
        "points": 10,
        "sides": ["Left side", "Right side"],
        "description": "A seated stretch to reduce stiffness in the back and torso.",
        "instructions": [
            "Sit upright with both feet on the floor.",
            "Place one hand on the opposite side of your chair or thigh.",
            "Gently rotate your upper body to one side.",
            "Return to the centre and repeat on the other side."
        ],
        "correct_conditions": [
            "User keeps both feet stable on the floor.",
            "User twists gently without forcing the movement.",
            "User completes both left and right sides.",
            "User clicks the completion button after finishing."
        ],
    },
]


def get_all_stretches():
    """
    Return all available stretches.

    Used by the home page to display the stretch options.
    """
    return STRETCHES


def get_stretch_by_id(stretch_id):
    """
    Find and return one stretch by its id.

    Returns:
        dict: The matching stretch if found.
        None: If no stretch matches the given id.
    """
    for stretch in STRETCHES:
        if stretch["id"] == stretch_id:
            return stretch

    return None