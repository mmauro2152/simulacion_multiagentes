from typing import List, Tuple
import matplotlib.pyplot as plt

lane_width = 20
size = 500

class route:
    x:List[float]
    y:List[float]
    points:List[Tuple[float,float]]
    starting_point:Tuple[float, float]
    index:int = 0
    cross_val:float = (size - lane_width) / 2
    cross_ax:int = 0

    def __init__(self, x:List[float], y:List[float]):
        self.x = x
        self.y = y
        self.points = []
        self.starting_point = ()
        self.save_as_points()

    def save_as_points(self):
        self.points = []
        for i in range(len(self.x)):
            self.points.append((self.x[i], self.y[i]))

        self.starting_point = self.points[0]

class routes:

    def __init__(self, all_routes:List[List[route]]):
        self.routes:List[List[route]] = all_routes
        self.colors:List[str] = ["blue", "red", "green", "purple"]
        self.top_routes:List[route] = all_routes[0]
        self.right_routes:List[route] = all_routes[1]
        self.bot_routes:List[route] = all_routes[2]
        self.left_routes:List[route] = all_routes[3]

def plot_map(ax):
    # limite de calles
    color = "black"
    left_top_corner_x = [0, 10 + (size - lane_width * 2) / 2, 10 + (size - lane_width * 2) / 2]
    left_top_corner_y = [30 + (size - lane_width * 2) / 2, 30 + (size - lane_width * 2) / 2, size]

    right_top_corner_x = [30 + (size - lane_width * 2) / 2, 30 + (size - lane_width * 2) / 2, size]
    right_top_corner_y = [size, 30 + (size - lane_width * 2) / 2, 30 + (size - lane_width * 2) / 2]

    left_bot_corner_x = [0, 10 + (size - lane_width * 2) / 2, 10 + (size - lane_width * 2) / 2]
    left_bot_corner_y = [10 + (size - lane_width * 2) / 2, 10 + (size - lane_width * 2) / 2, 0]

    right_bot_corner_x = [30 + (size - lane_width * 2) / 2, 30 + (size - lane_width * 2) / 2, 35 + (size - lane_width * 2) / 2, 40 + (size - lane_width * 2) / 2, size]
    right_bot_corner_y = [                               0, 10 + (size - lane_width * 2) / 2, 10 + (size - lane_width * 2) / 2, 15 + (size - lane_width * 2) / 2, 15 + (size - lane_width * 2) / 2]


    ax.plot(left_top_corner_x, left_top_corner_y, color)
    ax.plot(right_top_corner_x, right_top_corner_y, color)
    ax.plot(left_bot_corner_x, left_bot_corner_y, color)
    ax.plot(right_bot_corner_x, right_bot_corner_y, color)

    # lineas amarillas
    color = "orange"
    top_x = [20 + (size - lane_width * 2) / 2, 20 + (size - lane_width * 2) / 2]
    top_y = [size, 30 + (size - lane_width * 2) / 2]

    left_x = [0, 10 + (size - lane_width * 2) / 2]
    left_y = [20 + (size - lane_width * 2) / 2, 20 + (size - lane_width * 2) / 2]

    right_x = [30 + (size - lane_width * 2) / 2, size]
    right_y = [20 + (size - lane_width * 2) / 2, 20 + (size - lane_width * 2) / 2]

    bot_x = [20 + (size - lane_width * 2) / 2, 20 + (size - lane_width * 2) / 2]
    bot_y = [10 + (size - lane_width * 2) / 2, 0]

    ax.plot(top_x, top_y, color)
    ax.plot(left_x, left_y, color)
    ax.plot(right_x, right_y, color)
    ax.plot(bot_x, bot_y, color)

    # carriles
    color = "black"
    v_lane_left_x = [15 + (size - lane_width * 2) / 2, 15 + (size - lane_width * 2) / 2]
    v_lane_right_x = [25 + (size - lane_width * 2) / 2, 25 + (size - lane_width * 2) / 2]
    top_v_lane_y = [size, 30 + (size - lane_width * 2) / 2]
    bot_v_lane_y = [10 + (size - lane_width * 2) / 2, 0]

    left_h_lane_x = [0, 10 + (size - lane_width * 2) / 2]
    right_h_lane_x = [30 + (size - lane_width * 2) / 2, size]
    top_right_h_lane_x = [30 + (size - lane_width * 2) / 2, 40 + (size - lane_width * 2) / 2]
    h_lane_top_y = [25 + (size - lane_width * 2) / 2, 25 + (size - lane_width * 2) / 2]
    h_lane_bot_y = [15 + (size - lane_width * 2) / 2, 15 + (size - lane_width * 2) / 2]

    ax.plot(v_lane_left_x, top_v_lane_y, color, linestyle="--")
    ax.plot(v_lane_right_x, top_v_lane_y, color, linestyle="--")
    ax.plot(v_lane_left_x, bot_v_lane_y, color, linestyle="--")
    ax.plot(v_lane_right_x, bot_v_lane_y, color, linestyle="--")
    ax.plot(left_h_lane_x, h_lane_top_y, color, linestyle="--")
    ax.plot(left_h_lane_x, h_lane_bot_y, color, linestyle="--")
    ax.plot(right_h_lane_x, h_lane_top_y, color, linestyle="--")
    ax.plot(top_right_h_lane_x, h_lane_bot_y, color, linestyle="--")

