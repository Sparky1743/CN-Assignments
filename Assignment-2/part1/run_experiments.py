#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI

import os
import time
import subprocess
import argparse
import threading
from datetime import datetime

# Create result directories if they don't exist
def create_result_dirs():
    for exp in ['experiment_a', 'experiment_b', 'experiment_c', 'experiment_d_1', 'experiment_d_5']:
        result_dir = f'results/{exp}'
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
            print(f"Created directory: {result_dir}")

# Define topology for experiment A, B, D - basic dumbbell topology
class DumbbellTopo(Topo):
    def build(self, n=7):
        # Create switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # Create hosts on the left side
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')

        # Create hosts on the right side
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        h7 = self.addHost('h7')

        # Connect left hosts to s1 and s2
        self.addLink(h1, s1, bw=10)  # 10 Mbps
        self.addLink(h2, s1, bw=10)
        self.addLink(h3, s2, bw=10)
        self.addLink(h4, s2, bw=10)

        # Connect right hosts to s3 and s4
        self.addLink(h5, s3, bw=10)
        self.addLink(h6, s3, bw=10)
        self.addLink(h7, s4, bw=10)

        # Connect switches to form dumbbell
        self.addLink(s1, s3, bw=10)
        self.addLink(s2, s4, bw=10)

# Topology for experiment C (custom bandwidth scenarios)
class CustomBandwidthTopo(Topo):
    def build(self, scenario='c1'):
        # Create switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # Create hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        h7 = self.addHost('h7')

        # Connect hosts to switches
        self.addLink(h1, s1, bw=10)
        self.addLink(h2, s1, bw=10)
        self.addLink(h3, s2, bw=10)
        self.addLink(h4, s2, bw=10)
        self.addLink(h5, s3, bw=10)
        self.addLink(h6, s3, bw=10)
        self.addLink(h7, s4, bw=10)

        # Connect switches based on scenario
        if scenario == 'c1':
            # C-I: Only S2-S4 link active
            self.addLink(s2, s4, bw=10)
        else:
            # C-II: S1-S4 link active for a, b, c
            self.addLink(s1, s4, bw=10)

# Run tcpdump in background to capture packets
def start_tcpdump(node, interface, output_file):
    print(f"Starting tcpdump on {node.name}")
    return node.popen(f"tcpdump -i {interface} -w {output_file} tcp", shell=True)

# Run iperf3 client
def run_iperf_client(node, server_ip, output_file, duration=60, port=5001, start_delay=0):
    if start_delay > 0:
        print(f"Waiting {start_delay}s before starting {node.name}...")
        time.sleep(start_delay)
    
    print(f"Running iperf3 client on {node.name} connecting to {server_ip}")
    cmd = f"iperf3 -c {server_ip} -t {duration} -J -p {port} > {output_file} 2>&1"
    return node.cmd(cmd)

# Set TCP congestion control algorithm
def set_tcp_congestion_algorithm(net, algo):
    for host in net.hosts:
        host.cmd(f"sysctl -w net.ipv4.tcp_congestion_control={algo}")
    print(f"Set TCP congestion algorithm to {algo}")

# Run experiment A: Basic performance comparison
def run_experiment_a(net, congestion_algos, duration=60):
    print("\n=== Running Experiment A: Basic Performance Comparison ===\n")
    result_dir = 'results/experiment_a'
    
    for algo in congestion_algos:
        print(f"\nTesting congestion algorithm: {algo}")
        set_tcp_congestion_algorithm(net, algo)
        
        # Start server on h7
        h7 = net.get('h7')
        server_cmd = f"iperf3 -s -p 5001 &"
        h7.cmd(server_cmd)
        time.sleep(1)  # Give server time to start
        
        # Start tcpdump
        pcap_file = f"{result_dir}/h1_h7_{algo}.pcap"
        tcpdump_proc = start_tcpdump(h7, "h7-eth0", pcap_file)
        time.sleep(1)  # Give tcpdump time to start
        
        # Run iperf client
        h1 = net.get('h1')
        output_file = f"{result_dir}/h1_h7_{algo}.json"
        run_iperf_client(h1, h7.IP(), output_file, duration)
        
        # Stop tcpdump and server
        tcpdump_proc.terminate()
        h7.cmd("killall iperf3")
        time.sleep(1)
    
    print("Experiment A completed.")

