import matplotlib.pyplot as plt
import os
import numpy as np  # make sure numpy is imported if you use np.sum

def generate_plot(mouse_id, stage, metrics):
    """Generates and saves a performance plot for the given mouse and stage."""
    
    if stage == "hab1":
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Increase bottom space to accommodate the table.
        plt.subplots_adjust(bottom=0.4)
        
        # Horizontal progress bar for (Correct + Incorrect) out of 30
        total_responses = metrics["Correct"] + metrics["Incorrect"]
        progress = min(total_responses / 30, 1)  # Cap at 100%
        
        ax.barh(["Progress"], [progress], color="green")
        ax.set_xlabel("Total Response Completion")
        ax.set_title(f"Mouse {mouse_id} - {stage} Progress", pad=20)
        ax.set_xlim(0, 1)
        
        # Show percentage label on the progress bar
        ax.text(progress, 0, f"{int(progress * 100)}%", va="center", 
                ha="right", fontsize=12, color="white", weight="bold")
        
        # Fix x-axis to show percentages every 20%
        ax.set_xticks([i / 5 for i in range(0, 6)])
        ax.set_xticklabels([f"{i * 20}%" for i in range(0, 6)])
        
        # -----------------------------
        # Add latency table to hab1 plot
        # -----------------------------
        latency_data = [
            ["Correct", f'{metrics["Cumulative Correct Latency"]:.2f}'],
            ["Incorrect", f'{metrics["Cumulative Incorrect Latency"]:.2f}'],
            ["Reward", f'{metrics["Cumulative Reward Latency"]:.2f}'],
            ["Premature", f'{metrics["Cumulative Premature Latency"]:.2f}']
        ]
        # Adjust the bbox to push the table further down from the plot area.
        table = ax.table(cellText=latency_data, 
                         colLabels=["Latency Type", "Value"],
                         loc='bottom',
                         bbox=[0, -0.5, 1, 0.3])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)
    
    elif stage == "hab2":
        # Create two subplots for hab2.
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        # Increase bottom margin to leave space for the table (e.g., bottom=0.3)
        fig.subplots_adjust(bottom=0.3, hspace=0.4)
        
        # -----------------------------
        # Progress Bar (Correct out of 70)
        # -----------------------------
        progress = min(metrics["Correct"] / 70, 1)  # Cap at 100%
        ax1.barh(["Progress"], [progress], color="blue")
        ax1.set_xlim(0, 1)
        ax1.set_xlabel("Correct Response Completion")
        ax1.set_title(f"Mouse {mouse_id} - {stage} Progress")
        
        # Show percentage label on progress bar
        ax1.text(progress, 0, f"{int(progress * 100)}%", va="center",
                 ha="right", fontsize=12, color="white", weight="bold")
        
        # Fix x-axis to show percentages every 20%
        ax1.set_xticks([i / 5 for i in range(0, 6)])
        ax1.set_xticklabels([f"{i * 20}%" for i in range(0, 6)])
        
        # -----------------------------
        # Percentage Breakdown (Correct, Incorrect, Omission)
        # -----------------------------
        labels = ["Correct", "Incorrect", "Omission"]
        values = [
            metrics["Correct Percentage"] * 100,
            metrics["Omission Percentage"] * 100,
            100 - (metrics["Correct Percentage"] * 100 + metrics["Omission Percentage"] * 100)
        ]
        ax2.bar(labels, values, color=["green", "red", "orange"])
        ax2.set_ylabel("Percentage (%)")
        ax2.set_title("Response Breakdown")
        
        # Show percentage labels on bars
        for i, value in enumerate(values):
            ax2.text(i, value + 2, f"{int(value)}%", ha="center", fontsize=10, weight="bold")
        ax2.set_ylim(0, 100)
        
        # -----------------------------
        # Add latency table to hab2 plot
        # -----------------------------
        latency_data = [
            ["Correct", f'{metrics["Cumulative Correct Latency"]:.2f}'],
            ["Incorrect", f'{metrics["Cumulative Incorrect Latency"]:.2f}'],
            ["Reward", f'{metrics["Cumulative Reward Latency"]:.2f}'],
            ["Premature", f'{metrics["Cumulative Premature Latency"]:.2f}']
        ]
        # Adjust the position of the table so it doesn't overlap with ax2.
        # The new coordinates [0.15, 0.02, 0.7, 0.22] place the table
        # in the bottom margin of the figure.
        ax_table = fig.add_axes([0.15, 0.02, 0.7, 0.22])
        ax_table.axis('off')
        table = ax_table.table(cellText=latency_data, 
                               colLabels=["Latency Type", "Value"],
                               loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
    
    elif stage in ["5csr", "cpt"]:
        # Line plot for 5CSR and CPT stages
        fig, ax = plt.subplots(figsize=(10, 6))
        labels = ["Correct %", "Omission %", "Correct Withholding %", "False Alarm Rate", "Hit Rate"]
        values = [
            metrics["Correct Percentage"] * 100,
            metrics["Omission Percentage"] * 100,
            metrics["Correct Withholding Percentage"] * 100,
            metrics["False Alarm Rate"] * 100,
            metrics["Hit Rate"] * 100
        ]
        
        ax.plot(labels, values, marker='o', linestyle='-', 
                color='b' if stage == "5csr" else 'r')
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
    
    # Define folder structure and save the plot.
    folder_path = os.path.join(f"mouse_{mouse_id}", stage)
    os.makedirs(folder_path, exist_ok=True)
    trial_number = metrics["Total Trials"]
    file_path = os.path.join(folder_path, f"trial_{trial_number}.png")
    plt.savefig(file_path)
    plt.close()
    
    return file_path

def visualize(mouse_id, stage, metrics):
    """Saves the generated plot to the appropriate folder."""
    file_path = generate_plot(mouse_id, stage, metrics)
    print(f"Saved plot: {file_path}")
