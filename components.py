import pyxel
import consts as c
import textwrap
import time


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
    text_padding = 5
    height = c.CHARACTER_HEIGHT + text_padding * 2

    def __init__(self, text, x=None, y=None):
        if not x:
            x = (
                c.SCREEN_WIDTH / 2
                - len(text) * c.CHARACTER_WIDTH / 2
                - self.text_padding
            )
        self.x = x

        if not y:
            y = c.SCREEN_HEIGHT / 2 - c.CHARACTER_HEIGHT / 2 - self.text_padding
        self.y = y

        self.text = text
        self.width = len(text) * c.CHARACTER_WIDTH + self.text_padding * 2

    def draw(
        self,
    ):
        if self.is_hovered():
            pyxel.rect(self.x, self.y, self.width, self.height, c.HIGHLIGHT_COLOR_DARK)
        else:
            pyxel.rect(self.x, self.y, self.width, self.height, c.HIGHLIGHT_COLOR_LIGHT)

        pyxel.text(
            x=self.x + self.text_padding,
            y=self.y + self.text_padding,
            s=self.text,
            col=c.DARK,
        )


class NextDayButton:
    next_button_text = "Call it a day >"
    x = (
        c.SCREEN_WIDTH
        - len(next_button_text) * c.CHARACTER_WIDTH
        - Button.text_padding * 2
        - c.BORDER
    )

    def __init__(self):
        self.next_button = Button(
            x=self.x,
            y=c.BOTTOM_MENU_HEIGHT,
            text=self.next_button_text,
        )

    def draw(self):
        self.next_button.draw()

    def update(self, sim):
        if self.next_button.is_clicked():
            sim.update()  # Update simulation only if next button is pressed


class InfoBox:
    def __init__(self, filename=None, text=None):
        if filename:
            with open(filename, "r") as file:
                text = file.read()
        else:
            if not text:
                raise ValueError("Either filename or text must be provided")

        # constants
        self.is_shown = False
        self.characters_per_line = 30
        self.character_width = 4
        self.character_height = 6
        self.padding = 10
        self.padding_between_text_and_button = 10
        self.text = textwrap.fill(text, width=self.characters_per_line)
        text_height = (self.text.count("\n") + 1) * c.CHARACTER_HEIGHT
        text_width = self.characters_per_line * c.CHARACTER_WIDTH

        self.text_drawn = 0
        self.time_elapsed = 0

        self.width = self.padding + text_width + self.padding
        self.height = (
            self.padding
            + text_height
            + self.padding_between_text_and_button
            + Button.height
            + self.padding
        )

        # Position the middle of the box at the center of the screen
        self.x = c.SCREEN_WIDTH / 2 - self.width / 2
        self.y = c.SCREEN_HEIGHT / 2 - self.height / 2

        self.next_button = Button(
            y=self.y + self.height - Button.height - self.padding,
            text="Next >",
        )

    def draw(self):
        self.is_shown = True

        # every 10 milliseconds, draw one more character
        if self.text_drawn < len(self.text) and time.time() - self.time_elapsed > 0.005:
            self.text_drawn += 1
            self.time_elapsed = time.time()
        text_to_draw = self.text[: self.text_drawn]

        pyxel.rect(self.x, self.y, self.width, self.height, c.LIGHT)
        pyxel.text(self.x + self.padding, self.y + self.padding, text_to_draw, c.DARK)
        self.next_button.draw()

    def is_clicked(self):
        return self.is_shown and self.next_button.is_clicked()


class IntroInfoBox(InfoBox):
    def update(self, game_state):
        if self.is_clicked():
            game_state.intro_screen_shown = True


class MiddleGameInfoBox(InfoBox):
    def update(self, game_state):
        if self.is_clicked():
            game_state.middle_game_screen_shown = True


class EndGameInfoBox(InfoBox):
    def update(self, game_state):
        if self.is_clicked():
            game_state.end_game_screen_shown = True


