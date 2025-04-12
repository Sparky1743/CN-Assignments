#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
import time

class NetworkTopology(Topo):
    def build(self):
        # Create switches
        pub_switches = []
        for i in range(1, 5):
            pub_switches.append(self.addSwitch(f's{i}', stp=True))
        
        priv_switch = self.addSwitch('s5')
        
        # Create public hosts (h3-h8)
        pub_hosts = []
        for i in range(3, 9):
            pub_hosts.append(self.addHost(f'h{i}', ip=f'10.0.0.{i+1}/24', defaultRoute='via 10.0.0.1'))
        
        # NAT Gateway
        gateway = self.addHost('h9', ip=None)
        
        # Private hosts
        priv_hosts = []
        for i in range(1, 3):
            priv_hosts.append(self.addHost(f'h{i}', ip=None))
        
        # Connect public switches in a ring topology with redundant link
        self.addLink(pub_switches[0], pub_switches[1], cls=TCLink, delay='7ms')
        self.addLink(pub_switches[1], pub_switches[2], cls=TCLink, delay='7ms')
        self.addLink(pub_switches[2], pub_switches[3], cls=TCLink, delay='7ms')
        self.addLink(pub_switches[3], pub_switches[0], cls=TCLink, delay='7ms')
        self.addLink(pub_switches[0], pub_switches[2], cls=TCLink, delay='7ms')
        
        # Connect public hosts to switches
        self.addLink(pub_hosts[0], pub_switches[1], cls=TCLink, delay='5ms')
        self.addLink(pub_hosts[1], pub_switches[1], cls=TCLink, delay='5ms')
        self.addLink(pub_hosts[2], pub_switches[2], cls=TCLink, delay='5ms')
        self.addLink(pub_hosts[3], pub_switches[2], cls=TCLink, delay='5ms')
        self.addLink(pub_hosts[4], pub_switches[3], cls=TCLink, delay='5ms')
        self.addLink(pub_hosts[5], pub_switches[3], cls=TCLink, delay='5ms')
        
        # Connect NAT gateway to both networks
        self.addLink(gateway, pub_switches[0], cls=TCLink, delay='5ms', intfName1='h9-eth0')
        self.addLink(gateway, priv_switch, cls=TCLink, delay='1ms', intfName1='h9-eth1')
        
        # Connect private hosts
        for host in priv_hosts:
            self.addLink(host, priv_switch, cls=TCLink, delay='1ms')


def setup_nat(net):
    # Get hosts
    private_hosts = [net.get('h1'), net.get('h2')]
    nat = net.get('h9')
    
    print("*** Setting up private hosts...")
    # Configure h1
    private_hosts[0].cmd("ifconfig h1-eth0 10.1.1.2/24 up")
    private_hosts[0].cmd("ip route add default via 10.1.1.1")
    
    # Configure h2
    private_hosts[1].cmd("ifconfig h2-eth0 10.1.1.3/24 up")
    private_hosts[1].cmd("ip route add default via 10.1.1.1")
    
    print("\n*** Configuring NAT Gateway...")
    # Public interface with aliases
    nat.cmd("ifconfig h9-eth0 10.0.0.1/24 up")
    nat.cmd("ip addr add 172.16.10.10/24 dev h9-eth0")
    nat.cmd("ip addr add 172.16.10.11/24 dev h9-eth0") 
    nat.cmd("ip addr add 172.16.10.12/24 dev h9-eth0")
    
    # Private interface
    nat.cmd("ifconfig h9-eth1 10.1.1.1/24 up")
    
    # Enable forwarding
    nat.cmd("sysctl -w net.ipv4.ip_forward=1")
    
    # Clear existing rules
    nat.cmd("iptables -F")
    nat.cmd("iptables -t nat -F")
    nat.cmd("iptables -X")
    nat.cmd("iptables -t nat -X")
    
    # Outbound NAT masquerading
    nat.cmd("iptables -t nat -A POSTROUTING -s 10.1.1.0/24 -o h9-eth0 -j MASQUERADE")
    
    # Inbound NAT (port forwarding)
    # ICMP mappings
    nat.cmd("iptables -t nat -A PREROUTING -i h9-eth0 -d 172.16.10.11 -p icmp -j DNAT --to-destination 10.1.1.2")
    nat.cmd("iptables -t nat -A PREROUTING -i h9-eth0 -d 172.16.10.12 -p icmp -j DNAT --to-destination 10.1.1.3")
    
    # iperf port mappings
    nat.cmd("iptables -t nat -A PREROUTING -i h9-eth0 -d 172.16.10.11 -p tcp --dport 5201 -j DNAT --to-destination 10.1.1.2:5201")
    nat.cmd("iptables -t nat -A PREROUTING -i h9-eth0 -d 172.16.10.12 -p tcp --dport 5201 -j DNAT --to-destination 10.1.1.3:5201")
    
    # Firewall rules
    # Allow outbound traffic
    nat.cmd("iptables -A FORWARD -i h9-eth1 -o h9-eth0 -s 10.1.1.0/24 -j ACCEPT")
    
    # Allow established/related inbound traffic
    nat.cmd("iptables -A FORWARD -i h9-eth0 -o h9-eth1 -m state --state RELATED,ESTABLISHED -j ACCEPT")
    
    # Allow specific forwarded traffic
    nat.cmd("iptables -A FORWARD -i h9-eth0 -o h9-eth1 -p icmp -d 10.1.1.2 -j ACCEPT")
    nat.cmd("iptables -A FORWARD -i h9-eth0 -o h9-eth1 -p icmp -d 10.1.1.3 -j ACCEPT")
    nat.cmd("iptables -A FORWARD -i h9-eth0 -o h9-eth1 -p tcp -d 10.1.1.2 --dport 5201 -j ACCEPT")
    nat.cmd("iptables -A FORWARD -i h9-eth0 -o h9-eth1 -p tcp -d 10.1.1.3 --dport 5201 -j ACCEPT")
    
    # Show configuration
    print("\n*** NAT rules:")
    print(nat.cmd("iptables -t nat -L -v -n"))
    print("\n*** Filter rules:")
    print(nat.cmd("iptables -L -v -n"))


def start_network():
    topology = NetworkTopology()
    network = Mininet(topo=topology, link=TCLink, switch=OVSBridge, controller=None)
    
    print("*** Starting network...")
    network.start()
    
    setup_nat(network)
    
    print("\n*** Waiting for network to stabilize...")
    time.sleep(15)
    
    print("\n*** Network ready")
    CLI(network)
    
    network.stop()


if __name__ == '__main__':
    setLogLevel('info')
    start_network()