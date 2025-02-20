import argparse
import os
import time
import numpy as np
from watcher import start_watching

def main():
    parser = argparse.ArgumentParser(description="Initialize mouse training system.")
    parser.add_argument("--mouse_id", type=str, required=True, help="ID of the mouse.")
    parser.add_argument("--stage", type=str, choices=["hab1", "hab2", "5csr", "5csr_citi_10", "5csr_citi_8", "5csr_citi_4", "5csr_citi_2", "5csr_viti", 
                      "rcpt_viti_2_to_1", "rcpt_viti_2", "rcpt_viti_175", "rcpt_viti_15", "5cpt"], required=True, help="Current training stage.")
    parser.add_argument("--duration", type=int, required=True, default=10800, help="Duration of data collection.")
    parser.add_argument("--terminate_stage", type=str, choices=["hab1", "hab2", "5csr", "5csr_citi_10", "5csr_citi_8", "5csr_citi_4", "5csr_citi_2", "5csr_viti", 
                      "rcpt_viti_2_to_1", "rcpt_viti_2", "rcpt_viti_175", "rcpt_viti_15", "5cpt"], help="Terminate at this stage.")
    args = parser.parse_args()

    print(f"Monitoring test.txt for Mouse ID {args.mouse_id}, Stage {args.stage}...")
    start_watching(args.mouse_id, args.stage, args.duration, args.terminate_stage)

if __name__ == "__main__":
    main()
