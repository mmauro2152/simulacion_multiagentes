from agentpy import Space, Agent, Model
from typing import List
from utils.plot_utils import *
from random import randint
from math import sqrt 

car_colors = [
    "#FF0000",  # Ferrari Red
    "#C00000",  # Dark Red
    "#800000",  # Maroon
    "#B22222",  # Firebrick
    "#8B0000",  # Deep Red
    "#FF2400",  # Scarlet
    "#FF4C00",  # Vermilion
    "#FF4500",  # Orange Red
    "#FF8C00",  # Dark Orange
    "#FFA500",  # Orange
    "#FFD700",  # Gold
    "#DAA520",  # Goldenrod
    "#B8860B",  # Dark Goldenrod
    "#FFFF00",  # Yellow
    "#EEE600",  # Racing Yellow
    "#9ACD32",  # Yellow Green
    "#ADFF2F",  # Green Yellow
    "#006400",  # Dark Green
    "#228B22",  # Forest Green
    "#008000",  # Green
    "#2E8B57",  # Sea Green
    "#3CB371",  # Medium Sea Green
    "#00FF7F",  # Spring Green
    "#00FA9A",  # Medium Spring Green
    "#40E0D0",  # Turquoise
    "#008080",  # Teal
    "#20B2AA",  # Light Sea Green
    "#00CED1",  # Dark Turquoise
    "#4682B4",  # Steel Blue
    "#1E90FF",  # Dodger Blue
    "#0000FF",  # Blue
    "#00008B",  # Dark Blue
    "#191970",  # Midnight Blue
    "#4169E1",  # Royal Blue
    "#6495ED",  # Cornflower Blue
    "#5F9EA0",  # Cadet Blue
    "#7B68EE",  # Medium Slate Blue
    "#6A5ACD",  # Slate Blue
    "#8A2BE2",  # Blue Violet
    "#4B0082",  # Indigo
    "#800080",  # Purple
    "#9932CC",  # Dark Orchid
    "#C71585",  # Medium Violet Red
    "#FF00FF",  # Magenta
    "#FF69B4",  # Hot Pink
    "#FFC0CB",  # Pink
    "#D2691E",  # Chocolate
    "#A0522D",  # Sienna
    "#8B4513",  # Saddle Brown
    "#654321",  # Dark Brown
]

class vector:
    def __init__(self, x:float, y:float):
        self.x = x
        self.y = y
        self.m = sqrt(x ** 2 + y ** 2)

        if self.m != 0:
            self.norm_x = self.x / self.m
            self.norm_y = self.y / self.m

class car_space(Space):
    def setup(self):
        pass

class car_agent(Agent):

    def setup(self, env:car_space, route:route):
        self.env = env
        self.route = route
        self.speed = 3
        self.next_point = 1
        self.pos = self.route.starting_point
        self.color = car_colors[randint(0, len(car_colors) - 1)]
        self.semaforo = self.model.semaforos_manager.semaforos[self.route.index]
        self.state = "driving"
        self.waiting_since = None
        self.total_wait_time = None

    def vector_to_point(self, point):
        return vector(point[0] - self.pos[0], point[1] - self.pos[1])

    def is_path_free(self) -> bool:
        cars:List[car_agent] = list(filter(lambda n: n.type == "car_agent", self.env.neighbors(self, self.speed + 0.5)))
        
        for car in cars:
            if car.pos[0] == self.pos[0] and car.pos[1] == self.pos[1]:
                return False
            
            v_car = self.vector_to_point(car.pos)
            v_route = self.vector_to_point(self.route.points[self.next_point])

            if v_car.norm_x == v_route.norm_x and v_car.norm_y == v_route.norm_y:
                if self.state == "driving":
                    self.state = "waiting"
                    self.semaforo.queue += 1
                    self.waiting_since = self.model.t
                return False
            
        return True

    def follow_route(self):
        v = self.vector_to_point(self.route.points[self.next_point])

        if v.m <= self.speed:
            self.pos = self.route.points[self.next_point]
            self.next_point += 1

        else:   
            self.pos = (self.pos[0] + v.norm_x * self.speed, self.pos[1] + v.norm_y * self.speed)

        self.env.move_to(self, self.pos)

    def past_semaforo(self):
        if self.route.index <= 1:
            return self.pos[self.route.cross_ax] < self.route.cross_val
        else:
            return self.pos[self.route.cross_ax] > self.route.cross_val

    def semaforo_point(self):
        smf_point = [0, 0]
        smf_point[self.route.cross_ax] = self.route.cross_val
        smf_point[int(not bool(self.route.cross_ax))] = self.pos[int(not bool(self.route.cross_ax))]

        return smf_point

    def stop_at_semaforo(self):
        smf_point = self.semaforo_point()

        if self.pos[0] == smf_point[0] and self.pos[1] == smf_point[1]:
            if self.state == "driving":
                self.state = "waiting"
                self.semaforo.queue += 1
                self.waiting_since = self.model.t

            return

        v = self.vector_to_point(smf_point)

        if v.m <= self.speed:
            self.pos = smf_point

        else:   
            self.pos = (self.pos[0] + v.norm_x * self.speed, self.pos[1] + v.norm_y * self.speed)
            self.env.move_to(self, self.pos)    

    def execute(self):
        if self.next_point >= len(self.route.points):
            self.env.remove_agents(self)
            return

        elif not self.is_path_free():
            return 
        
        elif self.semaforo.color == "green" or self.semaforo.color == "yellow" or self.past_semaforo():
            self.follow_route()

        elif self.semaforo.color == "red":
            self.stop_at_semaforo()

        if self.past_semaforo() and (self.state == "waiting" or self.state == "driving"):
            if self.state == "waiting":
                self.semaforo.queue -= 1
                self.total_wait_time = self.model.t - self.waiting_since

            self.semaforo.throughput[-1] += 1
            self.state = "finish"

            self.model.active_cars[self.semaforo.index].remove(self)

class car_spawner(Agent):
    def setup(self, env:car_space):
        self.top_delay = 5
        self.rigth_delay = 6
        self.bot_delay = 4
        self.left_delay = 5
        self.delays = [self.top_delay, self.rigth_delay, self.bot_delay, self.left_delay]
        self.env = env

        self.steps = self.model.t
        self.last_spawn = [-self.delays[i] for i in range(4)] 
        self.spawn_count = [0 for i in range(4)]
        self.spawn_limit = 100

    def execute(self):
        self.steps = self.model.t
        for i in range(len(self.delays)):
            if self.steps - self.last_spawn[i] >= self.delays[i] :#and self.spawn_count[i] < self.spawn_limit:
                self.last_spawn[i] = self.steps
                self.spawn_car(i)
                self.spawn_count[i] += 1

    def spawn_car(self, index):
        routes:List[route] = self.model.routes[index]
        selected_route = routes[randint(0, len(routes) - 1)]
        
        car = car_agent(self.model, self.env, selected_route)

        self.model.active_cars[index].add(car)

        self.env.add_agents([car], [selected_route.starting_point])


