#!/bin/bash

# Check if running as root
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   echo "Try: sudo ./install_requirements.sh" 1>&2
   exit 1
fi

echo "Installing required packages..."

# Install mininet if not already installed
if ! command -v mn &> /dev/null; then
    echo "Installing Mininet..."
    apt-get update
    apt-get install -y mininet
fi

# Install iperf3 and tcpdump
apt-get install -y iperf3 tcpdump python3-pip

# Install Python dependencies
pip3 install matplotlib numpy scapy

# Install optional tools for visualization
apt-get install -y wireshark tshark

# Make script files executable
chmod +x run_experiments.py analyze_results.py run_all.sh

echo "All requirements installed successfully!"
echo "You can now run experiments using: sudo ./run_all.sh"
