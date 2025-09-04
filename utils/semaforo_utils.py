
from utils.car_utils import car_agent, car_space
from agentpy import Agent
from typing import List
from utils.plot_utils import *
from random import randint, random
from typing import Set

class semaforo_agent(Agent):
    def setup(self, env:car_space, pos:Tuple[float, float], text_pos:Tuple[float, float], index:int):
        self.color = "red"
        self.r = 1
        self.env = env
        self.pos = pos
        self.text_pos = text_pos
        self.throughput = [0]
        self.avg_waiting_times = []
        self.max_waiting_times = []
        self.queues = []
        self.queue = 0
        self.index = index

    def change_phase(self, color):
        self.color = color
        if self.color == "green":
            self.throughput.append(0)

    def wait_time(self):
        neighbors = list(self.env.neighbors(self, 50))
        w = self.model.t

        for n in neighbors:
            if n.type == "car_agent":
                c:car_agent = n
                if (c.semaforo.index == self.index and
                    c.semaforo_point() == c.pos and 
                    c.waiting_since != None and 
                    c.waiting_since < w):

                    w = c.waiting_since

                elif (c.semaforo.index == self.index and
                    c.vector_to_point(c.semaforo_point()).m < c.speed and 
                    c.waiting_since != None and 
                    c.waiting_since < w):

                    w = c.waiting_since
    
        return self.model.t - w
    
    def execute(self):
        active_cars:Set[car_agent] = self.model.active_cars[self.index]

        min_ws = self.model.t

        self.avg_waiting_times.append(0)

        for car in active_cars:
            if car.waiting_since != None:
                self.avg_waiting_times[-1] += car.waiting_since

                if car.waiting_since < min_ws:
                    min_ws = car.waiting_since

        self.max_waiting_times.append(self.model.t - min_ws)
        self.avg_waiting_times[-1] /= len(active_cars)
        self.queues.append(self.queue)                        

    def get_data(self):
        return {
            "avg_wait_times": self.avg_waiting_times,
            "max_wait_times": self.max_waiting_times,
            "queues": self.queues,
            "total_tp": sum(self.throughput)
        }

class semaforo_manager(Agent):

    # Q values

    follow_sequence = True
    Q = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ] if not follow_sequence else [
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0]
    ]

    # Semaforos N E S W
    S = [0, 1, 2, 3]

    A = [0, 1, 2, 3] if not follow_sequence else [0, 1]
    

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
        self.epsilon = 0.5

        self.semaforos[0].color = self.colors[0]

    def use_q_learning(self):
        curr_step = self.model.t
        curr_smf = self.semaforos[self.active]

        # if current phase ends
        if curr_step - (self.start_step + self.extension) >= self.times[self.curr_phase]:
            if self.curr_phase == 0:
                a = self.get_a()

                if self.follow_sequence:
                    if a == 0:
                        s_prime = self.s
                    elif a == 1:
                        s_prime = (self.s + 1) % len(self.S)

                else:
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

    def use_fixed(self):
        curr_step = self.model.t

        if curr_step - self.start_step >= self.times[self.curr_phase]:
            self.curr_phase = self.curr_phase + 1 if self.curr_phase + 1 < len(self.colors) else 0

            if self.curr_phase == 0:
                self.active = self.active + 1 if self.active + 1 < len(self.semaforos) else 0

            self.semaforos[self.active].change_phase(self.colors[self.curr_phase])

            self.start_step = curr_step

    def execute(self):
        if self.model.t % 100 == 0 and self.epsilon > 0.1:
            self.epsilon -= 0.04

        if self.model.mode == "fixed":
            self.use_fixed()
        else:
            self.use_q_learning()

    def get_a(self):
        r = random()

        if (r <= self.epsilon):
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
        # queues = 0
        # waits = 0

        # for smf in self.semaforos:
        #     queues += smf.queue
        #     waits += smf.wait_time()

        # q = self.semaforos[s_prime].queue
        # w = self.semaforos[s_prime].wait_time()

        # waits /= len(self.semaforos)

        # change = int(self.s != s_prime)

        # queue_w = 1.0
        # waits_w = 0.8
        # change_w = 0.1

        # return -(queue_w * q + waits_w * w)# + change_w * change

        # Observables from simulator
        Q_t = sum([smf.queue for smf in self.semaforos])                  # total vehicles waiting
        H_t = max([smf.wait_time() for smf in self.semaforos])     # use max across approaches
        T_t = self.semaforos[self.s].throughput[-1]                # vehicles discharged this step
        phase_changed = int(s_prime != self.s)

        # Normalization constants (tune to your scenario)
        Q_max, H_max, T_max = 30.0, 100.0, 30.0

        Q_n = Q_t / Q_max
        H_n = H_t / H_max
        T_n = T_t / T_max

        # Weights (baseline)
        w_q, w_h, w_tp, w_c, w_s = 1.0, 0.7, 1.2, 0.2, 2.0
        Wcap_n = 60.0 / H_max   # normalized starvation cap

        # Reward
        r = -(w_q * Q_n + w_h * H_n) + w_tp * T_n \
            - w_c * phase_changed \
            - w_s * max(0.0, H_n - Wcap_n)

        if self.epsilon > 0.1:
            # Clip
            r = max(-2.0, min(2.0, r))

        return r

    def get_data(self):
        return [smf.get_data() for smf in self.semaforos]