from components import Hoverable, Button, NextDayButton
import consts as c
import pyxel
import networkx as nx


def map_scaler(x, y, x_min, x_max, y_min, y_max):
    x = (x - x_min) / (x_max - x_min) * (c.SCREEN_WIDTH - c.BORDER - 10) + c.BORDER + 10
    y = (
        (y - y_min) / (y_max - y_min) * (c.SCREEN_HEIGHT - c.BORDER - 10)
        + c.BORDER
        + 10
    )
    return x, y


class MapPlaceMarker(Hoverable):
    def __init__(self, x, y, place_name):
        self.x = x - 5
        self.y = y - 5
        self.width = 10
        self.height = 10
        self.place_name = place_name

    def draw(self, prop_infected):
        if prop_infected == 0:
            color = c.GREEN
        elif prop_infected < 0.1:
            color = c.ORANGE
        else:
            color = c.ALERT_COLOR

        if self.is_hovered():
            pyxel.rect(self.x, self.y, self.width, self.height, c.HIGHLIGHT_COLOR_DARK)
            pyxel.text(c.BORDER, c.BORDER, self.place_name, c.DARK)
        else:
            pyxel.rect(self.x, self.y, self.width, self.height, color)


class MapEdge(Hoverable):
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


class Map:
    def __init__(self):
        self.visible = True

    def draw(self, sim):

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
                place.detected / place.population()
            )
