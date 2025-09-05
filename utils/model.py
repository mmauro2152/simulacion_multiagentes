from utils.car_utils import car_space, car_spawner, car_agent
from utils.semaforo_utils import semaforo_manager, semaforo_agent
from utils.plot_utils import create_routes
from datetime import datetime
from agentpy import Model
from typing import List, Set

class car_model(Model):
    def setup(self):
        self.size = self.p["size"]
        self.lane_width = self.p["lane_width"]
        self.environment = car_space(self, (self.size, self.size))
        self.speed = 0.25

        all_routes = create_routes(self.size)
        self.routes = all_routes.routes
        self.route_colors = all_routes.colors
        self.top_routes = all_routes.top_routes
        self.right_routes = all_routes.right_routes
        self.bot_routes = all_routes.bot_routes
        self.left_routes = all_routes.left_routes
        self.mode = self.p["mode"]
        self.semaforos_manager = semaforo_manager(self, self.environment, self.create_semaforos())
        self.semaforos_manager.semaforos[0].change_phase("green")
        self.active_cars:List[Set[car_agent]] = [set(), set(), set(), set()]

        self.environment.add_agents([car_spawner(self, self.environment)])
        self.environment.add_agents([self.semaforos_manager])
        self.environment.add_agents(self.semaforos_manager.semaforos, [smf.pos for smf in self.semaforos_manager.semaforos])

    def step(self):
        if self.t % 100 == 0:
            t = datetime.now().time().strftime("%H:%M:%S")
            print(f"Current step: {self.t},  {t}")

        for ag in list(self.environment.agents):
            ag.execute()
    
    def create_semaforos(self):
        env = None if self == None else self.environment

        semaforos = [
            semaforo_agent(self, env, (7.5, 32.5), (-9.5, 32.5), 0),
            semaforo_agent(self, env, (32.5, 32.5), (33.5, 32.5), 1),
            semaforo_agent(self, env, (32.5, 7.5), (33.5, 7.5), 2),
            semaforo_agent(self, env, (7.5, 7.5), (-9.5, 7.5), 3),
        ]

        for s in semaforos:
            s.pos = (s.pos[0] + (self.size - self.lane_width * 2) / 2, 
                    s.pos[1] + (self.size - self.lane_width * 2) / 2)
            
            f = 4 if s.index < 2 else -4
            
            s.text_pos = (s.text_pos[0] + (self.size - self.lane_width * 2) / 2, 
                        s.text_pos[1] + (self.size - self.lane_width * 2) / 2)
            
            s.text_pos2 = (s.text_pos[0], 
                        s.text_pos[1] + f)
            
            s.text_pos3 = (s.text_pos[0], 
                        s.text_pos[1] + f * 2)

        return semaforos
    
    def get_data(self):
        return {
            "semaforo_data": self.semaforos_manager.get_data(),
            "q_values": self.semaforos_manager.Q
        }