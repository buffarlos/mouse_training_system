import argparse
import os
import time
import numpy as np
from watcher import start_watching

def main():
    parser = argparse.ArgumentParser(description="Initialize mouse training system.")
    parser.add_argument("--mouse_id", type=str, required=True, help="ID of the mouse.")
    parser.add_argument("--stage", type=str, choices=["hab1", "hab2", "5csr", "cpt"], required=True, help="Current training stage.")
    parser.add_argument("--duration", type=int, required=True, default=10800, help="Duration of data collection")
    args = parser.parse_args()

    print(f"Monitoring test.txt for Mouse ID {args.mouse_id}, Stage {args.stage}...")
    start_watching(args.mouse_id, args.stage, args.duration)

if __name__ == "__main__":
    main()