def create_routes():
    bot_routes:List[route] = [
        route([27.5, 27.5, 40], [0, 17.5, 17.5]),
        route([27.5, 27.5], [0, 40]),
        route([22.5, 22.5, 0], [0, 27.5, 27.5]),
        route([22.5, 22.5, 0], [0, 22.5, 22.5]),
        route([22.5, 22.5], [0, 40])
    ]

    left_routes:List[route] = [
        route([0, 12.5, 12.5], [12.5, 12.5, 0]),
        route([0, 17.5, 17.5], [12.5, 12.5, 0]),
        route([0, 40], [17.5, 17.5]),
        route([0, 27.5, 27.5], [17.5, 17.5, 40]),
        route([0, 22.5, 22.5], [17.5, 17.5, 40])
    ]

    top_routes:List[route] = [
        route([12.5, 12.5], [40, 0]),
        route([12.5, 12.5, 0], [40, 27.5, 27.5]),
        route([12.5, 12.5, 0], [40, 22.5, 22.5]),
        route([17.5, 17.5, 40], [40, 17.5, 17.5]),
        route([17.5, 17.5], [40, 0])
    ]

    right_routes:List[route] = [
        route([40, 27.5, 27.5], [27.5, 27.5, 40]),
        route([40, 22.5, 22.5], [27.5, 27.5, 40]),
        route([40, 0], [27.5, 27.5]),
        route([40, 0], [22.5, 22.5]),
        route([40, 17.5, 17.5], [22.5, 22.5, 0]),
        route([40, 12.5, 12.5], [22.5, 22.5, 0])
    ]

    all_routes = [top_routes, right_routes, bot_routes, left_routes]

    index = 0
    for rs in all_routes:
        for r in rs:
            factor = 1 if index <= 1 else -1
            r.index = index
            r.cross_ax = int(not bool(index % 2))
            r.cross_val = (size + (lane_width * factor)) / 2

            for i in range(len(r.x)):
                if r.x[i] == 40:
                    r.x[i] = size

                elif r.x[i] != 0:
                    r.x[i] += (size - lane_width * 2) / 2

            for i in range(len(r.y)):
                if r.y[i] == 40:
                    r.y[i] = size

                elif r.y[i] != 0:
                    r.y[i] += (size - lane_width * 2) / 2

            r.save_as_points()

        index += 1

    return routes(all_routes)

def plot_semaforos(ax, semaforos):
    for s in semaforos:
        circle = plt.Circle(s.pos, s.r, color=s.color)
        ax.add_patch(circle)
        ax.text(s.text_pos[0], s.text_pos[1], f"queue: {s.queue}", fontsize=24, color="black")
        ax.text(s.text_pos2[0], s.text_pos2[1], f"tp: {s.throughput}", fontsize=24, color="black")
        ax.text(s.text_pos3[0], s.text_pos3[1], f"w: {s.wait_time()}", fontsize=24, color="black")