import random
import argparse
import csv
import time

def generate_data(size, N):
    # Define value ranges for each metric
    SD_range = (100, 5000)  # Stimulus Duration in milliseconds (100 ms to 5 seconds)
    Prem_range = (0, 20)  # Premature responses
    Om_range = (0, 30)  # Omissions
    Corr_W_range = (0, 50)  # Correct withholding
    Incorr_W_range = (0, 20)  # Incorrect withholding

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
    
    # Generate data
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
    headers = ["SD", "Corr", "Incorr", "Prem", "Om", "Corr W", "Incorr W"]
    mode = "a" if append else "w"
    with open(filename, mode, newline="") as f:
        writer = csv.writer(f, delimiter="\t")  # Tab-separated values
        if not append:
            writer.writerow(headers)
        writer.writerows(data)

def main():
    parser = argparse.ArgumentParser(description="Generate random test data for behavioral metrics.")
    parser.add_argument("--size", type=int, required=True, help="Number of data rows to generate.")
    parser.add_argument("--N", type=int, required=True, help="Total sum of correct and incorrect responses.")
    parser.add_argument("--interval", type=int, nargs="?", default=0, help="Time interval in seconds to append data continuously.")
    args = parser.parse_args()
    
    while True:
        data = generate_data(args.size, args.N)
        save_to_file("test.txt", data, append=args.interval > 0)
        print(f"Generated {args.size} rows of data and saved to test.txt")
        
        if args.interval <= 0:
            break
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