# Run experiment B: Staggered clients
def run_experiment_b(net, congestion_algos):
    print("\n=== Running Experiment B: Staggered Clients ===\n")
    result_dir = 'results/experiment_b'
    
    # Clients will start at different times
    clients = [('h1', 0), ('h3', 15), ('h4', 30)]
    durations = [150, 120, 90]
    
    for algo in congestion_algos:
        print(f"\nTesting congestion algorithm: {algo}")
        set_tcp_congestion_algorithm(net, algo)
        
        # Start server on h7
        h7 = net.get('h7')
        server_cmd = f"iperf3 -s -p 5001 &"
        h7.cmd(server_cmd)
        time.sleep(1)  # Give server time to start
        
        # Start tcpdump
        pcap_file = f"{result_dir}/staggered_{algo}.pcap"
        tcpdump_proc = start_tcpdump(h7, "h7-eth0", pcap_file)
        time.sleep(1)  # Give tcpdump time to start
        
        # Start clients in separate threads
        threads = []
        for i, (client_name, delay) in enumerate(clients):
            client = net.get(client_name)
            output_file = f"{result_dir}/{client_name}_staggered_{algo}.json"
            
            thread = threading.Thread(
                target=run_iperf_client,
                args=(client, h7.IP(), output_file, durations[i], 5001, delay)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Stop tcpdump and server
        tcpdump_proc.terminate()
        h7.cmd("killall iperf3")
        time.sleep(1)
    
    print("Experiment B completed.")

# Run experiment C: Custom bandwidth scenarios
def run_experiment_c(congestion_algos):
    print("\n=== Running Experiment C: Custom Bandwidth Scenarios ===\n")
    result_dir = 'results/experiment_c'
    
    # Define the different parts of experiment C
    scenarios = {
        'c1': ['h3'],             # C-I: Only h3 can reach h7
        'c2a': ['h1', 'h2'],      # C-II-a: h1, h2 can reach h7
        'c2b': ['h1', 'h3'],      # C-II-b: h1, h3 can reach h7
        'c2c': ['h1', 'h3', 'h4'] # C-II-c: h1, h3, h4 can reach h7
    }
    
    for scenario, clients in scenarios.items():
        print(f"\nRunning scenario {scenario}...")
        
        # Create topology for this scenario
        topo = CustomBandwidthTopo(scenario=scenario)
        net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
        net.start()
        
        # Test with each congestion algorithm
        for algo in congestion_algos:
            print(f"Testing algorithm {algo} with scenario {scenario}")
            set_tcp_congestion_algorithm(net, algo)
            
            # Start server on h7
            h7 = net.get('h7')
            server_cmd = f"iperf3 -s -p 5001 &"
            h7.cmd(server_cmd)
            time.sleep(1)
            
            # Start tcpdump
            pcap_file = f"{result_dir}/{scenario}_{algo}.pcap"
            tcpdump_proc = start_tcpdump(h7, "h7-eth0", pcap_file)
            time.sleep(1)
            
            # Start all clients simultaneously
            threads = []
            for client_name in clients:
                client = net.get(client_name)
                output_file = f"{result_dir}/{client_name}_{scenario}_{algo}.json"
                
                thread = threading.Thread(
                    target=run_iperf_client,
                    args=(client, h7.IP(), output_file, 60, 5001, 0)
                )
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Stop tcpdump and server
            tcpdump_proc.terminate()
            h7.cmd("killall iperf3")
            time.sleep(1)
        
        net.stop()
    
    print("Experiment C completed.")

# Run experiment D: Packet loss scenarios
def run_experiment_d(net, congestion_algos, loss_rate):
    print(f"\n=== Running Experiment D: {loss_rate}% Packet Loss ===\n")
    result_dir = f'results/experiment_d_{loss_rate}'
    
    # Set up packet loss on the bottleneck link
    print(f"Setting {loss_rate}% packet loss on bottleneck links")
    net.configLinkStatus('s1', 's3', 'down')  # Turn off one link to force traffic through s2-s4
    s2, s4 = net.get('s2', 's4')
    
    # Apply loss to both directions on the link
    s2.cmdPrint(f"tc qdisc add dev s2-eth5 root netem loss {loss_rate}%")
    s4.cmdPrint(f"tc qdisc add dev s4-eth5 root netem loss {loss_rate}%")
    
    clients = ['h1', 'h3', 'h4']
    
    for algo in congestion_algos:
        print(f"\nTesting congestion algorithm: {algo} with {loss_rate}% loss")
        set_tcp_congestion_algorithm(net, algo)
        
        # Start server on h7
        h7 = net.get('h7')
        server_cmd = f"iperf3 -s -p 5001 &"
        h7.cmd(server_cmd)
        time.sleep(1)
        
        # Start tcpdump
        pcap_file = f"{result_dir}/d_{loss_rate}_{algo}.pcap"
        tcpdump_proc = start_tcpdump(h7, "h7-eth0", pcap_file)
        time.sleep(1)
        
        # Run clients in parallel
        threads = []
        for client_name in clients:
            client = net.get(client_name)
            output_file = f"{result_dir}/{client_name}_d_{loss_rate}_{algo}.json"
            
            thread = threading.Thread(
                target=run_iperf_client,
                args=(client, h7.IP(), output_file, 60)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Stop tcpdump and server
        tcpdump_proc.terminate()
        h7.cmd("killall iperf3")
        time.sleep(1)
    
    # Remove the packet loss settings
    s2.cmdPrint("tc qdisc del dev s2-eth5 root")
    s4.cmdPrint("tc qdisc del dev s4-eth5 root")
    net.configLinkStatus('s1', 's3', 'up')  # Restore original link
    
    print(f"Experiment D with {loss_rate}% loss completed.")

def main():
    parser = argparse.ArgumentParser(description='Run TCP congestion control experiments')
    parser.add_argument('--experiment', choices=['a', 'b', 'c', 'd1', 'd5', 'all'], default='all',
                      help='Experiment to run')
    
    args = parser.parse_args()
    experiment = args.experiment
    
    # Set Mininet log level
    setLogLevel('info')
    
    # Create result directories
    create_result_dirs()
    
    # Common congestion algorithms to test
    congestion_algos = ['cubic', 'vegas', 'htcp']
    
    # Run selected experiments
    if experiment in ['a', 'all', 'b', 'd1', 'd5']:
        # Create base topology for experiments A, B, D
        topo = DumbbellTopo()
        net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
        net.start()
        
        print("Starting network:")
        dumpNodeConnections(net.hosts)
        
        # Verify connectivity
        print("Verifying connectivity:")
        net.pingAll()
        
        # Run experiments
        if experiment in ['a', 'all']:
            run_experiment_a(net, congestion_algos)
        
        if experiment in ['b', 'all']:
            run_experiment_b(net, congestion_algos)
        
        if experiment in ['d1', 'all']:
            run_experiment_d(net, congestion_algos, 1)
        
        if experiment in ['d5', 'all']:
            run_experiment_d(net, congestion_algos, 5)
        
        net.stop()
    
    if experiment in ['c', 'all']:
        run_experiment_c(congestion_algos)
    
    print("\nAll requested experiments completed!")

if __name__ == '__main__':
    main()
