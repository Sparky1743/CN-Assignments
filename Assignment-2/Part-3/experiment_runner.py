#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
import time
import json
import os
import subprocess

class SingleSwitchTopo(Topo):
    def build(self):
        # Add switch
        switch = self.addSwitch('s1')
        
        # Add hosts
        client = self.addHost('h1')
        server = self.addHost('h2')
        
        # Add links with rate limiting but without CPU limiting
        self.addLink(client, switch, bw=1, delay='5ms')
        self.addLink(server, switch, bw=1, delay='5ms')

def run_experiment():
    """Run all four combinations of Nagle and Delayed-ACK settings"""
    
    # Create results directory
    results_dir = "/home/srivamix/Downloads/Cn_task3/tcp_results"
    os.makedirs(results_dir, exist_ok=True)
    
    # Test configurations
    configurations = [
        {"nagle": 1, "delayed_ack": 1, "name": "nagle_on_delack_on"},
        {"nagle": 1, "delayed_ack": 0, "name": "nagle_on_delack_off"},
        {"nagle": 0, "delayed_ack": 1, "name": "nagle_off_delack_on"},
        {"nagle": 0, "delayed_ack": 0, "name": "nagle_off_delack_off"}
    ]
    
    # Parameters
    transfer_rate = 40  # bytes/second
    duration = 120      # seconds
    
    # Start Mininet - using regular hosts instead of CPULimitedHost
    topo = SingleSwitchTopo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()
    
    # Get hosts
    client = net.get('h1')
    server = net.get('h2')
    
    print("Network topology:")
    dumpNodeConnections(net.hosts)
    
    results = {}
    
    try:
        # Create test file
        client.cmd(f'python3 -c "import os; open(\'/tmp/test_file.bin\', \'wb\').write(os.urandom(4096))"')
        
        for config in configurations:
            print(f"\n\nRunning configuration: {config['name']}")
            print(f"Nagle's Algorithm: {'Enabled' if config['nagle'] else 'Disabled'}")
            print(f"Delayed ACK: {'Enabled' if config['delayed_ack'] else 'Disabled'}")
            
            # Start server in background
            server_cmd = f'python3 /home/srivamix/Downloads/Cn_task3/server.py --port 5000 --nagle {config["nagle"]} --delayed-ack {config["delayed_ack"]} > /tmp/server_output.txt 2>&1 &'
            print(f"Running server command: {server_cmd}")
            server.cmd(server_cmd)
            time.sleep(2)  # Give server more time to start
            
            # Run client
            client_cmd = f'python3 /home/srivamix/Downloads/Cn_task3/client.py --server {server.IP()} --port 5000 --rate {transfer_rate} --duration {duration} --nagle {config["nagle"]} --delayed-ack {config["delayed_ack"]}'
            print(f"Running client command: {client_cmd}")
            output = client.cmd(client_cmd)
            
            print(output)
            
            # Save results
            results[config['name']] = parse_client_output(output)
            
            # Kill server
            server.cmd('pkill -f "python3 /home/srivamix/Downloads/Cn_task3/server.py"')
            time.sleep(2)  # Give server more time to shut down
    
    except Exception as e:
        print(f"Error during experiment: {e}")
    finally:
        # Stop Mininet
        net.stop()
        
    # Save results to file
    with open(f"{results_dir}/results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nExperiment completed. Results saved to {results_dir}/results.json")
    
    # Generate analysis
    generate_analysis(results, results_dir)

def parse_client_output(output):
    """Parse client output to extract metrics"""
    metrics = {}
    
    lines = output.strip().split('\n')
    for line in lines:
        if "Throughput:" in line:
            try:
                metrics['throughput'] = float(line.split(':')[1].strip().split()[0])
            except (IndexError, ValueError):
                metrics['throughput'] = 0
        elif "Goodput:" in line:
            try:
                metrics['goodput'] = float(line.split(':')[1].strip().split()[0])
            except (IndexError, ValueError):
                metrics['goodput'] = 0
        elif "Packet loss rate:" in line:
            try:
                # Convert percentage to float
                metrics['packet_loss_rate'] = float(line.split(':')[1].strip().rstrip('%')) / 100
            except (IndexError, ValueError):
                metrics['packet_loss_rate'] = 0
        elif "Bytes sent:" in line:
            try:
                metrics['bytes_sent'] = int(line.split(':')[1].strip())
            except (IndexError, ValueError):
                metrics['bytes_sent'] = 0
        elif "Packets sent:" in line:
            try:
                metrics['packets_sent'] = int(line.split(':')[1].strip())
                if metrics.get('packets_sent', 0) > 0:
                    metrics['avg_packet_size'] = metrics.get('bytes_sent', 0) / metrics['packets_sent']
                else:
                    metrics['avg_packet_size'] = 0
            except (IndexError, ValueError):
                metrics['packets_sent'] = 0
                metrics['avg_packet_size'] = 0
    
    return metrics

