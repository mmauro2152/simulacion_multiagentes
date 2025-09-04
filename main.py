from matplotlib import pyplot as plt
from typing import List, Tuple
from agents_models.models import car_agent, car_space, car_model, semaforo_agent
import agentpy as ap
import asyncio
from plot_utils import *

def plot_animation(model:car_model, ax):
    plot_map(ax)
    plot_semaforos(ax, model.semaforos_manager.semaforos)
    for r in model.routes[model.semaforos_manager.active]:
        ax.plot(r.x, r.y, model.route_colors[model.semaforos_manager.active], linestyle="--", linewidth=0.4)

    ax.set_title(f"time: {model.t}", fontsize=40)

    for ag in list(model.environment.agents):
        if ag.type == "car_agent":
            car:car_agent = ag
            car_circle = plt.Circle(car.pos, 0.5, color=car.color)
            ax.add_patch(car_circle)
              
def run_animation():
    fig, ax = plt.subplots()
    fig.set_dpi(100)
    fig.set_size_inches(50, 50)
    params = {"steps": 12000, "size": size}
    model = car_model(params)

    anim = ap.animate(model, fig, ax, plot_animation)
    anim.save("animation2.mp4")
 
run_animation()
