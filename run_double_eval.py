import os
import subprocess
import pandas as pd

import time

import shutil

def run_eval():
    subprocess.run(["python", "-u", "eval/run_eval.py"], check=True)

print("Waiting 15s for Uvicorn to initialize...")
time.sleep(15)

print("Starting Run 1...")
run_eval()
shutil.move("eval/results.csv", "eval/results_1.csv")

print("\nStarting Run 2...")
run_eval()
shutil.move("eval/results.csv", "eval/results_2.csv")

print("\nComparing Run 1 and Run 2...")
df1 = pd.read_csv("eval/results_1.csv")
df2 = pd.read_csv("eval/results_2.csv")

identical = df1.equals(df2)
if identical:
    print("SUCCESS: The two runs are IDENTICAL row by row!")
else:
    print("WARNING: The two runs are NOT identical!")
    diff = df1.compare(df2)
    print(diff)

print("\nDone!")
