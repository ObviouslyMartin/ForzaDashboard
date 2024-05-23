import matplotlib.pyplot as plt

from matplotlib.animation import FuncAnimation
import time

def visualize_data(stop_event, data_queue):
    fig, ax = plt.subplots()
    x_data, y_data = [], []

    def update_graph(frame):
        while not data_queue.empty():
            packet = data_queue.get()
            engine_rpm = packet.get('current_engine_rpm', None)
            engine_max_rpm = packet.get('engine_max_rpm', None)
            if engine_rpm is not None:
                x_data.append(time.time())
                y_data.append(engine_rpm)
                ax.clear()
                ax.plot(x_data, y_data)
                ax.set_title("Engine RPM over Time")
                ax.set_xlabel("Time")
                ax.set_ylabel("Engine RPM")

    ani = FuncAnimation(fig, update_graph, interval=1)  # Update every millisecond
    plt.show()