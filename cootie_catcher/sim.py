import consts as c
from dataclasses import dataclass
import random
import networkx as nx


def binomial(n, p):
    """Generate a sample from a binomial distribution."""
    successes = 0
    for _ in range(n):
        if random.random() < p:
            successes += 1
    return successes


@dataclass
class PlaceData:
    # metadata
    node: int
    place_name: str

    # epidemic state
    susceptible: int
    exposed: int
    infected: int
    detected: int
    treated: int
    dead: int

    # control measures
    control_measures: dict
    anger: int = 0
    in_backlash: bool = False

    def population(self):
        return (
            self.susceptible
            + self.exposed
            + self.infected
            + self.detected
            + self.treated
            + self.dead
        )

    def alive(self):
        return (
            self.susceptible
            + self.exposed
            + self.infected
            + self.detected
            + self.treated
        )


class Pandemic:
    def __init__(self):
        self.day = 0
        self.action_budget = c.ACTION_BUDGET_BEGINNING
        self.days_since_last_infection = 0
        self.network = nx.barabasi_albert_graph(c.PLACE_COUNT, 2)
        self.cities = {}
        for place, place_name in zip(self.network.nodes, c.PLACE_NAMES):
            # population = world population * node degree / (edge count * 2)
            place_pop = (
                c.TOTAL_POPULATION
                * self.network.degree[place]
                / (self.network.number_of_edges() * 2)
            )

            # Create a place data object for each place
            self.cities[place_name] = PlaceData(
                node=place,
                place_name=place_name,
                susceptible=int(place_pop),
                exposed=0,
                infected=0,
                detected=0,
                treated=0,
                dead=0,
                control_measures={
                    "restrict_travel": False,
                    "mass_testing": False,
                    "contact_tracing": False,
                    "lockdown": False,
                },
            )

        # create patient(s) zero
        random_place = random.choice(list(self.cities.values()))
        random_place.infected = 5

    def update(self):
        self.day += 1

        # update days since last infection
        total_infections = 0
        for place_data in self.cities.values():
            total_infections += (
                place_data.infected + place_data.exposed + place_data.detected
            )

        if total_infections > 0:
            self.days_since_last_infection = 0
        else:
            self.days_since_last_infection += 1

        # update action budget
        if self.day < c.MIDDLE_CUTOFF:
            self.action_budget = c.ACTION_BUDGET_BEGINNING
        elif self.day < c.END_CUTOFF:
            self.action_budget = c.ACTION_BUDGET_MIDDLE
        else:
            self.action_budget = c.ACTION_BUDGET_END

        for place in self.cities.values():
            self.update_place(place)

    def update_place(self, place):
        if place.alive() == 0:
            return

        # update backlash
        if place.control_measures["lockdown"]:
            place.anger += 1
        elif place.anger > 0:
            place.anger -= 1

        if place.anger == 0 and place.in_backlash:
            place.in_backlash = False

        if place.anger == c.ANGER_THRESHOLD:
            for measure in place.control_measures:
                place.control_measures[measure] = False
                place.in_backlash = True

        # calculate deltas

        # new disease

        # get infections in neighbours
        neighbour_contagious = 0
        for neighbour in self.network.neighbors(place.node):
            neighbour = self.cities[c.PLACE_NAMES[neighbour]]
            neighbour_contagious += neighbour.infected + neighbour.exposed

        # calculate infected travellers as a proportion of infected in neighbours
        travel_rate = (
            c.TRAVEL_RATE
            if not place.control_measures["restrict_travel"]
            and not place.control_measures["lockdown"]
            else 0
        )
        infected_travellers = binomial(neighbour_contagious, travel_rate)

        # calculate number of people spreading
        total_infections = place.infected + infected_travellers
        total_spreading = total_infections + place.exposed
        if place.control_measures["contact_tracing"]:
            total_spreading -= min(c.CONTACT_TRACING_CAPACITY, total_spreading)

        infection_risk_per_contact = (
            c.INFECTION_RATE * total_spreading / (place.alive() + infected_travellers)
        )
        contacts = c.CONTACTS if not place.control_measures["lockdown"] else 0
        infection_risk = 1 - (1 - infection_risk_per_contact) ** (contacts)

        new_exposed = binomial(place.susceptible, infection_risk)

        # symptomatic deltas
        new_infected = binomial(place.exposed, c.INCUBATION_RATE)
        detection_rate = (
            c.DETECTION_RATE
            if not place.control_measures["mass_testing"]
            else c.MASS_TESTING_DETECTION_RATE
        )
        new_detected = binomial(place.infected, detection_rate)
        new_dead_from_infected = binomial(
            place.infected - new_detected, c.MORTALITY_RATE
        )
        new_susceptible_from_infected = binomial(
            place.infected - new_detected - new_dead_from_infected, c.RECOVERY_RATE
        )

        # detected deltas
        new_treated = int(
            min(
                binomial(place.detected, c.TREATMENT_RATE),
                place.population() * c.TREATMENT_CAPACITY,
            )
        )
        new_dead_from_detected = binomial(
            place.detected - new_treated, c.MORTALITY_RATE
        )
        new_susceptible_from_detected = binomial(
            place.detected - new_treated - new_dead_from_detected,
            c.RECOVERY_RATE,
        )

        # treated deltas
        new_dead_from_treated = binomial(place.treated, c.MORTALITY_RATE * 0.1)
        new_susceptible_from_treated = binomial(
            place.treated - new_dead_from_treated, c.RECOVERY_RATE * 5
        )

        # totals
        new_dead_total = (
            new_dead_from_infected + new_dead_from_detected + new_dead_from_treated
        )
        new_susceptible_total = (
            new_susceptible_from_infected
            + new_susceptible_from_detected
            + new_susceptible_from_treated
        )

        # update place data
        place.susceptible = place.susceptible - new_exposed + new_susceptible_total
        place.exposed = place.exposed + new_exposed - new_infected
        place.infected = (
            place.infected
            + new_infected
            - new_detected
            - new_dead_from_infected
            - new_susceptible_from_infected
        )
        place.detected = (
            place.detected
            + new_detected
            - new_treated
            - new_dead_from_detected
            - new_susceptible_from_detected
        )
        place.treated = (
            place.treated
            + new_treated
            - new_dead_from_treated
            - new_susceptible_from_treated
        )
        place.dead = place.dead + new_dead_total

    def get_totals(self):
        total_susceptible = 0
        total_exposed = 0
        total_infected = 0
        total_detected = 0
        total_treated = 0
        total_dead = 0

        for place in self.cities.values():
            total_susceptible += place.susceptible
            total_exposed += place.exposed
            total_infected += place.infected
            total_detected += place.detected
            total_treated += place.treated
            total_dead += place.dead

        return PlaceData(
            node=-1,
            place_name="Total",
            susceptible=total_susceptible,
            exposed=total_exposed,
            infected=total_infected,
            detected=total_detected,
            treated=total_treated,
            dead=total_dead,
            control_measures=None,
        )

    def __str__(self):
        totals = self.get_totals()
        return (
            f"Total susceptible: {totals.susceptible}|"
            + f"Total exposed: {totals.exposed}|"
            + f"Total infected: {totals.infected}|"
            + f"Total detected: {totals.detected}|"
            + f"Total treated: {totals.treated}|"
            + f"Total dead: {totals.dead}|"
        )

    def randomize_actions(self, action_name, n):
        # get cities that are not in backlash
        non_backlash_cities = [
            place for place in self.cities.values() if not place.in_backlash
        ]

        # Randomly select n places to apply the action to
        places = random.sample(non_backlash_cities, n)

        # deselect all actions for the selected action type
        for place in self.cities.values():
            place.control_measures[action_name] = False

        # Apply the action to the selected places
        for place in places:
            place.control_measures[action_name] = True  # Apply the action

    @property
    def action_count(self):
        action_count = 0
        for place in self.cities.values():
            action_count += sum(place.control_measures.values())
        return action_count

    @property
    def pct_dead(self):
        totals = self.get_totals()
        return int((1 - totals.alive() / totals.population()) * 100)


if __name__ == "__main__":

    p = Pandemic()

    place_populations = [place.population() for place in p.cities.values()]

    day = 0
    while p.get_totals().susceptible > 0 and day < 1000:
        p.update()
        day += 1