class ActionCheckbox(Clickable):
    def __init__(self, x, y, size, place_name, action_name):
        self.x = x
        self.y = y
        self.width = size
        self.height = size
        self.place_name = place_name
        self.action_name = action_name

    def draw(self, sim):
        if self.is_hovered():
            pyxel.rect(self.x, self.y, self.width, self.height, c.HIGHLIGHT_COLOR_DARK)
        elif self.is_checked(sim):
            pyxel.rect(self.x, self.y, self.width, self.height, c.SELECTED_COLOR)
        else:
            pyxel.rect(self.x, self.y, self.width, self.height, c.DARK)

    def is_checked(self, sim):
        return sim.cities[self.place_name].control_measures[self.action_name]

    def update(self, sim):
        is_checkable = sim.action_budget - sim.action_count > 0
        if self.is_clicked():
            if not self.is_checked(sim) and is_checkable:
                sim.cities[self.place_name].control_measures[self.action_name] = True

            elif self.is_checked(sim):
                sim.cities[self.place_name].control_measures[self.action_name] = False


class Place(Hoverable):
    def __init__(self, place, x, y, width, height):
        self.place = place
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.checkboxes = {
            action: ActionCheckbox(
                x=c.COL_WIDTH * (6 + idx + 1)
                + c.BORDER,  # 6 is the number of columns before the action columns
                y=self.y + 2,
                size=5,
                place_name=place.place_name,
                action_name=action,
            )
            for idx, action in enumerate(c.ACTIONS)
        }

    def draw(self, sim):
        fields = (
            self.place.place_name,
            self.place.susceptible + self.place.exposed + self.place.infected,
            self.place.detected,
            self.place.treated,
            self.place.dead,
            self.place.anger,
        )

        if self.is_hovered():
            pyxel.rect(self.x, self.y, self.width, self.height, c.HIGHLIGHT_COLOR_LIGHT)

        for idx, f in enumerate(fields):
            color = c.DARK if f == 0 or idx < 2 else c.ALERT_COLOR

            if idx > 0:  # two columns for the place name
                idx += 1

            if idx == 6:
                stat_str = (
                    f"{f}/5"
                    if not self.place.in_backlash
                    else f"Parents are pissed! ({f} turns remaining)"
                )
            else:
                stat_str = str(f)

            pyxel.text(c.COL_WIDTH * idx + c.BORDER, self.y + 2, stat_str, color)

        for idx, action in enumerate(self.checkboxes):
            if not self.place.in_backlash:
                self.checkboxes[action].draw(sim)

    def update(self, sim):
        for checkbox in self.checkboxes.values():
            checkbox.update(sim)


class GameStats:
    def draw(self, sim):
        pyxel.text(
            c.BORDER,
            c.SCREEN_HEIGHT - c.BORDER - 40,
            f"Days since last infection: {sim.days_since_last_infection} ({c.WIN_THRESHOLD- sim.days_since_last_infection} more to win!)",
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
            f"Homeschooled: {sim.pct_dead} % (Lose at {c.LOSE_THRESHOLD}%)",
            c.DARK,
        )


class ColumnName(Hoverable):
    def __init__(self, x, y, s, col, description):
        self.x = x
        self.y = y
        self.width = c.COL_WIDTH
        self.height = c.ROW_HEIGHT
        self.text = s
        self.description = textwrap.fill(
            description, width=c.COL_WIDTH // c.CHARACTER_WIDTH
        )
        self.color = col

    def draw(self):
        pyxel.text(self.x, self.y, self.text, self.color)

        if self.is_hovered():
            pyxel.rect(
                x=self.x - 5,
                y=self.y + self.height - 5,
                w=self.width + 10,
                h=(self.description.count("\n") + 1) * c.CHARACTER_HEIGHT + 10,
                col=c.DARK,
            )
            pyxel.text(self.x, self.y + self.height, self.description, c.LIGHT)


class Heading:
    def __init__(self):
        self.column_names = []
        for idx, (name, description) in enumerate(c.COLUMNS):
            if idx > 0:
                idx += 1

            self.column_names.append(
                ColumnName(
                    x=c.COL_WIDTH * idx + c.BORDER,
                    y=c.BORDER,
                    s=name,
                    col=c.DARK,
                    description=description,
                )
            )

    def draw(self):

        pyxel.line(
            0, c.ROW_HEIGHT + c.BORDER, c.SCREEN_WIDTH, c.ROW_HEIGHT + c.BORDER, c.DARK
        )

        for column in self.column_names:
            column.draw()
