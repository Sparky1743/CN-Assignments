# TCP Congestion Control Comparison

This project compares three TCP congestion control algorithms (cubic, vegas, htcp) using Mininet.

## Requirements

- Ubuntu/Debian-based system with Python
- Mininet installed
- iperf3
- tcpdump
- Python packages: matplotlib, numpy, scapy

## Project Structure

- `custom_topo.py` - Defines the custom Mininet topology
- `run_experiments.py` - Main script to run all the experiments
- `analyze_results.py` - Processes the results and generates visualizations
- `run_all.sh` - Helper script to run everything in one go

## Experiments

The project contains four experiments:

1. **Experiment A**: Single client (H1) and server (H7)
2. **Experiment B**: Staggered clients (H1, H3, H4) connecting to server (H7)
3. **Experiment C**: Tests with custom bandwidth configurations
4. **Experiment D**: Tests with link loss rates (1% and 5%)

## How to Run

1. Make sure Mininet is installed on your system
2. Clone this repository

```bash
# Run everything (requires sudo)
sudo ./run_all.sh

# Or run individual experiments
sudo python run_experiments.py --option=a  # For experiment A
sudo python run_experiments.py --option=b  # For experiment B
sudo python run_experiments.py --option=c  # For experiment C
sudo python run_experiments.py --option=d  # For experiment D

# Analyze results separately
python analyze_results.py --experiment=all
```

## Output

The scripts will generate:
- JSON output files from iperf3
- PCAP packet capture files
- PNG graphs showing throughput over time and window sizes
- Summary text files with statistics for each algorithm

All output is stored in the `results` directory, organized by experiment.

## Congestion Control Algorithms

This project compares:
- **cubic**: Default TCP congestion control in most Linux distributions
- **vegas**: A delay-based congestion control algorithm
- **htcp**: Hamilton TCP, designed for high-speed, high-latency networks
