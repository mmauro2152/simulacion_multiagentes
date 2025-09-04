from matplotlib import pyplot as plt
from utils.car_utils import car_agent
import agentpy as ap
from utils.plot_utils import *
from datetime import datetime
from utils.model import car_model
import json

def save_data(model:car_model, filename:str):
    data = model.get_data()

    processing_time = model.end_time - model.start_time
    total_seconds = int(processing_time.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    model.processing_time_str = f"{hours}:{minutes}:{seconds}"

    data["processing_time"] = model.processing_time_str

    with open(f"{filename}.json", "w") as f:
        json.dump(data, f, indent=4)
    
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

    follow_sequence = True

    params = {
        "steps": 2000, 
        "size": size, 
        "lane_width": lane_width,
        "mode": "fixed",
        "follow_sequence": follow_sequence
    }
    
    model = car_model(params)
    
    model.start_time = datetime.now()
    start_time_str = model.start_time.time().strftime("%H:%M:%S")
    print(f"starting time:      {start_time_str}")

    anim = ap.animate(model, fig, ax, plot_animation)
    model.end_time = datetime.now()

    m = params["mode"]
    filename = f"{m} {str(follow_sequence)}"
    anim.save(f"{filename}.mp4")

    save_data(model, filename)

    print(f"took {model.processing_time_str}")


run_animation()