def generate_analysis(results, results_dir):
    """Generate analysis of the results"""
    with open(f"{results_dir}/analysis.txt", 'w') as f:
        f.write("=== TCP Performance Analysis: Nagle's Algorithm and Delayed-ACK ===\n\n")
        
        # Print table of results
        f.write(f"{'Configuration':<25} {'Throughput (B/s)':<20} {'Goodput (B/s)':<20} {'Packet Loss Rate':<20} {'Avg Packet Size (B)':<20}\n")
        f.write("-" * 105 + "\n")
        
        for config, metrics in results.items():
            f.write(f"{config:<25} {metrics.get('throughput', 0):<20.2f} {metrics.get('goodput', 0):<20.2f} {metrics.get('packet_loss_rate', 0):<20.2%} {metrics.get('avg_packet_size', 0):<20.2f}\n")
        
        f.write("\n\n=== Analysis and Observations ===\n\n")
        
        # Compare Nagle on vs off
        nagle_on = {k: v for k, v in results.items() if 'nagle_on' in k}
        nagle_off = {k: v for k, v in results.items() if 'nagle_off' in k}
        
        avg_throughput_nagle_on = sum(v.get('throughput', 0) for v in nagle_on.values()) / len(nagle_on) if nagle_on else 0
        avg_throughput_nagle_off = sum(v.get('throughput', 0) for v in nagle_off.values()) / len(nagle_off) if nagle_off else 0
        
        f.write(f"1. Effect of Nagle's Algorithm:\n")
        f.write(f"   - Average throughput with Nagle on: {avg_throughput_nagle_on:.2f} B/s\n")
        f.write(f"   - Average throughput with Nagle off: {avg_throughput_nagle_off:.2f} B/s\n")
        f.write(f"   - Nagle's algorithm {'increases' if avg_throughput_nagle_on > avg_throughput_nagle_off else 'decreases'} throughput by {abs(avg_throughput_nagle_on - avg_throughput_nagle_off):.2f} B/s ({abs(avg_throughput_nagle_on - avg_throughput_nagle_off) / max(avg_throughput_nagle_off, 0.001):.2%})\n\n")
        
        # Compare DelACK on vs off
        delack_on = {k: v for k, v in results.items() if 'delack_on' in k}
        delack_off = {k: v for k, v in results.items() if 'delack_off' in k}
        
        avg_throughput_delack_on = sum(v.get('throughput', 0) for v in delack_on.values()) / len(delack_on) if delack_on else 0
        avg_throughput_delack_off = sum(v.get('throughput', 0) for v in delack_off.values()) / len(delack_off) if delack_off else 0
        
        f.write(f"2. Effect of Delayed ACK:\n")
        f.write(f"   - Average throughput with Delayed ACK on: {avg_throughput_delack_on:.2f} B/s\n")
        f.write(f"   - Average throughput with Delayed ACK off: {avg_throughput_delack_off:.2f} B/s\n")
        f.write(f"   - Delayed ACK {'increases' if avg_throughput_delack_on > avg_throughput_delack_off else 'decreases'} throughput by {abs(avg_throughput_delack_on - avg_throughput_delack_off):.2f} B/s ({abs(avg_throughput_delack_on - avg_throughput_delack_off) / max(avg_throughput_delack_off, 0.001):.2%})\n\n")
        
        # Find the best configuration
        best_config = max(results.items(), key=lambda x: x[1].get('goodput', 0))
        f.write(f"3. Best Configuration:\n")
        f.write(f"   - {best_config[0]} provides the highest goodput at {best_config[1].get('goodput', 0):.2f} B/s\n\n")
        
        # Theoretical explanation
        f.write("4. Explanation of Observations:\n")
        f.write("   - Nagle's Algorithm aims to reduce the number of small packets by buffering data until either a full-sized packet can be sent or an ACK is received.\n")
        f.write("   - Delayed ACK reduces the number of ACKs by delaying them, which can cause Nagle's algorithm to wait unnecessarily.\n")
        f.write("   - When both are enabled, they can create a 'lock-step' behavior where each is waiting for the other.\n")
        f.write("   - Disabling both typically gives the best interactive performance but may increase network overhead.\n\n")
        
        f.write("5. Recommendations:\n")
        f.write("   - For bulk transfers: Nagle on, Delayed ACK on - Reduces overhead, maximizes efficiency\n")
        f.write("   - For interactive applications: Nagle off, Delayed ACK off - Minimizes latency\n")
        f.write("   - For mixed workloads: Nagle off, Delayed ACK on - Good compromise\n")
        
    print(f"Analysis generated and saved to {results_dir}/analysis.txt")

if __name__ == '__main__':
    setLogLevel('info')
    run_experiment()
