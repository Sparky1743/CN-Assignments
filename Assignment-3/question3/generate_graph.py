import matplotlib.pyplot as plt
import re
import numpy as np

# Function to parse the simulation output
def parse_output(output_file):
    with open(output_file, 'r') as f:
        content = f.read()
    
    # Extract time and cost information
    updates = []
    
    # Look for rtupdate calls
    pattern = r"rtupdate(\d) called at time (\d+\.\d+).*?Updated distance table for node \d:(.*?)(?=MAIN|Distance vector|Simulator|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)
    
    for node, time, table in matches:
        node = int(node)
        time = float(time)
        
        # Extract costs from the table
        costs = {}
        if node == 0:
            # Extract minimum costs from node 0's table
            dest_pattern = r"dest (\d)\|.*?(\d+).*?(\d+).*?(\d+)"
            dest_matches = re.findall(dest_pattern, table)
            for dest, cost1, cost2, cost3 in dest_matches:
                costs[int(dest)] = min(int(cost1), int(cost2), int(cost3))
        
        updates.append((time, node, costs))
    
    return updates

# Track the evolution of costs over time
def track_cost_evolution(updates, from_node=0):
    # Initialize with high values
    cost_evolution = {dest: [] for dest in range(1, 4)}
    times = []
    
    for time, node, costs in sorted(updates):
        if node == from_node and costs:  # Only track node 0's updates
            times.append(time)
            for dest, cost in costs.items():
                if dest in cost_evolution:
                    cost_evolution[dest].append(cost)
    
    return times, cost_evolution

# Create the convergence graph
def create_convergence_graph(output_file, graph_file):
    updates = parse_output(output_file)
    times, cost_evolution = track_cost_evolution(updates)
    
    plt.figure(figsize=(10, 6))
    markers = ['o', 's', '^']
    
    for i, (dest, costs) in enumerate(cost_evolution.items()):
        if costs:
            plt.plot(times, costs, marker=markers[i], label=f'Node 0 to Node {dest}')
    
    plt.title('Distance Vector Algorithm Convergence')
    plt.xlabel('Simulation Time')
    plt.ylabel('Minimum Cost')
    plt.grid(True)
    plt.legend()
    plt.savefig(graph_file)
    plt.close()
    
    print(f"Convergence graph saved to {graph_file}")

# Example usage
if __name__ == "__main__":
    output_file = "simulation_output.txt"
    graph_file = "convergence_graph.png"
    create_convergence_graph(output_file, graph_file)
