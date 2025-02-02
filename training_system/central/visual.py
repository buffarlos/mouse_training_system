import matplotlib.pyplot as plt

def visualize(mouse_id, stage, metrics):
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
    plt.show()
