import random
import argparse
import csv
import time
import os

def generate_data(size, N):
    """Generates behavioral test data with constraints."""
    # Define value ranges for each metric
    SD_range = (100, 5000)  # Stimulus Duration in milliseconds (100 ms to 5 seconds)
    Prem_range = (0, 1)  # Premature responses
    Om_range = (0, 1)  # Omissions
    Corr_W_range = (0, 1)  # Correct withholding
    Incorr_W_range = (0, 1)  # Incorrect withholding

    # Generate monotonically increasing correct and incorrect values
    correct = [0]
    incorrect = [0]
    for _ in range(1, size):
        remaining = N - correct[-1] - incorrect[-1]
        if remaining > 0:
            corr_inc = min(1, remaining)
            incorr_inc = min(1, remaining - corr_inc)
        else:
            corr_inc = 0
            incorr_inc = 0
        correct.append(correct[-1] + corr_inc)
        incorrect.append(incorrect[-1] + incorr_inc)

    # Ensure monotonicity
    for i in range(1, size):
        incorrect[i] = max(incorrect[i], incorrect[i - 1])

    # Generate data rows
    data = []
    for i in range(size):
        row = [
            random.randint(*SD_range),
            correct[i],
            incorrect[i],
            random.randint(*Prem_range),
            random.randint(*Om_range),
            random.randint(*Corr_W_range),
            random.randint(*Incorr_W_range),
        ]
        data.append(row)

    return data

def save_to_file(filename, data, append=False):
    """Saves data to file. Overwrites on first call, appends otherwise."""
    headers = ["SD", "Corr", "Incorr", "Prem", "Om", "Corr W", "Incorr W"]
    
    mode = "a" if append else "w"  # Append only when appending interval data
    file_exists = os.path.exists(filename)

    with open(filename, mode, newline="") as f:
        writer = csv.writer(f, delimiter="\t")  # Tab-separated values
        if not append or not file_exists:  # Write headers only if overwriting
            writer.writerow(headers)
        writer.writerows(data)

def main():
    parser = argparse.ArgumentParser(description="Generate random test data for behavioral metrics.")
    parser.add_argument("--size", type=int, required=True, help="Number of data rows to generate.")
    parser.add_argument("--N", type=int, required=True, help="Total sum of correct and incorrect responses.")
    parser.add_argument("--interval", type=int, nargs="?", default=0, help="Time interval in seconds to append data continuously.")
    args = parser.parse_args()

    filename = "test.txt"
    
    # First run: Overwrite test.txt
    data = generate_data(args.size, args.N)
    save_to_file(filename, data, append=False)  # Overwrite initially
    print(f"Generated {args.size} rows of data and saved to {filename}")

    # Continuous appending mode
    while args.interval > 0:
        time.sleep(args.interval)
        data = generate_data(args.size, args.N)
        save_to_file(filename, data, append=True)  # Append new data
        print(f"Appended {args.size} rows of data to {filename}")

if __name__ == "__main__":
    main()
