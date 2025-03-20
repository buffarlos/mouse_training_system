import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

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
            ["Cumulative Reward (ms)", f'{metrics["Cumulative Reward Latency"]:.2f}'],
            ["Mean Reward (ms)", f'{metrics["Mean Reward Latency"]:.2f}']
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
        # Use the same figure size as hab1
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_title(f"Mouse {mouse_id} - {stage} Progress", pad=10)
        
        # Calculate progress based on total responses (target is 70)
        total_response = metrics["Count"]
        progress = min(total_response / 70, 1)  # Cap at 100%
        
        # Use the same progress bar dimensions and position as hab1
        bar_left = 0.1
        bar_bottom = 0.7   # same as hab1
        bar_width = 0.8
        bar_height = 0.08
        
        # Draw the background of the progress bar.
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
            f"Responses: {int(total_response)}/70",
            ha="center",
            va="top",
            fontsize=12,
            color="black"
        )
        
        # Tighten axis limits and hide axes.
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        
        # -----------------------------
        # Add latency table below the progress bar (only Reward latency, labeled in ms)
        # -----------------------------
        latency_data = [
            ["Cumulative Reward (ms)", f'{metrics["Cumulative Reward Latency"]:.2f}'],
            ["Mean Reward (ms)", f'{metrics["Mean Reward Latency"]:.2f}']
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

    elif stage in ["5csr_citi_10", "5csr_citi_8", "5csr_citi_4", "5csr_citi_2"]:
        # Extract stimulus duration from stage string (assumes stage format "5csr_citi_<duration>")
        stim_duration = stage.split("_")[-1]
        
        # Create figure with two subplots (one for progress bar, one for breakdown)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        fig.subplots_adjust(top=0.65, bottom=0.25, hspace=0.15)
        
        # ---- Progress Bar Subplot (ax1) ----
        ax1.set_title(f"5csr_citi, stimulus duration: {stim_duration} seconds", pad=10)
        
        correct_responses = metrics["Correct"]
        target_correct = 30  # Adjust as needed
        progress = min(correct_responses / target_correct, 1)
        
        bar_left = 0.1
        bar_bottom = 0.55
        bar_width = 0.8
        bar_height = 0.08
        
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
        
        ax1.text(
            0.5,
            bar_bottom - 0.05,
            f"Correct Responses: {int(correct_responses)}/{target_correct}",
            ha="center",
            va="top",
            fontsize=12,
            color="black"
        )
        
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0.35, 0.7)
        ax1.axis("off")
        
        # ---- Breakdown Plot Subplot (ax2) ----
        total_trials = metrics["Total Trials"]
        labels = ["Correct", "Incorrect", "Premature", "Omission"]
        values = [
            100 * metrics["Correct"] / total_trials,
            100 * metrics["Incorrect"] / total_trials,
            100 * metrics["Premature"] / total_trials,
            100 * metrics["Omission"] / total_trials,
        ]
        
        ax2.bar(labels, values, color=["blue", "red", "purple", "orange"])
        ax2.set_ylabel("Percentage")
        ax2.set_ylim(0, 100)
        ax2.set_title("Response Breakdown", pad=10)
        
        # ---- Latency Table ----
        mean_correct_latency = metrics["Mean Correct Latency"]
        # For 5csr_citi, if the stage is 10, 8, or 4, use half the stimulus duration;
        # if it's 2, then use 75% of the stimulus duration.
        if stage == "5csr_citi_2":
            threshold = float(stim_duration) * 1000 * 0.75
        else:
            threshold = float(stim_duration) * 1000 / 2

        if mean_correct_latency < threshold:
            status = "threshold met"
            value_color = "green"
        else:
            status = "threshold not met"
            value_color = "red"
        
        latency_data = [
            ["Mean Correct Latency (ms)", f'{mean_correct_latency:.2f}', status],
            ["Mean Incorrect Latency (ms)", f'{metrics["Mean Incorrect Latency"]:.2f}', ""],
            ["Mean Reward Latency (ms)", f'{metrics["Mean Reward Latency"]:.2f}', ""],
            ["Mean Premature Latency (ms)", f'{metrics["Mean Premature Latency"]:.2f}', ""]
        ]
        
        ax_table = fig.add_axes([0.15, 0.02, 0.7, 0.15])
        ax_table.axis("off")
        table = ax_table.table(
            cellText=latency_data,
            colLabels=["Latency Type", "Value", "Status"],
            loc="center"
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        
        # Set the text color for the Mean Correct Latency row (first data row) only.
        table[(1, 1)].get_text().set_color(value_color)
        table[(1, 2)].get_text().set_color(value_color)

    elif stage == "5csr_viti":
        # For 5csr_viti, stimulus duration is always 2 seconds.
        stim_duration = 2  
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        fig.subplots_adjust(top=0.65, bottom=0.25, hspace=0.15)
        
        inter_trial_duration = metrics["Inter Trial Duration"]
        
        ax1.set_title(f"5csr_viti, stimulus duration: {stim_duration} seconds, inter trial duration: {int(inter_trial_duration/1000)} seconds", pad=10)
        
        correct_responses = metrics["Correct"]
        target_correct = 30  # Adjust as needed
        progress = min(correct_responses / target_correct, 1)
        
        bar_left = 0.1
        bar_bottom = 0.55
        bar_width = 0.8
        bar_height = 0.08
        
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
        
        ax1.text(
            0.5,
            bar_bottom - 0.05,
            f"Correct Responses: {int(correct_responses)}/{target_correct}",
            ha="center",
            va="top",
            fontsize=12,
            color="black"
        )
        
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0.35, 0.7)
        ax1.axis("off")
        
        total_trials = metrics["Total Trials"]
        labels = ["Correct", "Incorrect", "Premature", "Omission"]
        values = [
            100 * metrics["Correct"] / total_trials,
            100 * metrics["Incorrect"] / total_trials,
            100 * metrics["Premature"] / total_trials,
            100 * metrics["Omission"] / total_trials,
        ]
        
        ax2.bar(labels, values, color=["blue", "red", "purple", "orange"])
        ax2.set_ylabel("Percentage")
        ax2.set_ylim(0, 100)
        ax2.set_title("Response Breakdown", pad=10)
        
        mean_correct_latency = metrics["Mean Correct Latency"]
        # For 5csr_viti, the threshold is 75% of 2 seconds (i.e., 1500 ms).
        if mean_correct_latency < 1500:
            status = "threshold met"
            value_color = "green"
        else:
            status = "threshold not met"
            value_color = "red"
        
        latency_data = [
            ["Mean Correct Latency (ms)", f'{mean_correct_latency:.2f}', status],
            ["Mean Incorrect Latency (ms)", f'{metrics["Mean Incorrect Latency"]:.2f}', ""],
            ["Mean Reward Latency (ms)", f'{metrics["Mean Reward Latency"]:.2f}', ""],
            ["Mean Premature Latency (ms)", f'{metrics["Mean Premature Latency"]:.2f}', ""]
        ]
        
        ax_table = fig.add_axes([0.15, 0.02, 0.7, 0.15])
        ax_table.axis("off")
        table = ax_table.table(
            cellText=latency_data,
            colLabels=["Latency Type", "Value", "Status"],
            loc="center"
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        
        table[(1, 1)].get_text().set_color(value_color)
        table[(1, 2)].get_text().set_color(value_color)

    elif stage in ["rcpt_viti_2_to_1", "rcpt_viti_2", "rcpt_viti_175", "rcpt_viti_15"]:
        # Set stimulus duration based on stage.
        if stage in ["rcpt_viti_2_to_1", "rcpt_viti_2"]:
            stim_duration = 2
        elif stage == "rcpt_viti_175":
            stim_duration = 1.75
        elif stage == "rcpt_viti_15":
            stim_duration = 1.5

        # Create figure with two subplots (one for progress bar, one for breakdown)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        fig.subplots_adjust(top=0.65, bottom=0.25, hspace=0.15)
        
        inter_trial_duration = metrics["Inter Trial Duration"]
        
        ax1.set_title(
            f"rcpt_viti, stimulus duration: {stim_duration} seconds, inter trial duration: {int(inter_trial_duration/1000)} seconds", 
            pad=10
        )
        
        correct_responses = metrics["Count"]
        target_correct = 30  # Adjust as needed
        progress = min(correct_responses / target_correct, 1)
        
        bar_left = 0.1
        bar_bottom = 0.55
        bar_width = 0.8
        bar_height = 0.08
        
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
        
        ax1.text(
            0.5,
            bar_bottom - 0.05,
            f"Correct Responses: {int(correct_responses)}/{target_correct}",
            ha="center",
            va="top",
            fontsize=12,
            color="black"
        )
        
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.axis("off")
        
        # ---- Breakdown Plot (ax2) ----
        total_trials = metrics["Total Trials"]
        # Include Correct Withholding as an additional breakdown.
        labels = ["Correct", "Incorrect", "Premature", "Omission", "Correct Withholding"]
        values = [
            100 * metrics["Correct"] / total_trials,
            100 * metrics["Incorrect"] / total_trials,
            100 * metrics["Premature"] / total_trials,
            100 * metrics["Omission"] / total_trials,
            metrics["Correct Withholding Percentage"]  # assumed to be already in percent
        ]
        
        ax2.bar(labels, values, color=["blue", "red", "purple", "orange", "teal"])
        ax2.set_ylabel("Percentage")
        ax2.set_ylim(0, 100)
        ax2.set_title("Response Breakdown", pad=10)
        
        # ---- Latency Table ----
        mean_correct_latency = metrics["Mean Correct Latency"]
        # For all these stages, the threshold is fixed at 1500 ms.
        if mean_correct_latency < 1500:
            status = "threshold met"
            value_color = "green"
        else:
            status = "threshold not met"
            value_color = "red"
        
        latency_data = [
            ["Mean Correct Latency (ms)", f'{mean_correct_latency:.2f}', status],
            ["Mean Incorrect Latency (ms)", f'{metrics["Mean Incorrect Latency"]:.2f}', ""],
            ["Mean Reward Latency (ms)", f'{metrics["Mean Reward Latency"]:.2f}', ""],
            ["Mean Premature Latency (ms)", f'{metrics["Mean Premature Latency"]:.2f}', ""]
        ]
        
        ax_table = fig.add_axes([0.15, 0.02, 0.7, 0.15])
        ax_table.axis("off")
        table = ax_table.table(
            cellText=latency_data,
            colLabels=["Latency Type", "Value", "Status"],
            loc="center"
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        
        # Conditionally color the Mean Correct Latency row.
        table[(1, 1)].get_text().set_color(value_color)
        table[(1, 2)].get_text().set_color(value_color)
    
    plt.grid(False)
    
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
