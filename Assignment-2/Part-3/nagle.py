#!/usr/bin/python

import os
import sys
import subprocess
import time

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        from mininet.topo import Topo
        from mininet.net import Mininet
        from mininet.link import TCLink
        print("✓ Mininet dependencies found")
    except ImportError:
        print("✗ Mininet not found. Please install Mininet.")
        print("  Run: sudo apt-get install mininet")
        return False
    
    # Check if files exist
    required_files = [
        "/home/srivamix/Downloads/Cn_task3/experiment_runner.py",
        "/home/srivamix/Downloads/Cn_task3/server.py",
        "/home/srivamix/Downloads/Cn_task3/client.py"
    ]
    
    for file in required_files:
        if not os.path.isfile(file):
            print(f"✗ Required file not found: {file}")
            return False
        else:
            print(f"✓ Found: {file}")
    
    return True

def ensure_permissions():
    """Ensure all scripts have execute permissions"""
    scripts = [
        "/home/srivamix/Downloads/Cn_task3/experiment_runner.py",
        "/home/srivamix/Downloads/Cn_task3/server.py",
        "/home/srivamix/Downloads/Cn_task3/client.py",
        "/home/srivamix/Downloads/Cn_task3/nagle.py"
    ]
    
    for script in scripts:
        os.system(f"chmod +x {script}")
    
    print("✓ Set execute permissions on all scripts")

def create_results_dir():
    """Create the results directory"""
    results_dir = "/home/srivamix/Downloads/Cn_task3/tcp_results"
    os.makedirs(results_dir, exist_ok=True)
    print(f"✓ Created results directory: {results_dir}")
    return results_dir

def run_experiment():
    """Run the experiment_runner.py script with sudo"""
    print("Starting TCP/IP performance analysis with Nagle's Algorithm...")
    print("This will run all four combinations of Nagle and Delayed-ACK configurations")
    print("The experiment will run for approximately 8-10 minutes")
    print("Please wait...")
    
    # Run script with sudo
    cmd = ["sudo", "python3", "/home/srivamix/Downloads/Cn_task3/experiment_runner.py"]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print("✗ Experiment failed. Check error messages above.")
        return False
    
    # Fix permissions on results
    results_dir = "/home/srivamix/Downloads/Cn_task3/tcp_results"
    os.system(f"sudo chown -R $USER:$USER {results_dir}")
    
    return True

def display_results():
    """Display the analysis results"""
    results_file = "/home/srivamix/Downloads/Cn_task3/tcp_results/analysis.txt"
    if os.path.isfile(results_file):
        with open(results_file, 'r') as f:
            print("\n" + "="*80)
            print("ANALYSIS RESULTS:")
            print("="*80)
            print(f.read())
    else:
        print("✗ Results file not found. The experiment may have failed.")

def main():
    print("=" * 80)
    print("TCP/IP Performance Analysis: Nagle's Algorithm and Delayed-ACK")
    print("=" * 80)
    
    if not check_dependencies():
        print("Please fix the dependencies and try again.")
        return
    
    ensure_permissions()
    create_results_dir()
    
    if run_experiment():
        display_results()

if __name__ == "__main__":
    main()
