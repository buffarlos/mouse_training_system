import matplotlib.pyplot as plt
import base64
import io
import webbrowser
import os
from datetime import datetime

def generate_plot(mouse_id, stage, metrics):
    plt.figure(figsize=(10, 5))
    
    if stage == "hab1":
        labels = ["Correct", "Incorrect", "Omission"]
        values = [metrics["Correct"], metrics["Incorrect"], metrics["Omission"]]
        plt.bar(labels, values, color=["green", "red", "orange"])
        plt.ylabel("Count")
    elif stage == "hab2":
        labels = ["Correct", "Incorrect", "Omission"]
        values = [metrics["Correct"], metrics["Incorrect"], metrics["Omission"]]
        plt.bar(labels, values, color=["blue", "purple", "yellow"])
        plt.ylabel("Count")
    elif stage == "5csr":
        labels = ["Correct %", "Omission %", "Correct Withholding %", "False Alarm Rate", "Hit Rate"]
        values = [
            metrics["Correct Percentage"],
            metrics["Omission Percentage"],
            metrics["Correct Withholding Percentage"],
            metrics["False Alarm Rate"],
            metrics["Hit Rate"]
        ]
        plt.plot(labels, values, marker='o', linestyle='-', color='b')
        plt.ylim(0, 1)
        plt.ylabel("Percentage")
    elif stage == "cpt":
        labels = ["Correct %", "Omission %", "Correct Withholding %", "False Alarm Rate", "Hit Rate"]
        values = [
            metrics["Correct Percentage"],
            metrics["Omission Percentage"],
            metrics["Correct Withholding Percentage"],
            metrics["False Alarm Rate"],
            metrics["Hit Rate"]
        ]
        plt.plot(labels, values, marker='o', linestyle='-', color='r')
        plt.ylim(0, 1)
        plt.ylabel("Percentage")
    
    plt.title(f"Mouse {mouse_id} - {stage} Performance")
    plt.xlabel("Metric")
    plt.grid(True)
    
    # Create directory if it doesn't exist
    folder_name = f"{mouse_id}_{stage}"
    os.makedirs(folder_name, exist_ok=True)
    
    # Generate timestamped filename
    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
    file_path = os.path.join(folder_name, f"{timestamp}.png")
    
    plt.savefig(file_path)
    plt.close()
    
    return file_path

def visualize(mouse_id, stage, metrics):
    file_path = generate_plot(mouse_id, stage, metrics)
    webbrowser.open(file_path)