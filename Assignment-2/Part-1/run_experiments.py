#!/usr/bin/env python

import os
import time
import subprocess
import argparse
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from custom_topo import setup_network

# Define congestion control algorithms
CONGESTION_ALGOS = ['cubic', 'vegas', 'htcp']

def start_capture(net, host, output_file):
    """Start tcpdump on a host"""
    # Make sure the directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    cmd = f'tcpdump -i {host.defaultIntf().name} -w {output_file} tcp &'
    host.cmd(cmd)
    return host.lastPid  # Corrected from lastPID to lastPid

def stop_capture(host, pid):
    """Stop tcpdump on a host"""
    host.cmd(f'kill -9 {pid}')
    time.sleep(1)  # Give time for the process to terminate

def run_server(server_host, port=5201):
    """Run iperf3 server"""
    cmd = f'iperf3 -s -p {port} -D'  # Run in daemon mode
    server_host.cmd(cmd)
    info(f'*** Server started on {server_host.name} port {port}\n')
    time.sleep(1)  # Wait for server to start

def run_client(client_host, server_ip, port=5201, bw='10M', parallel=10, duration=150, cong_ctrl='cubic'):
    """Run iperf3 client"""
    output_file = f'iperf3_{client_host.name}_to_h7_{cong_ctrl}.json'
    cmd = f'iperf3 -c {server_ip} -p {port} -b {bw} -P {parallel} -t {duration} -C {cong_ctrl} -J > {output_file}'
    info(f'*** Running client on {client_host.name} with {cong_ctrl}\n')
    client_host.cmd(cmd)
    return output_file



# Run  the  client  on  H1  and  the  server  on  H7.  Measure  the  below  parameters  and 
# summarize the observations for the three congestion schemes as applicable.  
# 1. Throughput over time (with valid Wireshark I/O graphs)  
# 2. Goodput 
# 3. Packet loss rate 
# 4. Maximum window size achieved (with valid Wireshark I/O graphs). 

def experiment_a(net):
    """Run experiment A: H1 -> H7 with different congestion control algorithms"""
    info('*** Running Experiment A\n')
    
    h1, h7 = net.get('h1', 'h7')
    server_ip = h7.IP()
    
    for algo in CONGESTION_ALGOS:
        info(f'*** Starting experiment with {algo}\n')
        
        # Ensure output directory exists
        os.makedirs('results/experiment_a', exist_ok=True)
        
        # Start capture
        pcap_file = f'results/experiment_a/h1_h7_{algo}.pcap'
        capture_pid = start_capture(net, h7, pcap_file)
        
        # Start server
        run_server(h7)
        
        # Run client
        output_file = run_client(h1, server_ip, cong_ctrl=algo)
        
        # Stop capture
        stop_capture(h7, capture_pid)
        
        # Move output file to results directory
        os.system(f'mv {output_file} results/experiment_a/')
        
        # Clean up
        h7.cmd('pkill -9 iperf3')
        time.sleep(2)  # Wait for cleanup

def experiment_b(net):
    """Run experiment B: Staggered clients H1, H3, H4 -> H7"""
    info('*** Running Experiment B\n')
    
    h1, h3, h4, h7 = net.get('h1', 'h3', 'h4', 'h7')
    server_ip = h7.IP()
    
    for algo in CONGESTION_ALGOS:
        info(f'*** Starting experiment with {algo}\n')
        
        # Ensure output directory exists
        os.makedirs('results/experiment_b', exist_ok=True)
        
        # Start capture
        pcap_file = f'results/experiment_b/staggered_{algo}.pcap'
        capture_pid = start_capture(net, h7, pcap_file)
        
        # Start server
        run_server(h7)
        
        # Start H1 client at T=0s for 150s
        h1.cmd(f'iperf3 -c {server_ip} -p 5201 -b 10M -P 10 -t 150 -C {algo} -J > results/experiment_b/h1_staggered_{algo}.json &')
        
        # Start H3 client at T=15s for 120s
        time.sleep(15)
        h3.cmd(f'iperf3 -c {server_ip} -p 5201 -b 10M -P 10 -t 120 -C {algo} -J > results/experiment_b/h3_staggered_{algo}.json &')
        
        # Start H4 client at T=30s for 90s
        time.sleep(15)
        h4.cmd(f'iperf3 -c {server_ip} -p 5201 -b 10M -P 10 -t 90 -C {algo} -J > results/experiment_b/h4_staggered_{algo}.json &')
        
        # Wait for all experiments to finish
        time.sleep(120)  # Total wait = 15 + 15 + 120 = 150s
        
        # Stop capture
        stop_capture(h7, capture_pid)
        
        # Clean up
        h7.cmd('pkill -9 iperf3')
        time.sleep(2)  # Wait for cleanup

