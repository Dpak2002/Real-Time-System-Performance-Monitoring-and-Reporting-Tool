import time
import threading
import pandas as pd
import matplotlib.pyplot as plt
from collections import deque
import psutil
import os

REFRESH_INTERVAL = 1
MAX_HISTORY = 100
REPORT_FILE = "report.csv"

performance_data = []
cpu_usage_history = deque(maxlen=MAX_HISTORY)
memory_usage_history = deque(maxlen=MAX_HISTORY)
network_sent_history = deque(maxlen=MAX_HISTORY)
network_recv_history = deque(maxlen=MAX_HISTORY)


def log_sys():

    while True:
        current_time = time.strftime("%H:%M:%S")
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_percent = psutil.virtual_memory().percent
        net_io = psutil.net_io_counters()
        net_sent = net_io.bytes_sent / (1024**2)
        net_recv = net_io.bytes_recv / (1024**2)
        print(f"{current_time:<10} | {cpu_percent:<10.2f} | {memory_percent:<10.2f} | {net_sent:<15.2f} | {net_recv:<15.2f}")

        cpu_usage_history.append(cpu_percent)
        memory_usage_history.append(memory_percent)
        network_sent_history.append(net_sent)
        network_recv_history.append(net_recv)

        performance_data.append({
            "Time": current_time,
            "CPU (%)": cpu_percent,
            "Memory (%)": memory_percent,
            "Net Sent (MB)": net_sent,
            "Net Recv (MB)": net_recv
        })

        time.sleep(REFRESH_INTERVAL)


def export_report():
    """
    Exports the performance data to a CSV file using Pandas.
    """
    if performance_data:
        df = pd.DataFrame(performance_data)
        df.to_csv(REPORT_FILE, index=False)
    else:
        print("\nNo performance data to export.")


def visualize_metrics():
    """
    Real-time visualization of system metrics using Matplotlib.
    """
    plt.ion()  
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle("Real-Time System Performance Monitoring")

    while plt.fignum_exists(fig.number): 
        for ax in axs.flat:
            ax.clear()

        axs[0, 0].plot(cpu_usage_history, label="CPU Usage (%)", color="blue")
        axs[0, 0].set_title("CPU Usage (%)")
        axs[0, 0].set_ylim(0, 100)

        axs[0, 1].plot(memory_usage_history, label="Memory Usage (%)", color="green")
        axs[0, 1].set_title("Memory Usage (%)")
        axs[0, 1].set_ylim(0, 100)

        axs[1, 0].plot(network_sent_history, label="Network Sent (MB)", color="orange")
        axs[1, 0].set_title("Network Sent (MB)")

        axs[1, 1].plot(network_recv_history, label="Network Received (MB)", color="red")
        axs[1, 1].set_title("Network Received (MB)")

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.pause(REFRESH_INTERVAL)

    print("GUI closed. Exiting visualization...")


try:
    logging_thread = threading.Thread(target=log_sys, daemon=True)
    logging_thread.start()

    visualize_metrics()
except KeyboardInterrupt:
    print("\nMonitoring interrupted by user.")
finally:
    export_report()
