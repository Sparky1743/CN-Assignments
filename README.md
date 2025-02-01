# Python Packet Sniffer

A Python-based network packet sniffer that captures and analyzes network traffic. This tool leverages the `dpkt` library for packet parsing and `matplotlib` for visualizing packet size distributions.

## Features

- **Packet Capture**: Real-time packet capture from specified network interfaces
- **Protocol Analysis**: Comprehensive parsing of Ethernet, IP, TCP, and UDP headers
- **Network Statistics**: 
  - Packet count and total bytes transferred
  - Real-time packets per second (PPS)
  - Bandwidth utilization in Mbps
  - Unique source-destination pair identification
  - Network flow analysis with data transfer metrics
- **Visualization**: Dynamic histogram generation of packet size distributions
- **Interactive Analysis**: Post-capture analysis mode with multiple options:
  - `a`: Analyze captured packets
  - `h`: Generate packet size histogram
  - `u`: List unique source-destination pairs
  - `m`: Analyze network flows
  - `q`: Exit
- **Flexible Capture Control**: Stop capture anytime using Ctrl+C

## Requirements

- Python 3.x
- Required libraries:
  ```bash
  pip install dpkt matplotlib
  ```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Sparky1743/CN-Assignments
   cd Computer-Networks/Packet-Sniffer/
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the packet sniffer using the following command structure:

```bash
sudo python python_sniffer.py --interface <interface> --duration <duration> --pcap <pcap_file>
```

### Command Line Arguments

- `--interface` or `-i`: Network interface to capture from (default: eth0)
- `--duration` or `-d`: Capture duration in seconds (default: 60)
- `--pcap` or `-p`: Output path for captured packets in PCAP format

### Example

```bash
sudo python python_sniffer.py --interface eth0 --duration 1000 --pcap capture.pcap
```

### Sample Output

```
Starting packet capture on eth0 for 1000 seconds...
Successfully bound to eth0
Current PPS: 10000.17, Mbps: 34.04
...
Final Statistics:
Total Packets: 805844
Total Bytes Transferred: 364554242 bytes
Average PPS: 8293.81
Average Mbps: 28.63
Total Duration: 97.16 seconds
Peak PPS: 14388.69
Peak Mbps: 166.20
```

## Interactive Analysis Mode

After capture completion or when stopped with Ctrl+C, the tool enters interactive analysis mode:

1. Press `a` to view detailed packet analysis
2. Press `h` to generate packet size distribution histogram
3. Press `u` to view unique source-destination pairs
4. Press `m` to analyze network flows
5. Press `q` to exit analysis mode
