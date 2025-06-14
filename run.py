#!/usr/bin/env python3

import sys
import os
import json
import subprocess

JSON_EXECUTED_NAME = "./executed.json"
STANDARD_DATSET_NAME = "G1_1e4_1e1_0_0"

def executing(cmd, env=None, use_bash_c=False):
    """
    Run a shell command and print status. 
    If it fails, print error and exit.
    If use_bash_c is True, runs: bash -c 'cmd' (for commands like 'source ...').
    """
    print(f"[EXECUTING] {cmd}")
    if use_bash_c:
        result = subprocess.run(["bash", "-c", cmd], env=env)
    else:
        result = subprocess.run(cmd, shell=True, env=env)
    if result.returncode != 0:
        print(f"[ERROR] Command failed: {cmd}")
        return result.returncode
    print(f"[OK] Command succeeded: {cmd}")
    return 0

def load_executed():
    if os.path.exists(JSON_EXECUTED_NAME):
        with open(JSON_EXECUTED_NAME, "r") as f:
            executed = json.load(f)
    else:
        executed = {}
    return executed

def save_executed(executed):
    with open(JSON_EXECUTED_NAME, "w") as f:
        json.dump(executed, f, indent=4)


def run_all_commands(lib_name, lib_version, executed):
    key = f"{lib_name}:{lib_version}"
    if executed[key]['tried']:
        print(f"[INFO] {key} already executed. Exiting.")
        return executed[key]['tried'], executed[key]['error']

    # === Set environment variables for all subprocesses ===
    env = os.environ.copy()

    env["SRC_DATANAME"] = STANDARD_DATSET_NAME
    env["MACHINE_TYPE"] = "mac"
    env["SPILL_DIR"] = "."

    commands = [
        f"rm -f -r {lib_name}/py-{lib_name}",
        f"bash {lib_name}/setup-{lib_name}.sh {lib_version}",
        f"source {lib_name}/py-{lib_name}/bin/activate",
        f"python {lib_name}/groupby-{lib_name}.py",
        f"python {lib_name}/join-{lib_name}.py",
        "deactivate"
    ]

    # Concatenate all commands with &&
    cmd_concat = " && ".join(commands)
    
    ret = executing(cmd_concat, env=env, use_bash_c=True)
    if ret != 0:
        return True, True
    

    return True, False
    


# === Argument parsing ===
lib_name = sys.argv[1]          # e.g. "pandas" or "polars"
lib_version = sys.argv[2]       # e.g. "2.3.0"
key = f"{lib_name}:{lib_version}"
executed = load_executed()
executed[key] = executed.get(key, {})
executed[key]['tried'] = executed[key].get('tried', False)
executed[key]['error'] = executed[key].get('error', False)

executed[key]['tried'], executed[key]['error'] = run_all_commands(lib_name, lib_version, executed)

save_executed(executed)
print(f"[OK] {key} execution recorded.")

