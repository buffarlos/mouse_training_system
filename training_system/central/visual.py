import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import numpy as np  # ensure numpy is imported if needed

def generate_plot(mouse_id, stage, metrics):
    """Generates and saves a performance plot for the given mouse and stage."""
    
    if stage == "hab1":
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_title(f"Mouse {mouse_id} - {stage} Progress", pad=10)
        
        # Calculate progress
        total_responses = metrics["Count"]
        progress = min(total_responses / 30, 1)  # Cap at 100%
        
        # Define progress bar dimensions.
        bar_left = 0.1   
        bar_bottom = 0.7   # Position the bar near the top of the axis
        bar_width = 0.8   
        bar_height = 0.08  # Slim progress bar
        
        # Draw the background of the progress bar with rounded corners.
        bg_bar = patches.FancyBboxPatch(
            (bar_left, bar_bottom),
            bar_width,
            bar_height,
            boxstyle="round,pad=0.02",
            edgecolor="gray",
            facecolor="lightgray",
            lw=2
        )
        ax.add_patch(bg_bar)
        
        # Draw the filled portion.
        filled_width = bar_width * progress
        filled_bar = patches.FancyBboxPatch(
            (bar_left, bar_bottom),
            filled_width,
            bar_height,
            boxstyle="round,pad=0.02",
            edgecolor="none",
            facecolor="seagreen"
        )
        ax.add_patch(filled_bar)
        
        # Add percentage label centered in the progress bar.
        ax.text(
            bar_left + filled_width / 2,
            bar_bottom + bar_height / 2,
            f"{int(progress * 100)}%",
            ha="center",
            va="center",
            fontsize=12,
            color="white",
            weight="bold"
        )
        
        # Add a label below the progress bar with the response count.
        ax.text(
            0.5, 
            bar_bottom - 0.05,
            f"Responses: {int(total_responses)}/30",
            ha="center",
            va="top",
            fontsize=12,
            color="black"
        )
        
        # Tighten axis limits.
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        
        # -----------------------------
        # Add latency table below the progress bar (only Reward latency, labeled in ms)
        # -----------------------------
        latency_data = [
            ["Reward (ms)", f'{metrics["Cumulative Reward Latency"]:.2f}']
        ]
        table = ax.table(
            cellText=latency_data, 
            colLabels=["Latency Type", "Value"],
            loc='bottom',
            bbox=[0, 0.0, 1, 0.3]
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)
    
    elif stage == "hab2":
        # For hab2, we have two subplots: one for the progress bar and one for the breakdown.
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        # Reduce white space between plots and table.
        fig.subplots_adjust(top=0.65, bottom=0.25, hspace=0.15)
        
        # ---- Progress Bar Subplot (ax1) ----
        ax1.set_title(f"Mouse {mouse_id} - {stage} Progress", pad=10)
        total_response = metrics["Count"]
        progress = min(total_response / 70, 1)
        bar_left = 0.1   
        bar_bottom = 0.55   # near top of ax1
        bar_width = 0.8   
        bar_height = 0.08
        
        # Draw background.
        bg_bar = patches.FancyBboxPatch(
            (bar_left, bar_bottom),
            bar_width,
            bar_height,
            boxstyle="round,pad=0.02",
            edgecolor="gray",
            facecolor="lightgray",
            lw=2
        )
        ax1.add_patch(bg_bar)
        
        # Draw filled portion.
        filled_width = bar_width * progress
        filled_bar = patches.FancyBboxPatch(
            (bar_left, bar_bottom),
            filled_width,
            bar_height,
            boxstyle="round,pad=0.02",
            edgecolor="none",
            facecolor="seagreen"
        )
        ax1.add_patch(filled_bar)
        
        # Add percentage label in the progress bar.
        ax1.text(
            bar_left + filled_width / 2,
            bar_bottom + bar_height / 2,
            f"{int(progress * 100)}%",
            ha="center",
            va="center",
            fontsize=12,
            color="white",
            weight="bold"
        )
        
        # Add a label below the progress bar.
        ax1.text(
            0.5,
            bar_bottom - 0.05,
            f"Responses: {int(total_response)}/70",
            ha="center",
            va="top",
            fontsize=12,
            color="black"
        )
        
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0.35, 0.7)

        ax1.axis("off")
        
        # ---- Breakdown Plot (ax2): Total Response vs. Omitted Response ----
        omitted_response = metrics["Omission"]  # Use the provided omission metric
        labels = ["Total Response", "Omitted Response"]
        values = [total_response, omitted_response]
        ax2.bar(labels, values, color=["blue", "orange"])
        ax2.set_ylabel("Number of Responses")
        ax2.set_ylim(0, max(total_response, omitted_response) * 1.2)
        for i, val in enumerate(values):
            ax2.text(i, val + 1, f"{int(val)}", ha="center", fontsize=10, weight="bold")
        ax2.set_title("Response Breakdown", pad=10)
        
        # -----------------------------
        # Add latency table below the breakdown plot (only Reward and Premature, labeled in ms)
        # -----------------------------
        latency_data = [
            ["Reward (ms)", f'{metrics["Cumulative Reward Latency"]:.2f}'],
            ["Premature (ms)", f'{metrics["Cumulative Premature Latency"]:.2f}']
        ]
        # Move the table up by reducing the bottom offset and height.
        ax_table = fig.add_axes([0.15, 0.02, 0.7, 0.15])
        ax_table.axis("off")
        table = ax_table.table(
            cellText=latency_data, 
            colLabels=["Latency Type", "Value"],
            loc="center"
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
    
    #TODO Visuals for everything beyond hab: 5csr_citi, 5csr_viti, rcpt2to1, rcpt_v, cpt
    elif stage in ["5csr", "cpt"]:
        # Line plot for 5CSR and CPT stages.
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
        ax.set_ylim(0, 100)
        ax.set_ylabel("Percentage (%)")
        ax.set_xlabel("Metric")
        ax.set_title(f"Mouse {mouse_id} - {stage} Performance")
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
    plt.savefig(file_path, bbox_inches="tight")
    plt.close()
    
    return file_path

def visualize(mouse_id, stage, metrics):
    """Generates and saves the plot, printing the file path."""
    file_path = generate_plot(mouse_id, stage, metrics)
    print(f"Saved plot: {file_path}")
