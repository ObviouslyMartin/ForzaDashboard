'''
visualize manages the display window. Reads from consumer and ouputs the data
while the data_queue filled by fdpconsumer has item(s) it it.

Copyright (c) 2024 Martin Plut

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time


class FDPVisualizer():
    def __init__(self, stop_event, data_queue, params) -> None:
        self.stop_event=stop_event,
        self.data_queue = data_queue,
        self.params = params
    
    # show engine rpm over time. will update to dynamically show graphs based on input params
    def visualize_data(stop_event, data_queue):
        fig, ax = plt.subplots()
        x_data, y_data = [], []

        def update_graph(frame):
            while not data_queue.empty() and not stop_event.is_set():
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