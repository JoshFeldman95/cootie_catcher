TOTAL_POPULATION = 3000
PLACE_COUNT = 20

#
TRAVEL_RATE = 0.01
INFECTION_RATE = 0.1
INCUBATION_RATE = 1 / 3
DETECTION_RATE = 0.1
TREATMENT_RATE = 0.9
TREATMENT_CAPACITY = 0.01
MORTALITY_RATE = 0.05
RECOVERY_RATE = 1 / 7
CONTACTS = 10
MASS_TESTING_DETECTION_RATE = 0.95
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


ACTIONS = [
    "restrict_travel",
    "mass_testing",
    "contact_tracing",
    "lockdown",
]

WIN_THRESHOLD = 10
LOSE_THRESHOLD = 20
ROW_HEIGHT = 10
COL_WIDTH = 60

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 280
BORDER = 5

HIGHLIGHT_COLOR_LIGHT = 15
HIGHLIGHT_COLOR_DARK = 14
SELECTED_COLOR = 8
LIGHT = 7
DARK = 1
ALERT_COLOR = 8
BACKGROUND_COLOR = 6
CHARACTER_WIDTH = 4
CHARACTER_HEIGHT = 6
