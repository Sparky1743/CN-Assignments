#!/bin/bash

# Make sure we're running as root (required for Mininet)
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   echo "Try: sudo ./run_all_simple.sh" 1>&2
   exit 1
fi

# Create results directory
mkdir -p results

# Ensure iperf3 is installed
if ! command -v iperf3 &> /dev/null; then
    echo "iperf3 not found, installing..."
    apt-get update && apt-get install -y iperf3
fi

# Make sure the scripts are executable
chmod +x run_experiments.py analyze_results.py

# This script uses the custom_topo.py file that has been modified to use Host instead of CPULimitedHost

# Run all experiments
echo "Running experiment a"
sudo python3 run_experiments.py --option=a
echo "analyze part a"
python3 analyze_results.py --experiment=a
echo "Running experiment b"
sudo python3 run_experiments.py --option=b
echo "analyze part b"
python3 analyze_results.py --experiment=b
echo "Running experiment c"
sudo python3 run_experiments.py --option=c
echo "analyze part c"
python3 analyze_results.py --experiment=c
echo "Running experiment d"
sudo python3 run_experiments.py --option=d
echo "analyze part d"
python3 analyze_results.py --experiment=d


# Analyze results
echo "===== Analyzing results ====="
python3 analyze_results.py --experiment=all

echo "===== All experiments completed ====="
echo "Results are available in the 'results' directory"
