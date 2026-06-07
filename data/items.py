"""
Stores avatar item unlocks for the prototype.
Items are unlocked automatically based on total points.
"""

ITEMS = [
    {
        "id": "none",
        "name": "No Item",
        "required_points": 0,
        "description": "Default avatar with no cosmetic item."
    },
    {
        "id": "crown",
        "name": "Crown",
        "required_points": 30,
        "description": "A crown for users starting their movement streak."
    },
    {
        "id": "halo",
        "name": "Halo",
        "required_points": 60,
        "description": "A halo for consistent movement progress."
    },
    {
        "id": "sunglasses",
        "name": "Sunglasses",
        "required_points": 100,
        "description": "A cool avatar item for high-scoring users."
    },
    {
        "id": "mystery",
        "name": "Locked Mystery Item",
        "required_points": 150,
        "description": "A future reward to show progression.",
         "is_future_item": True
    },
]

def get_all_items():
    return ITEMS


def get_item_by_id(item_id):
    for item in ITEMS:
        if item["id"] == item_id:
            return item

    return None


def is_item_unlocked(item, points):
    return points >= item["required_points"]

def get_latest_unlocked_item(points):
    """
    Return the latest unlocked real item based on points.
    Future placeholder items are ignored.
    """

    latest_item = "none"
    highest_required_points = -1

    for item in ITEMS:

        if item.get("is_future_item", False):
            continue

        if (
            points >= item["required_points"]
            and item["required_points"] > highest_required_points
        ):
            latest_item = item["id"]
            highest_required_points = item["required_points"]

    return latest_item