import os
import shutil
import time
import numpy as np
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from metrics import *
from visual import visualize

class Watcher(FileSystemEventHandler):
    """ Watches test.txt and updates metrics when new data is added. """
    STAGE_SEQUENCE = ["hab1", "hab2", "5csr", "cpt"]

    def __init__(self, mouse_id, stage):
        self.mouse_id = mouse_id
        self.stage = stage
        self.mouse_dir = self.create_mouse_directory()  # Ensures fresh directory
        self.metrics = {"Total Trials": 0}
        self.last_processed_row = 0  # Track the last processed row
        self.stage_start_row = 0  # Start tracking from this row for current stage
        self.last_modified_time = 0

    def create_mouse_directory(self):
        """ Overwrites the existing 'mouse_{mouse_id}' directory to start fresh. """
        folder_path = f"mouse_{self.mouse_id}"
        
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)  # **Delete existing folder**
            print(f"Deleted existing directory: {folder_path}")

        os.makedirs(folder_path, exist_ok=True)  # **Recreate the directory**
        print(f"Created fresh directory: {folder_path}")
        
        return folder_path

    def on_modified(self, event):
        """ Detects file updates and triggers metric computation. """
        if event.src_path.endswith("test.txt"):
            current_time = time.time()
            if current_time - self.last_modified_time < 1:
                return
            
            self.last_modified_time = current_time
            print("test.txt has been updated. Recomputing metrics...")
            self.update_metrics()

    def update_metrics(self):
        """ Processes new data and updates metrics. """
        if not os.path.exists("test.txt") or os.stat("test.txt").st_size == 0:
            print("Warning: test.txt is empty. Skipping computation.")
            return

        try:
            data = np.loadtxt("test.txt", delimiter="\t", skiprows=1)
        except Exception as e:
            print(f"Error reading test.txt: {e}")
            return

        if len(data) == 0:
            return

        # Process only from `stage_start_row`
        process_from = self.stage_start_row
        self.last_processed_row = len(data)  # Update last row processed

        # If no new rows, return early
        if process_from >= len(data):
            return

        new_data = data[process_from:].T  # Process only new rows
        self.metrics["Total Trials"] += 1  # Update total trials count

        # Compute metrics from processed rows
        self.metrics["Correct"] = np.sum(new_data[1, :])  
        self.metrics["Incorrect"] = np.sum(new_data[2, :])  
        self.metrics["Omission"] = np.sum(new_data[4, :])  
        self.metrics["Correct Withholding"] = np.sum(new_data[5, :])  
        self.metrics["Incorrect Withholding"] = np.sum(new_data[6, :])
        self.metrics["Cumulative Correct Latency"] = np.sum(new_data[7, :])
        self.metrics["Cumulative Incorrect Latency"] = np.sum(new_data[8, :])
        self.metrics["Cumulative Reward Latency"] = np.sum(new_data[9, :])
        self.metrics["Cumulative Premature Latency"] = np.sum(new_data[10, :])

        # Compute percentages and derived metrics
        self.metrics["Correct Percentage"] = correct_perc(self.metrics["Correct"], self.metrics["Incorrect"])
        self.metrics["Omission Percentage"] = omission_perc(self.metrics["Omission"], self.metrics["Correct"], self.metrics["Incorrect"])
        self.metrics["Correct Withholding Percentage"] = c_wh_perc(self.metrics["Correct Withholding"], self.metrics["Incorrect Withholding"])
        self.metrics["Difference Withholding"] = diff_wh(self.metrics["Correct Withholding Percentage"], self.metrics["Omission Percentage"])
        self.metrics["False Alarm Rate"] = false_alarm(self.metrics["Correct Withholding"], self.metrics["Incorrect Withholding"])
        self.metrics["Hit Rate"] = hit_rate(self.metrics["Correct"], self.metrics["Incorrect"], self.metrics["Omission"])

        print(f"Total Trials: {self.metrics['Total Trials']}")
        print(f"Updated Metrics for Mouse {self.mouse_id}, Stage {self.stage}")

        # Visualization
        visualize(self.mouse_id, self.stage, self.metrics)

        # Save metrics to data.txt
        self.save_metrics()

        # Compute threshold
        threshold = compute_threshold(task=self.stage, metrics=self.metrics)
        if threshold:
            print(f"Threshold met! Advancing from {self.stage} to next stage...")
            self.advance_stage()

    def save_metrics(self):
        """ Saves current metrics to 'mouse_{mouse_id}/{stage}/data.txt'. """
        stage_folder = os.path.join(self.mouse_dir, self.stage)
        os.makedirs(stage_folder, exist_ok=True)  # Ensure stage directory exists
        file_path = os.path.join(stage_folder, "data.txt")

        with open(file_path, "a") as f:  # Append to data.txt
            f.write(f"Total Trials: {self.metrics['Total Trials']}\n")
            f.write(f"Correct: {self.metrics['Correct']}\n")
            f.write(f"Incorrect: {self.metrics['Incorrect']}\n")
            f.write(f"Omission: {self.metrics['Omission']}\n")
            f.write(f"Correct Withholding: {self.metrics['Correct Withholding']}\n")
            f.write(f"Incorrect Withholding: {self.metrics['Incorrect Withholding']}\n")
            f.write(f"Correct Percentage: {self.metrics['Correct Percentage']:.2f}\n")
            f.write(f"Omission Percentage: {self.metrics['Omission Percentage']:.2f}\n")
            f.write(f"Correct Withholding Percentage: {self.metrics['Correct Withholding Percentage']:.2f}\n")
            f.write(f"Difference Withholding: {self.metrics['Difference Withholding']:.2f}\n")
            f.write(f"False Alarm Rate: {self.metrics['False Alarm Rate']:.2f}\n")
            f.write(f"Hit Rate: {self.metrics['Hit Rate']:.2f}\n")
            f.write("-" * 40 + "\n")  # Separator for each update
        print(f"Metrics saved to {file_path}")

    def advance_stage(self):
        """ Advances to the next stage and resets metrics while tracking new rows only. """
        current_index = self.STAGE_SEQUENCE.index(self.stage)
        if current_index < len(self.STAGE_SEQUENCE) - 1:
            self.stage = self.STAGE_SEQUENCE[current_index + 1]
            print(f"New stage: {self.stage}")

            # Update `stage_start_row` to track new stage correctly
            self.stage_start_row = self.last_processed_row
        else:
            print("Final stage reached. No further advancement.")

        # Reset metrics but retain last processed row tracking
        self.metrics = {"Total Trials": self.metrics["Total Trials"]}  

def start_watching(mouse_id, stage, duration):
    """ Initializes and starts the file watcher process. """
    path = os.path.dirname(os.path.abspath("test.txt"))
    event_handler = Watcher(mouse_id, stage)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    start_time = time.time()

    try:
        while time.time() - start_time < duration:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Watcher manually stopped.")
    
    observer.stop()
    observer.join()
    print("Watcher process ended.")