# c.  Configure the links with the following bandwidths: 
# I.  Link S1-S2: 100Mbps 
# II.  Links S2-S3: 50Mbps 
# III.  Links S3-S4: 100Mbps 
#             Measure the performance parameters listed in part (a) and explain the observations in 
# the following conditions: 
# 1.  Link S2-S4 is active with client on H3 and server on H7. 
# 2.  Link S1-S4 is active with: 
# a.  Running client on H1 and H2 and server on H7 
# b.  Running client on H1 and H3 and server on H7 
# c.  Running client on H1, H3 and H4 and server on H7

def experiment_c(net):
    """Run experiment C with custom bandwidths"""
    info('*** Running Experiment C\n')
    
    # Get hosts
    h1, h2, h3, h4, h7 = net.get('h1', 'h2', 'h3', 'h4', 'h7')
    server_ip = h7.IP()
    
    # Create results directory
    os.makedirs('results/experiment_c', exist_ok=True)
    
    # Configure link bandwidths (already done in topology setup)
    
    for algo in CONGESTION_ALGOS:
        info(f'*** Starting experiment C with {algo}\n')
        
        # C-I: Link S2-S4 active (H3 -> H7)
        pcap_file = f'results/experiment_c/c1_{algo}.pcap'
        capture_pid = start_capture(net, h7, pcap_file)
        run_server(h7)
        run_client(h3, server_ip, cong_ctrl=algo)
        stop_capture(h7, capture_pid)
        h7.cmd('pkill -9 iperf3')
        time.sleep(2)
        
        # C-II-a: Link S1-S4 active (H1,H2 -> H7)
        pcap_file = f'results/experiment_c/c2a_{algo}.pcap'
        capture_pid = start_capture(net, h7, pcap_file)
        run_server(h7)
        # Start both clients
        h1.cmd(f'iperf3 -c {server_ip} -p 5201 -b 10M -P 10 -t 150 -C {algo} -J > results/experiment_c/h1_c2a_{algo}.json &')
        h2.cmd(f'iperf3 -c {server_ip} -p 5201 -b 10M -P 10 -t 150 -C {algo} -J > results/experiment_c/h2_c2a_{algo}.json &')
        time.sleep(150)  # Wait for test to complete
        stop_capture(h7, capture_pid)
        h7.cmd('pkill -9 iperf3')
        time.sleep(2)
        
        # C-II-b: Link S1-S4 active (H1,H3 -> H7)
        pcap_file = f'results/experiment_c/c2b_{algo}.pcap'
        capture_pid = start_capture(net, h7, pcap_file)
        run_server(h7)
        # Start both clients
        h1.cmd(f'iperf3 -c {server_ip} -p 5201 -b 10M -P 10 -t 150 -C {algo} -J > results/experiment_c/h1_c2b_{algo}.json &')
        h3.cmd(f'iperf3 -c {server_ip} -p 5201 -b 10M -P 10 -t 150 -C {algo} -J > results/experiment_c/h3_c2b_{algo}.json &')
        time.sleep(150)  # Wait for test to complete
        stop_capture(h7, capture_pid)
        h7.cmd('pkill -9 iperf3')
        time.sleep(2)
        
        # C-II-c: Link S1-S4 active (H1,H3,H4 -> H7)
        pcap_file = f'results/experiment_c/c2c_{algo}.pcap'
        capture_pid = start_capture(net, h7, pcap_file)
        run_server(h7)
        # Start all clients
        h1.cmd(f'iperf3 -c {server_ip} -p 5201 -b 10M -P 10 -t 150 -C {algo} -J > results/experiment_c/h1_c2c_{algo}.json &')
        h3.cmd(f'iperf3 -c {server_ip} -p 5201 -b 10M -P 10 -t 150 -C {algo} -J > results/experiment_c/h3_c2c_{algo}.json &')
        h4.cmd(f'iperf3 -c {server_ip} -p 5201 -b 10M -P 10 -t 150 -C {algo} -J > results/experiment_c/h4_c2c_{algo}.json &')
        time.sleep(150)  # Wait for test to complete
        stop_capture(h7, capture_pid)
        h7.cmd('pkill -9 iperf3')
        time.sleep(2)

