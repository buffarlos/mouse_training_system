import matplotlib.pyplot as plt
import os

def generate_plot(mouse_id, stage, metrics):
    """Generates and saves a performance plot for the given mouse and stage."""
    fig, ax = plt.subplots(figsize=(10, 6))  # Create figure and axis

    if stage == "hab1":
        # Horizontal progress bar for (Correct + Incorrect) out of 30
        total_responses = metrics["Correct"] + metrics["Incorrect"]
        progress = min(total_responses / 30, 1)  # Cap at 100%
        
        ax.barh(["Progress"], [progress], color="green")
        ax.set_xlabel("Total Response Completion")
        ax.set_title(f"Mouse {mouse_id} - {stage} Progress")
        ax.set_xlim(0, 1)
        
        # Show percentage label
        ax.text(progress, 0, f"{int(progress * 100)}%", va="center", ha="right", fontsize=12, color="white", weight="bold")

        # Fix x-axis to show percentages every 20%
        ax.set_xticks([i / 5 for i in range(0, 6)])
        ax.set_xticklabels([f"{i * 20}%" for i in range(0, 6)])

    elif stage == "hab2":
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))  # Create two subplots

        # **Add more space between subplots**
        fig.subplots_adjust(hspace=0.4)  # Increases vertical spacing

        # Progress Bar (Correct out of 70)
        progress = min(metrics["Correct"] / 70, 1)  # Cap at 100%
        ax1.barh(["Progress"], [progress], color="blue")
        ax1.set_xlim(0, 1)
        ax1.set_xlabel("Correct Response Completion)")
        ax1.set_title(f"Mouse {mouse_id} - {stage} Progress")
        
        # Show percentage label
        ax1.text(progress, 0, f"{int(progress * 100)}%", va="center", ha="right", fontsize=12, color="white", weight="bold")

        # Fix x-axis to show percentages every 20%
        ax1.set_xticks([i / 5 for i in range(0, 6)])
        ax1.set_xticklabels([f"{i * 20}%" for i in range(0, 6)])

        # Percentage Breakdown (Correct, Incorrect, Omission)
        labels = ["Correct", "Incorrect", "Omission"]
        values = [
            metrics["Correct Percentage"] * 100,
            metrics["Omission Percentage"] * 100,
            100 - (metrics["Correct Percentage"] * 100 + metrics["Omission Percentage"] * 100)  # Remaining as Incorrect
        ]

        ax2.bar(labels, values, color=["green", "red", "orange"])
        ax2.set_ylabel("Percentage (%)")
        ax2.set_title("Response Breakdown")

        # Show percentage labels on bars
        for i, value in enumerate(values):
            ax2.text(i, value + 2, f"{int(value)}%", ha="center", fontsize=10, weight="bold")

        ax2.set_ylim(0, 100)

    elif stage in ["5csr", "cpt"]:
        # Line plot for 5CSR and CPT stages
        labels = ["Correct %", "Omission %", "Correct Withholding %", "False Alarm Rate", "Hit Rate"]
        values = [
            metrics["Correct Percentage"] * 100,
            metrics["Omission Percentage"] * 100,
            metrics["Correct Withholding Percentage"] * 100,
            metrics["False Alarm Rate"] * 100,
            metrics["Hit Rate"] * 100
        ]

        ax.plot(labels, values, marker='o', linestyle='-', color='b' if stage == "5csr" else 'r')
        ax.set_ylim(0, 100)  # Set percentage range from 0 to 100
        ax.set_ylabel("Percentage (%)")
        ax.set_xlabel("Metric")
        ax.set_title(f"Mouse {mouse_id} - {stage} Performance")

        # Show percentage labels above markers
        for i, value in enumerate(values):
            ax.text(i, value + 2, f"{int(value)}%", ha="center", fontsize=10, weight="bold")

        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels)

    plt.grid(False)  # Disable grid for a cleaner look

    # Define folder structure
    folder_path = os.path.join(f"mouse_{mouse_id}", stage)
    os.makedirs(folder_path, exist_ok=True)  # Ensure directory exists

    # Generate filename based on trial count
    trial_number = metrics["Total Trials"]
    file_path = os.path.join(folder_path, f"trial_{trial_number}.png")

    plt.savefig(file_path)
    plt.close()
    
    return file_path

def visualize(mouse_id, stage, metrics):
    """Saves the generated plot to the appropriate folder."""
    file_path = generate_plot(mouse_id, stage, metrics)
    print(f"Saved plot: {file_path}")
