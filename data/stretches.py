"""
data/stretches.py

Stores the stretch exercises used in the prototype.

This file keeps the stretch content separate from the Flask routes,
so the team can easily add, remove, or edit stretches later without
rewriting the main app logic.
"""

STRETCHES = [
    {
        "id": "side-body-stretch",
        "name": "Side Body Stretch",
        "duration": 16,
        "target_label": "8 seconds each side",
        "points": 10,
        "sides": ["Left side", "Right side"],
        "description": "Stretch your upper body gently to the left and right to reduce side-body stiffness.",
        "instructions": [
            "Stand or sit upright while facing the camera.",
            "Lean your upper body gently to one side.",
            "Hold the stretch for 8 seconds.",
            "Return to the centre and repeat on the other side.",
            "Hand placement does not matter for this prototype."
        ],
        "correct_conditions": [
            "User keeps their upper body visible.",
            "User leans clearly to the left side.",
            "User holds the left side stretch for 8 seconds.",
            "User leans clearly to the right side.",
            "User holds the right side stretch for 8 seconds."
        ],
    },
    {
         "id": "neck-stretch-calf-raises",
         "name": "Neck Stretch + Calf Raises",
         "duration": 16,
         "target_label": "8 calf raises each side",
         "points": 10,
         "sides": ["Left neck stretch", "Right neck stretch"],
         "description": "Gently guide your neck to each side while completing calf raises.",
        "instructions": [
        "Stand facing the camera with your body visible.",
        "Gently guide your head to one side using your hand.",
        "Do not force your neck.",
        "While holding the neck stretch, perform 8 calf raises.",
        "Switch to the other side and perform another 8 calf raises.",
        "Lower your heels fully between each calf raise."
           ],
        "correct_conditions": [
        "User keeps their face, shoulders, and body visible.",
        "User tilts the head sideways for the neck stretch.",
        "User completes 8 calf raises on the left neck stretch.",
        "User completes 8 calf raises on the right neck stretch.",
        "User moves slowly and safely."
    ],
    },
    {
        "id": "squat",
        "name": "Squat",
        "duration": 10,
        "target_label": "10 reps",
        "points": 10,
        "description": "Face the camera and complete 10 controlled squats.",
        "instructions": [
            "Stand facing the camera with your full body visible.",
            "Lower your hips into a squat.",
            "Stand back up fully.",
            "Repeat until you complete 10 reps."
        ],
        "correct_conditions": [
            "User keeps their body visible.",
            "User lowers their hips clearly.",
            "User returns to standing position.",
            "User completes 10 squat repetitions."
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