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
        "description": "A future reward to show progression."
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