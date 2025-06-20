#!/usr/bin/env python3

import sys
import os
import json
import subprocess
from util.python_lib_info import versions
from packaging.version import parse

JSON_EXECUTED_NAME = "./executed.json"
STANDARD_DATSET_NAME = "G1_1e4_1e1_0_0"
MAX_EXECUTIONS = 10  # Maximum number of executions to run

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

def prepare_env(lib_name, lib_version, python_version):
    commands = [
        f"rm -f -r {lib_name}/py-{lib_name}",
        f"bash {lib_name}/setup-{lib_name}.sh {lib_version} {python_version}"
    ]
    env = os.environ.copy()
    env["SRC_DATANAME"] = STANDARD_DATSET_NAME

    # Concatenate all commands with &&
    cmd_concat = " && ".join(commands)
    
    return executing(cmd_concat, env=env, use_bash_c=True) == 0
    


def run_all_commands(lib_name, lib_version, execution_data, python_version, execution, profile=False):
    key = f"{lib_name}:{lib_version}"
    if execution_data['tried']:
        print(f"[INFO] {key} already executed. Exiting.")
        return execution_data['tried'], execution_data['error']

    # === Set environment variables for all subprocesses ===
    env = os.environ.copy()

    env["SRC_DATANAME"] = STANDARD_DATSET_NAME
    env["MACHINE_TYPE"] = "mac"
    env["SPILL_DIR"] = "."

    commands = [
        f"source {lib_name}/py-{lib_name}/bin/activate",
        f"python {lib_name}/groupby-{lib_name}.py {execution}",
        f"python {lib_name}/join-{lib_name}.py {execution}",
        "deactivate"
    ]

    if profile:
        commands = [
            f"{lib_name}/py-{lib_name}/bin/pyinstrument  -t -o {lib_name}_{lib_version}_groupby.json {lib_name}/groupby-{lib_name}.py {execution}",
            f"{lib_name}/py-{lib_name}/bin/pyinstrument -t -o {lib_name}_{lib_version}_join.json {lib_name}/join-{lib_name}.py {execution}",
        ]


    # Concatenate all commands with &&
    cmd_concat = " && ".join(commands)
    
    ret = executing(cmd_concat, env=env, use_bash_c=True)
    if ret != 0:
        return True, True
    

    return True, False




# === Argument parsing ===
if len(sys.argv) == 2:
    
    lib_name = sys.argv[1]          # e.g. "pandas" or "polars"
    versions_list = versions(lib_name)
    versions_list = sorted(versions_list, key=lambda x: x[0], reverse=True)
    executed = load_executed()
    for lib_version, python_version in versions_list:
        lib_version = str(lib_version)
        python_version = str(python_version)
        key = f"{lib_name}:{lib_version}"
        executed[key] = executed.get(key, {})
        if not executed[key].get(str(MAX_EXECUTIONS), {}).get('tried', False):
            if prepare_env(lib_name, lib_version, python_version):
                for execution in range(1, MAX_EXECUTIONS + 1):
                    
                    execution_data = executed[key].get(str(execution), {})
                    if execution_data.get('tried', False):
                        print(f"[INFO] {key} execution {execution} already tried. Skipping.")
                        continue
                    print(f"[INFO] Processing {key} execution {execution}...")

                    
                    

                    execution_data['tried'] = execution_data.get('tried', False)
                    execution_data['error'] = execution_data.get('error', False)
                    execution_data['tried'], execution_data['error'] = run_all_commands(lib_name, lib_version, execution_data, python_version, execution)
                    
                    executed[key][execution] = execution_data

                    if execution_data['error']:
                        break

                    save_executed(executed)
        else:
            print(f"[INFO] {key} finished. Skipping.")
            
    print(f"[OK] {key} execution recorded.")
elif len(sys.argv) == 5:
    lib_name = sys.argv[1]          # e.g. "pandas" or "polars"
    lib_version = str(parse(sys.argv[2]))       # e.g. "1.3.0"
    python_version = str(parse(sys.argv[3]))    # e.g. "3.8"
    execution = int(sys.argv[4])    # e.g. 1
    executed = load_executed()
    key = f"{lib_name}:{lib_version}"
    print(f"[INFO] Processing {key}...")
    executed[key] = executed.get(key, {})
    execution_data = executed[key].get(execution, {})
    execution_data['tried'] = execution_data.get('tried', False)
    execution_data['error'] = execution_data.get('error', False)
    execution_data['tried'], execution_data['error'] = run_all_commands(lib_name, lib_version, execution_data, python_version, execution)
    
    executed[key][execution] = execution_data
    save_executed(executed)
    print(f"[OK] {key} execution recorded.")
elif len(sys.argv) == 3:
    lib_name = sys.argv[1]          # e.g. "pandas" or "polars"
    lib_version = str(parse(sys.argv[2]))       # e.g. "1.3.0"
    key = f"{lib_name}:{lib_version}"
    print(f"[INFO] Processing {key}...")
    prepare_env(lib_name, lib_version, 3.12)
    execution_data = {}
    execution_data['tried'] = False
    execution_data['error'] = False
    execution_data['tried'], execution_data['error'] = run_all_commands(lib_name, lib_version, execution_data, 3.12, 0, True)
    print(f"[OK] {key} execution recorded.")