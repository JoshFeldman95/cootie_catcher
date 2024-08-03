import pyxel
from sim import Pandemic
import consts as c
from components import (
    GameStats,
    Heading,
    Place,
    NextDayButton,
    IntroInfoBox,
    MiddleGameInfoBox,
    EndGameInfoBox,
)

from map import Map, MapButton


class GameState:
    intro_screen_shown = False
    middle_game_screen_shown = False
    end_game_screen_shown = False
    map_visible = False


class App:
    def __init__(self):
        pyxel.init(
            c.SCREEN_WIDTH, c.SCREEN_HEIGHT, title="Cootie Catcher", display_scale=2
        )
        pyxel.playm(0, loop=True)
        pyxel.mouse(True)

        self.game_state = GameState()
        self.sim = Pandemic()
        self.stats = GameStats()
        self.heading = Heading()
        self.intro = IntroInfoBox(filename="intro.txt")
        self.middle_game_info = MiddleGameInfoBox(filename="middle_game.txt")
        self.end_game_info = EndGameInfoBox(filename="end_game.txt")
        self.map = Map()
        self.map_button = MapButton()

        y_init = c.ROW_HEIGHT + c.BORDER
        self.places = [
            Place(
                place=place_data,
                x=0,
                y=y_init + idx * c.ROW_HEIGHT,
                width=c.SCREEN_WIDTH,
                height=c.ROW_HEIGHT,
            )
            for idx, place_data in enumerate(self.sim.cities.values())
        ]

        self.next_button = NextDayButton()
        pyxel.run(self.update, self.draw)

    def update(self):
        self.intro.update(self.game_state)
        self.middle_game_info.update(self.game_state)
        self.end_game_info.update(self.game_state)
        self.map_button.update(self.game_state)

        for place in self.places:
            place.update(self.sim)

        self.next_button.update(self.sim)

    def draw(self):
        pyxel.cls(c.BACKGROUND_COLOR)

        if self.sim.days_since_last_infection == c.WIN_THRESHOLD:
            self.win()
            return

        if self.sim.pct_dead >= c.LOSE_THRESHOLD:
            self.lose()
            return

        if not self.game_state.intro_screen_shown:
            self.intro.draw()
            return

        if (
            not self.game_state.middle_game_screen_shown
        ) and self.sim.day == c.MIDDLE_CUTOFF:
            self.middle_game_info.draw()
            return

        if (not self.game_state.end_game_screen_shown) and self.sim.day == c.END_CUTOFF:
            self.end_game_info.draw()
            return

        if self.game_state.map_visible:
            self.map.draw(self.sim)

        else:
            self.stats.draw(sim=self.sim)
            for place in self.places:
                place.draw(self.sim)
            self.heading.draw()

        # Draw next button
        self.next_button.draw()
        self.map_button.draw(self.game_state)

    def win(self):
        pyxel.rect(
            c.SCREEN_WIDTH / 2 - 100 / 2, c.SCREEN_HEIGHT / 2 - 50 / 2, 100, 50, c.LIGHT
        )
        win_text = "You Win!"
        pyxel.text(
            c.SCREEN_WIDTH / 2 - len(win_text) / 2 * 4,
            c.SCREEN_HEIGHT / 2 - 5,
            win_text,
            c.DARK,
        )

    def lose(self):
        pyxel.rect(
            c.SCREEN_WIDTH / 2 - 100 / 2, c.SCREEN_HEIGHT / 2 - 50 / 2, 100, 50, c.LIGHT
        )
        lose_text = "You Lose :("
        pyxel.text(
            c.SCREEN_WIDTH / 2 - len(lose_text) / 2 * 4,
            c.SCREEN_HEIGHT / 2 - 5,
            lose_text,
            c.DARK,
        )


App()
