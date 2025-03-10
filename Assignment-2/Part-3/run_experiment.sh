#!/bin/bash

# Make all Python scripts executable
chmod +x /home/srivamix/Downloads/Cn_task3/nagle.py
chmod +x /home/srivamix/Downloads/Cn_task3/server.py
chmod +x /home/srivamix/Downloads/Cn_task3/client.py
chmod +x /home/srivamix/Downloads/Cn_task3/experiment_runner.py

# Create results directory
mkdir -p /home/srivamix/Downloads/Cn_task3/tcp_results

echo "Starting experiment using the simplified nagle.py script..."
sudo python3 /home/srivamix/Downloads/Cn_task3/nagle.py

# Make results accessible to the user
sudo chown -R $USER:$USER /home/srivamix/Downloads/Cn_task3/tcp_results
