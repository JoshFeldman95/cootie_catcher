import pyxel
import consts as c


class Hoverable:
    def is_hovered(self):
        x, y = pyxel.mouse_x, pyxel.mouse_y
        return (
            x >= self.x
            and x <= self.x + self.width
            and y >= self.y
            and y <= self.y + self.height
        )


class Clickable(Hoverable):
    def is_clicked(self):
        return self.is_hovered() and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)


class Button(Clickable):
    def __init__(self, x, y, width, height, text):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(
        self,
    ):
        if self.is_hovered():
            pyxel.rect(self.x, self.y, self.width, self.height, c.HIGHLIGHT_COLOR_DARK)
        else:
            pyxel.rect(self.x, self.y, self.width, self.height, c.HIGHLIGHT_COLOR_LIGHT)

        pyxel.text(self.x + 5, self.y + 2, self.text, c.DARK)


class Checkbox(Clickable):
    def draw(
        self,
    ):

        if self.is_hovered():
            pyxel.rect(self.x, self.y, self.width, self.height, c.HIGHLIGHT_COLOR_DARK)
        elif self.is_checked:
            pyxel.rect(self.x, self.y, self.width, self.height, c.SELECTED_COLOR)
        else:
            pyxel.rect(self.x, self.y, self.width, self.height, c.DARK)


class ActionCheckbox(Checkbox):
    def __init__(self, x, y, size, place_name, action_name):
        self.x = x
        self.y = y
        self.width = size
        self.height = size
        self.place_name = place_name
        self.action_name = action_name
        self.is_checked = False

    def update(self, sim):
        is_checkable = sim.action_budget - sim.action_count > 0
        if self.is_clicked():
            if not self.is_checked and is_checkable > 0:
                self.is_checked = True
                sim.cities[self.place_name].control_measures[self.action_name] = True

            elif self.is_checked:
                self.is_checked = False
                sim.cities[self.place_name].control_measures[self.action_name] = False


class Place(Hoverable):
    def __init__(self, place, x, y, width, height):
        self.place = place
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.checkboxes = {
            "restrict_travel": ActionCheckbox(
                x=c.COL_WIDTH * (6 + 0) + c.BORDER,
                y=self.y + 2,
                size=5,
                place_name=place.place_name,
                action_name="restrict_travel",
            ),
            "mass_testing": ActionCheckbox(
                x=c.COL_WIDTH * (6 + 1) + c.BORDER,
                y=self.y + 2,
                size=5,
                place_name=place.place_name,
                action_name="mass_testing",
            ),
            "contact_tracing": ActionCheckbox(
                x=c.COL_WIDTH * (6 + 2) + c.BORDER,
                y=self.y + 2,
                size=5,
                place_name=place.place_name,
                action_name="contact_tracing",
            ),
            "lockdown": ActionCheckbox(
                x=c.COL_WIDTH * (6 + 3) + c.BORDER,
                y=self.y + 2,
                size=5,
                place_name=place.place_name,
                action_name="lockdown",
            ),
        }

    def draw(self):
        if self.is_hovered():
            pyxel.rect(self.x, self.y, self.width, self.height, c.HIGHLIGHT_COLOR_LIGHT)

        fields = (
            self.place.place_name,
            self.place.susceptible + self.place.exposed + self.place.infected,
            self.place.detected,
            self.place.treated,
            self.place.dead,
        )
        for idx, f in enumerate(fields):
            color = c.DARK if f == 0 or idx < 2 else c.ALERT_COLOR

            if idx > 0:
                idx += 1
            pyxel.text(c.COL_WIDTH * idx + c.BORDER, self.y + 2, str(f), color)

        for idx, action in enumerate(self.checkboxes):
            self.checkboxes[action].draw()

    def update(self, sim):
        for checkbox in self.checkboxes.values():
            checkbox.update(sim)


class GameStats:
    def draw(self, sim, days_since_last_infection, pct_homeschooled):
        pyxel.text(
            c.BORDER,
            c.SCREEN_HEIGHT - c.BORDER - 40,
            f"Days since last infection: {days_since_last_infection} ({c.WIN_THRESHOLD- days_since_last_infection} more to win!)",
            c.DARK,
        )
        pyxel.text(
            c.BORDER,
            c.SCREEN_HEIGHT - c.BORDER - 30,
            f"Action count: {sim.action_count} (Remaining: {sim.action_budget - sim.action_count})",
            c.DARK,
        )
        pyxel.text(c.BORDER, c.SCREEN_HEIGHT - c.BORDER - 20, f"Day: {sim.day}", c.DARK)
        pyxel.text(
            c.BORDER,
            c.SCREEN_HEIGHT - c.BORDER - 10,
            f"Homeschooled: {pct_homeschooled} % (Lose at {c.LOSE_THRESHOLD}%)",
            c.DARK,
        )


class Heading:
    def draw(self):
        column_names = [
            "Place",
            "Health",
            "Caught Cooties",
            "Treated",
            "Homeschooled",
            "Ban Playdates",
            "Test the Class",
            "Quarantine",
            "Close School",
        ]
        for idx, name in enumerate(column_names):
            if idx > 0:
                idx += 1
            pyxel.text(c.COL_WIDTH * idx + c.BORDER, c.BORDER, name, c.DARK)

        pyxel.line(
            0, c.ROW_HEIGHT + c.BORDER, c.SCREEN_WIDTH, c.ROW_HEIGHT + c.BORDER, c.DARK
        )
