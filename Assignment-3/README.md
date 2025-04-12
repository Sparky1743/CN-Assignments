# Q1: Network Loops
## 1. Run the Topology

```bash
sudo python question1_network_topology.py
```

## 2. Testing Ping Commands (Part A)

```bash
mininet> h3 ping -c 3 h1
mininet> h5 ping -c 3 h7
mininet> h8 ping -c 3 h2
```

## 3. Fix Implementation (Part B)

```bash
# Enable STP on all switches
mininet> sh ovs-vsctl set bridge s1 stp_enable=true
mininet> sh ovs-vsctl set bridge s2 stp_enable=true
mininet> sh ovs-vsctl set bridge s3 stp_enable=true
mininet> sh ovs-vsctl set bridge s4 stp_enable=true

# Wait for STP to converge (approximately 30 seconds)
mininet> sh sleep 30

# Verify STP status
mininet> sh ovs-vsctl show
```

## 4. Testing After Fix (Part B)

```bash
mininet> h3 ping -c 3 h1
mininet> h5 ping -c 3 h7
mininet> h8 ping -c 3 h2
```

## 5. Cleanup

```bash
mininet> exit
$ sudo mn -c
```

# Q2:Configure Host-based NAT​
## Run the Topology

```bash
sudo python question2_network_topology.py
```

## Testing Instructions

### A. Internal to External Communication Tests

#### Test 1: Ping from h1 to h5
```bash
mininet> h1 ping -c 3 h5
```

#### Test 2: Ping from h2 to h3
```bash
mininet> h2 ping -c 3 h3
```

### B. External to Internal Communication Tests

#### Test 1: Ping from h8 to h1 (via NAT)
```bash
mininet> h8 ping -c 3 172.16.10.11
```

#### Test 2: Ping from h6 to h2 (via NAT)
```bash
mininet> h6 ping -c 3 172.16.10.12
```

### C. iperf3 Performance Tests

#### Test 1: h1 (Server) to h6 (Client)
```bash
# Start iperf3 server on h1
mininet> h1 iperf3 -s &

# Run client from h6 (repeat 3 times with 120s duration)
mininet> h6 iperf3 -c 172.16.10.11 -t 120
mininet> h6 iperf3 -c 172.16.10.11 -t 120
mininet> h6 iperf3 -c 172.16.10.11 -t 120
```

#### Test 2: h8 (Server) to h2 (Client)
```bash
# Start iperf3 server on h8
mininet> h8 iperf3 -s &

# Run client from h2 (repeat 3 times with 120s duration)
mininet> h2 iperf3 -c 10.0.0.9 -t 120
mininet> h2 iperf3 -c 10.0.0.9 -t 120
mininet> h2 iperf3 -c 10.0.0.9 -t 120
```

### D. Verify NAT Rules
```bash
mininet> h9 iptables -t nat -L PREROUTING -v -n
mininet> h9 iptables -t nat -L POSTROUTING -v -n
```


# Q3: Network Routing​

Our solution implements a distributed, asynchronous distance vector routing protocol for a network with 4 nodes (0-3).

## Network Topology

The network has the following direct connections and costs:
- Node 0 connected to Nodes 1, 2, and 3 with costs 1, 3, and 7 respectively
- Node 1 connected to Nodes 0 and 2 with costs 1 and 1 respectively
- Node 2 connected to Nodes 0, 1, and 3 with costs 3, 1, and 2 respectively
- Node 3 connected to Nodes 0 and 2 with costs 7 and 2 respectively

## Algorithm Implementation

Each node:
1. Initializes its distance table with direct costs to neighbors and infinity (999) for non-neighbors
2. Sends its initial distance vector to its neighbors
3. Upon receiving a distance vector from a neighbor:
   - Updates its distance table
   - Recalculates minimum costs to all destinations
   - If any minimum cost changes, sends updated distance vector to all neighbors

## Files

- `node0.c`, `node1.c`, `node2.c`, `node3.c`: Implementation of node-specific functions
- `distance_vector.c`: Main simulation environment (provided)

## Compilation

```bash
cc distance_vector.c node0.c node1.c node2.c node3.c -o distance_vector
```

## Execution

```bash
./distance_vector
```

When prompted, enter a trace value (recommended: 2 for detailed output).

## Expected Behavior

The simulation runs until the distance tables converge (no more packets in transit).
Final distance tables will show the minimum cost paths from each node to all other nodes.
