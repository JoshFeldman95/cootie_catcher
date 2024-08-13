from components import Clickable, Button, NextDayButton, ActionCheckbox
import consts as c
import pyxel
import networkx as nx


def map_scaler(x, y, x_min, x_max, y_min, y_max):
    # normalize x and y values to 0-1
    x = (x - x_min) / (x_max - x_min)
    y = (y - y_min) / (y_max - y_min)

    # scale to screen size with border
    x = x * (c.SCREEN_WIDTH - c.BORDER * 8) + c.BORDER * 4
    y = y * (c.SCREEN_HEIGHT - c.BORDER * 8) + c.BORDER * 4
    return x, y


class MapPlaceMarker(Clickable):
    def __init__(self, x, y, place_name):
        self.x = x - 5
        self.y = y - 5
        self.width = 10
        self.height = 10
        self.place_name = place_name

    def draw(self, game_state, prop_infected):
        if game_state.map_selected_place == self.place_name:
            color = c.DARK
        elif prop_infected == 0:
            color = c.GREEN
        elif prop_infected < 0.1:
            color = c.ORANGE
        else:
            color = c.ALERT_COLOR

        if self.is_hovered():
            pyxel.circ(self.x + 5, self.y + 5, self.width, c.HIGHLIGHT_COLOR_DARK)
        else:
            pyxel.circ(self.x + 5, self.y + 5, self.width / 2, color)

        if self.is_clicked():
            if game_state.map_selected_place == self.place_name:
                game_state.map_selected_place = None
            else:
                game_state.map_selected_place = self.place_name


class MapEdge:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def draw(self):
        pyxel.line(self.x1, self.y1, self.x2, self.y2, c.DARK)


class MapButton(Button):
    def __init__(self):
        map_button_text = "Show Map"
        self.map_button = Button(
            x=NextDayButton.x
            - len(map_button_text) * c.CHARACTER_WIDTH
            - Button.text_padding * 2
            - 5,
            y=c.BOTTOM_MENU_HEIGHT,
            text=map_button_text,
        )

    def draw(self, game_state):
        if game_state.map_visible:
            self.map_button.text = "Hide Map"
        else:
            self.map_button.text = "Show Map"
        self.map_button.draw()

    def update(self, game_state):
        if self.map_button.is_clicked():
            game_state.map_visible = not game_state.map_visible


class SelectionBox:
    def __init__(self):
        self.action_checkboxes = []

    def update(self, sim):
        for checkbox in self.action_checkboxes:
            checkbox.update(sim)

    def draw(self, game_state, sim):
        if game_state.map_selected_place:
            pyxel.rect(x=c.BORDER, y=c.BORDER, w=110, h=75, col=c.LIGHT)
            pyxel.rectb(x=c.BORDER, y=c.BORDER, w=110, h=75, col=c.DARK)
            selected_place = sim.cities[game_state.map_selected_place]
            place_stats = [
                f"{selected_place.place_name}",
                f"Caught Cooties: {selected_place.detected}",
                f"Treated: {selected_place.treated}",
                f"Homeschooled: {selected_place.dead}",
                f"Anger: {selected_place.anger}/5",
            ]
            for idx, stat in enumerate(place_stats):
                pyxel.text(
                    x=c.BORDER + 5,
                    y=c.BORDER + c.CHARACTER_HEIGHT * (1 + idx),
                    s=stat,
                    col=c.DARK,
                )
            # draw actions
            self.action_checkboxes = []
            for idx, action in enumerate(c.ACTIONS):
                pyxel.text(
                    x=c.BORDER + 5,
                    y=c.BORDER + c.CHARACTER_HEIGHT * (len(place_stats) + 3 + idx),
                    s=f"{c.ACTIONS[action]}: ",
                    col=c.DARK,
                )
                checkbox = ActionCheckbox(
                    x=c.BORDER + 5 + len(c.ACTIONS[action]) * c.CHARACTER_WIDTH + 5,
                    y=c.BORDER + c.CHARACTER_HEIGHT * (len(place_stats) + 3 + idx),
                    size=5,
                    place_name=selected_place.place_name,
                    action_name=action,
                )
                self.action_checkboxes.append(checkbox)
                checkbox.draw(sim)


class Map:
    def __init__(self):
        self.visible = True
        self.selection_box = SelectionBox()

    def update(self, sim):
        if self.visible:
            self.selection_box.update(sim)

    def draw(self, game_state, sim):

        # draw background
        pyxel.rect(0, 0, c.SCREEN_WIDTH, c.SCREEN_HEIGHT, c.LIGHT)

        # draw network

        # Create a graph from the network
        graph = nx.Graph(sim.network)

        # Specify the positions of the nodes
        pos = nx.spring_layout(
            graph,
            pos={i: (i // 5, i % 5) for i in range(c.PLACE_COUNT)},
            seed=42,
            iterations=1000,
        )

        # x and y min and max values
        xs = [x for x, _ in pos.values()]
        ys = [y for _, y in pos.values()]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)

        for edge in graph.edges:
            x1, y1 = pos[edge[0]]
            x2, y2 = pos[edge[1]]
            x1, y1 = map_scaler(x1, y1, x_min, x_max, y_min, y_max)
            x2, y2 = map_scaler(x2, y2, x_min, x_max, y_min, y_max)

            MapEdge(x1, y1, x2, y2).draw()

        for place in sim.cities.values():
            x, y = pos[place.node]

            # Normalize x and y values
            x, y = map_scaler(x, y, x_min, x_max, y_min, y_max)
            MapPlaceMarker(x, y, place.place_name).draw(
                game_state=game_state, prop_infected=place.detected / place.population()
            )

        self.selection_box.draw(game_state, sim)
