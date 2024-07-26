import pyxel
from sim import Pandemic
import consts as c
from components import GameStats, Heading, Place, Button


class App:
    def __init__(self):
        pyxel.init(
            c.SCREEN_WIDTH, c.SCREEN_HEIGHT, title="Cootie Catcher", display_scale=2
        )
        pyxel.playm(0, loop=True)
        pyxel.mouse(True)

        self.sim = Pandemic()
        self.stats = GameStats()
        self.heading = Heading()

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

        self.next_button = Button(
            x=c.SCREEN_WIDTH - 40,
            y=c.SCREEN_HEIGHT - 30,
            width=30,
            height=15,
            text="Next",
        )

        pyxel.run(self.update, self.draw)

    def update(self):
        for place in self.places:
            place.update(self.sim)

        self.sim.action_count = 0
        for place in self.places:
            for action in c.ACTIONS:
                self.sim.action_count += place.checkboxes[action].is_checked

        if self.next_button.is_clicked():
            total_infections = 0
            for place in self.places:
                total_infections += place.place.infected

            if total_infections > 0:
                self.sim.days_since_last_infection = 0
            else:
                self.sim.days_since_last_infection += 1

            self.sim.update()  # Update simulation only if next button is pressed

    def draw(self):
        pyxel.cls(c.BACKGROUND_COLOR)
        if self.sim.days_since_last_infection == c.WIN_THRESHOLD:
            self.win()
            return

        totals = self.sim.get_totals()
        pct_homeschooled = int((1 - totals.alive() / totals.population()) * 100)
        if pct_homeschooled >= c.LOSE_THRESHOLD:
            self.lose()
            return

        self.heading.draw()

        for place in self.places:
            place.draw()

        # Draw next button
        self.next_button.draw()

        # display stats
        self.stats.draw(
            sim=self.sim,
            days_since_last_infection=self.sim.days_since_last_infection,
            pct_homeschooled=pct_homeschooled,
        )

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
