import agentpy as ap
from agentpy import Space, Agent, Model
from typing import List
from plot_utils import *
from time import time
from random import randint, random
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
        self.norm_x = self.x / self.m
        self.norm_y = self.y / self.m

class car_model(Model):
    def setup(self):
        self.size = self.p["size"]
        self.environment = car_space(self, (self.size, self.size))
        self.speed = 0.25

        all_routes = create_routes()
        self.routes = all_routes.routes
        self.route_colors = all_routes.colors
        self.top_routes = all_routes.top_routes
        self.right_routes = all_routes.right_routes
        self.bot_routes = all_routes.bot_routes
        self.left_routes = all_routes.left_routes
        self.semaforos_manager = semaforo_manager(self, self.environment, create_semaforos(self))

        self.environment.add_agents([car_spawner(self, self.environment)])
        self.environment.add_agents([self.semaforos_manager])
        self.environment.add_agents(self.semaforos_manager.semaforos, [smf.pos for smf in self.semaforos_manager.semaforos])
        # car = car_agent(self, self.environment, self.bot_routes[1])
        # self.environment.add_agents([car], [car.route.starting_point])

    def step(self):
        if self.t % 100 == 0:
            print(f"Current step: {self.t}")

        for ag in list(self.environment.agents):
            ag.execute()

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
        self.semaforo:semaforo_agent = self.model.semaforos_manager.semaforos[self.route.index]
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

            self.semaforo.throughput += 1
            self.state = "finish"

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

        self.env.add_agents([car_agent(self.model, self.env, selected_route)], [selected_route.starting_point])

class semaforo_agent(Agent):
    def setup(self, env:car_space, pos:Tuple[float, float], text_pos:Tuple[float, float], index:int):
        self.color = "red"
        self.r = 1
        self.env = env
        self.pos = pos
        self.text_pos = text_pos
        self.throughput = 0
        self.queue = 0
        self.index = index

    def change_phase(self, color):
        self.color = color

    def wait_time(self):
        neighbors = list(self.env.neighbors(self, 25))
        w = self.model.t

        for n in neighbors:
            if n.type == "car_agent":
                c:car_agent = n
                if (c.semaforo_point() == c.pos and 
                    c.waiting_since != None and 
                    c.waiting_since < w):

                    w = c.waiting_since

        return self.model.t - w
    
    def execute(self):
        pass
                    
                

class semaforo_manager(Agent):

    # Q values

    Q = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]

    # Semaforos N E S W
    S = [0, 1, 2, 3]
    A = [0, 1, 2, 3]

    def setup(self, env:car_space, semaforos:List[semaforo_agent]):
        self.active = 0
        self.extend_time = 5
        self.green_time = 25
        self.yellow_time = 9
        self.red_time = 9
        self.times = [self.green_time, self.yellow_time, self.red_time]
        self.env = env
        self.semaforos = semaforos
        self.start_step = self.model.t
        self.curr_phase = 0
        self.colors = ["green", "yellow", "red"]
        self.s = 0
        self.past_s = None
        self.extension = 0

        self.semaforos[0].color = self.colors[0]

    def execute(self):
        curr_step = self.model.t

        # if curr_step - self.start_step >= self.times[self.curr_phase]:
        #     self.curr_phase = self.curr_phase + 1 if self.curr_phase + 1 < len(self.colors) else 0

        #     if self.curr_phase == 0:
        #         self.active = self.active + 1 if self.active + 1 < len(self.semaforos) else 0

        #     self.semaforos[self.active].change_phase(self.colors[self.curr_phase])

        #     self.start_step = curr_step

        curr_smf = self.semaforos[self.active]

        # if current phase ends
        if curr_step - (self.start_step + self.extension) >= self.times[self.curr_phase]:
            if self.curr_phase == 0:
                a = self.get_a()
                s_prime = self.S[a]

                self.q_learn(s_prime, a)

                # extender fase
                if s_prime == self.s:
                    self.extension += 5
                    self.s = s_prime

                # cambiar a otro semaforo
                else:
                    self.s = s_prime
                    self.extension = 0
                    self.curr_phase += 1
                    curr_smf.change_phase(self.colors[self.curr_phase])
                    self.start_step = curr_step

            elif self.curr_phase == 1:
                self.curr_phase += 1
                curr_smf.change_phase(self.colors[self.curr_phase])
                self.start_step = curr_step

            elif self.curr_phase == 2:
                self.active = self.s
                self.curr_phase = 0
                self.semaforos[self.active].change_phase(self.colors[self.curr_phase])

    def get_a(self):
        epsilon = 0.1
        r = random()

        if (r <= epsilon):
            return randint(0, len(self.A) - 1)
        
        else:
            max_q = None
            a = 0
            for act in self.A:
                if max_q == None or max_q < self.Q[self.s][act]: 
                    max_q = self.Q[self.s][act]
                    a = act

            return a

    def q_learn(self, s_prime:int, a:int):
        alpha = 0.2
        gamma = 0.98

        new_q_val = self.Q[self.s][a] + alpha * (self.reward(s_prime) + gamma * self.max_a(s_prime))
        self.Q[self.s][a] = new_q_val

    def max_a(self, s_prime):
        max_q = None
        for a in self.A:
            if max_q == None or max_q < self.Q[s_prime][a]: 
                max_q = self.Q[s_prime][a]

        return max_q
    
    def reward(self, s_prime):
        queues = 0
        waits = 0

        for smf in self.semaforos:
            queues += smf.queue
            waits += smf.wait_time()

        waits /= len(self.semaforos)

        change = int(self.s != s_prime)

        queue_w = 1.0
        waits_w = 0.5
        change_w = 0.1

        return -(queue_w * queues + waits_w * waits) + change_w * change
    
def create_semaforos(model:car_model):
    env = None if model == None else model.environment

    semaforos:List[semaforo_agent] = [
        semaforo_agent(model, env, (7.5, 32.5), (-9.5, 32.5), 0),
        semaforo_agent(model, env, (32.5, 32.5), (33.5, 32.5), 1),
        semaforo_agent(model, env, (32.5, 7.5), (33.5, 7.5), 2),
        semaforo_agent(model, env, (7.5, 7.5), (-9.5, 7.5), 3),
    ]

    for s in semaforos:
        s.pos = (s.pos[0] + (size - lane_width * 2) / 2, 
                 s.pos[1] + (size - lane_width * 2) / 2)
        
        f = 4 if s.index < 2 else -4
        
        s.text_pos = (s.text_pos[0] + (size - lane_width * 2) / 2, 
                      s.text_pos[1] + (size - lane_width * 2) / 2)
        
        s.text_pos2 = (s.text_pos[0], 
                       s.text_pos[1] + f)
        
        s.text_pos3 = (s.text_pos[0], 
                       s.text_pos[1] + f * 2)

    return semaforos



