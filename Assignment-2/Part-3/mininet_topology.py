#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
import time

class SingleSwitchTopo(Topo):
    """Single switch connected to n hosts."""
    def build(self, n=2):
        switch = self.addSwitch('s1')
        # Add hosts and connect them to the switch
        for h in range(n):
            host = self.addHost(f'h{h+1}')
            self.addLink(host, switch, bw=1, delay='5ms')

def run_topology():
    """Create and test a simple network"""
    topo = SingleSwitchTopo(n=2)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()
    
    print("Dumping host connections")
    dumpNodeConnections(net.hosts)
    
    # Get hosts
    h1, h2 = net.get('h1'), net.get('h2')
    
    # Return network and hosts
    return net, h1, h2

if __name__ == '__main__':
    setLogLevel('info')
    net, client, server = run_topology()
    
    # Keep the network running until ctrl+c is pressed
    try:
        print("Network is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping network")
        net.stop()
