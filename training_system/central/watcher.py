import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from metrics import *
from visual import visualize

class Watcher(FileSystemEventHandler):
    """ Watches test.txt and updates metrics when new data is added. """
    def __init__(self, mouse_id, stage):
        self.mouse_id = mouse_id
        self.stage = stage
        self.metrics = {}

    def on_modified(self, event):
        if event.src_path.endswith("test.txt"):
            print("test.txt has been updated. Recomputing metrics...")
            self.update_metrics()

    def update_metrics(self):
        with open("test.txt", "r") as file:
            lines = file.readlines()[1:]  # Skip headers
            data = [list(map(int, line.strip().split())) for line in lines]
            
        # Compute all required metrics
        self.metrics["Correct"] = sum(row[1] for row in data)
        self.metrics["Incorrect"] = sum(row[2] for row in data)
        self.metrics["Omission"] = sum(row[4] for row in data)
        self.metrics["Correct Withholding"] = sum(row[5] for row in data)
        self.metrics["Incorrect Withholding"] = sum(row[6] for row in data)
        
        self.metrics["Correct Percentage"] = correct_perc(self.metrics["Correct"], self.metrics["Incorrect"])
        self.metrics["Omission Percentage"] = omission_perc(self.metrics["Omission"], self.metrics["Correct"], self.metrics["Incorrect"])
        self.metrics["Correct Withholding Percentage"] = c_wh_perc(self.metrics["Correct Withholding"], self.metrics["Incorrect Withholding"])
        self.metrics["Difference Withholding"] = diff_wh(self.metrics["Correct Withholding Percentage"], self.metrics["Omission Percentage"])
        self.metrics["False Alarm Rate"] = false_alarm(self.metrics["Correct Withholding"], self.metrics["Incorrect Withholding"])
        self.metrics["Hit Rate"] = hit_rate(self.metrics["Correct"], self.metrics["Incorrect"], self.metrics["Omission"])
        print(f"Updated Metrics for Mouse {self.mouse_id}, Stage {self.stage}")

        # Compute threshold
        threshold = compute_threshold(task=self.stage, metrics=self.metrics)

        # Visualization
        visualize(self)

        print(f"Threshold Passed for next stage: {threshold}")

def start_watching(mouse_id, stage, duration):
    path = os.path.dirname(os.path.abspath("test.txt"))
    event_handler = Watcher(mouse_id, stage)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()


    start_time = time.time()  # Track start time

    try:
        while time.time() - start_time < duration:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Watcher manually stopped.")
    
    observer.stop()
    observer.join()
    print("Watcher process ended.")
