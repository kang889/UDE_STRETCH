def get_level_info(points):

    level = 1

    xp_needed = 20

    remaining_points = points

    while remaining_points >= xp_needed:

        remaining_points -= xp_needed

        level += 1

        xp_needed *= 2

    # =========================
    # RANK SYSTEM
    # =========================

    if level <= 2:

        badge = "bronze.png"

        rank = "Bronze"

        xp_to_next_rank = max(
            0,
            60 - points
        )

    elif level <= 4:

        badge = "silver.png"

        rank = "Silver"

        xp_to_next_rank = max(
            0,
            300 - points
        )

    else:

        badge = "gold.png"

        rank = "Gold"

        xp_to_next_rank = 0

    return {

        "level": level,

        "current_xp": remaining_points,

        "xp_needed": xp_needed,

        "badge": badge,

        "rank": rank,

        "xp_to_next_rank": xp_to_next_rank
    }