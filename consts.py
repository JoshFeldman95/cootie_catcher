TOTAL_POPULATION = 3000
PLACE_COUNT = 20

#
TRAVEL_RATE = 0.01
INFECTION_RATE = 0.1
INCUBATION_RATE = 1 / 3
DETECTION_RATE = 0.5
TREATMENT_RATE = 0.9
TREATMENT_CAPACITY = 0.01
MORTALITY_RATE = 0.05
RECOVERY_RATE = 1 / 7
CONTACTS = 10
MASS_TESTING_DETECTION_RATE = 1
CONTACT_TRACING_CAPACITY = 50

PLACE_NAMES = [
    "Little Sprouts Preschool",
    "Tiny Tots Academy",
    "Happy Faces Childcare",
    "Rainbow Kids Preschool",
    "Sunshine Daycare",
    "Playful Pals Nursery",
    "Creative Kids Learning Center",
    "Bright Beginnings Preschool",
    "Caterpillar Corner",
    "Magic Garden Preschool",
    "Adventureland Childcare",
    "Busy Bees Academy",
    "Imagination Station",
    "Wonderland Preschool",
    "Dreamy Days Nursery",
    "Starshine Kids Center",
    "Giggles and Grins Preschool",
    "Sunny Skies Childcare",
    "Little Explorers Academy",
    "Cuddle Bugs Daycare",
]

ACTION_BUDGET_BEGINNING = 4
ACTION_BUDGET_MIDDLE = 10
ACTION_BUDGET_END = 20
ANGER_THRESHOLD = 5
MIDDLE_CUTOFF = 10
END_CUTOFF = 20


WIN_THRESHOLD = 10
LOSE_THRESHOLD = 20
ROW_HEIGHT = 10
COL_WIDTH = 60

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 280
BORDER = 5
BOTTOM_MENU_HEIGHT = SCREEN_HEIGHT - 20

HIGHLIGHT_COLOR_LIGHT = 15
HIGHLIGHT_COLOR_DARK = 14
SELECTED_COLOR = 8
LIGHT = 7
DARK = 1
ALERT_COLOR = 8
BACKGROUND_COLOR = 6
GREEN = 3
ORANGE = 9

CHARACTER_WIDTH = 4
CHARACTER_HEIGHT = 6

ACTIONS = {
    "restrict_travel": "Ban Playdates",
    "mass_testing": "Test the Class",
    "contact_tracing": "Quarantine",
    "lockdown": "Close School",
}

COLUMNS = [
    ("School", "The name of the school."),
    ("Healthy", "The number of healthy kids (so we think...)"),
    ("Caught Cooties", "The number of kids who we think caught cooties."),
    (
        "Treated",
        "The number of kids undergoing cootie treatment, which will make recovery more likely.",
    ),
    (
        "Homeschooled",
        "The number of kids who have been pulled from school due to cooties.",
    ),
    (
        "Parent Anger",
        f"The amount parents are angry. If it gets to {ANGER_THRESHOLD}, watch out. You won't be able to take any more actions for {ANGER_THRESHOLD} turns.",
    ),
    (
        ACTIONS["restrict_travel"],
        "This will stop kids from spreading cooties to other schools",
    ),
    (ACTIONS["mass_testing"], "Figure out how many kids really have cooties"),
    (
        ACTIONS["contact_tracing"],
        f"Kids at this school won't spread cooties to other kids at this school, but we can only quarantine {CONTACT_TRACING_CAPACITY} kids.",
    ),
    (ACTIONS["lockdown"], "No new infections! But parents will be angry..."),
]