def experiment_d(net, loss_rate):
    """Run experiment D with link loss"""
    info(f'*** Running Experiment D with {loss_rate}% packet loss\n')
    
    # Get hosts
    h1, h3, h4, h7 = net.get('h1', 'h3', 'h4', 'h7')
    server_ip = h7.IP()
    
    # Create results directory
    os.makedirs(f'results/experiment_d_{loss_rate}', exist_ok=True)
    
    for algo in CONGESTION_ALGOS:
        info(f'*** Starting experiment D with {algo} and {loss_rate}% loss\n')
        
        # Run clients as in experiment_c part C-II-c but with link loss
        pcap_file = f'results/experiment_d_{loss_rate}/d_{loss_rate}_{algo}.pcap'
        capture_pid = start_capture(net, h7, pcap_file)
        run_server(h7)
        
        # Start all clients
        h1.cmd(f'iperf3 -c {server_ip} -p 5201 -b 10M -P 10 -t 150 -C {algo} -J > results/experiment_d_{loss_rate}/h1_d_{loss_rate}_{algo}.json &')
        h3.cmd(f'iperf3 -c {server_ip} -p 5201 -b 10M -P 10 -t 150 -C {algo} -J > results/experiment_d_{loss_rate}/h3_d_{loss_rate}_{algo}.json &')
        h4.cmd(f'iperf3 -c {server_ip} -p 5201 -b 10M -P 10 -t 150 -C {algo} -J > results/experiment_d_{loss_rate}/h4_d_{loss_rate}_{algo}.json &')
        
        time.sleep(150)  # Wait for test to complete
        stop_capture(h7, capture_pid)
        h7.cmd('pkill -9 iperf3')
        time.sleep(2)

def main():
    """Main function to run all experiments"""
    parser = argparse.ArgumentParser(description='Run TCP congestion control experiments')
    parser.add_argument('--option', choices=['a', 'b', 'c', 'd', 'all'], default='all',
                      help='Experiment option to run (a, b, c, d, or all)')
    
    args = parser.parse_args()
    option = args.option
    
    # Create results directory
    os.makedirs('results', exist_ok=True)
    
    # Set log level
    setLogLevel('info')
    
    if option in ['a', 'b', 'all']:
        # Standard network for experiments A and B
        net = setup_network()
        net.start()
        
        if option == 'a' or option == 'all':
            experiment_a(net)
        
        if option == 'b' or option == 'all':
            experiment_b(net)
        
        net.stop()
    
    if option in ['c', 'all']:
        # Custom bandwidth network for experiment C
        net = setup_network(bandwidth_s1_s2=100, bandwidth_s2_s3=50, bandwidth_s3_s4=100)
        net.start()
        experiment_c(net)
        net.stop()
    
    if option in ['d', 'all']:
        # 1% loss network for experiment D
        net = setup_network(bandwidth_s1_s2=100, bandwidth_s2_s3=50, bandwidth_s3_s4=100, loss_s2_s3=1)
        net.start()
        experiment_d(net, 1)
        net.stop()
        
        # 5% loss network for experiment D
        net = setup_network(bandwidth_s1_s2=100, bandwidth_s2_s3=50, bandwidth_s3_s4=100, loss_s2_s3=5)
        net.start()
        experiment_d(net, 5)
        net.stop()
    
    info('*** All experiments completed\n')

if __name__ == '__main__':
    main()