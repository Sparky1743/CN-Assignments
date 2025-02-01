from scapy.all import *

# Load the pcap file
packets = rdpcap('capture.pcap')

# Q1. Find the IP address in a TCP packet containing the message "<my ip address = >"
def find_my_ip_address(packets):
    for packet in packets:
        if packet.haslayer(TCP) and packet.haslayer(Raw):
            payload = packet[Raw].load.decode(errors='ignore')
            if "ip address" in payload:
                print("hello")
                # Extract the IP address from the payload
                start_index = payload.find("ip address =") + len("ip address =")
                end_index = payload.find(">", start_index)  # Find the closing '>'
                ip_address = payload[start_index:end_index].strip()
                return ip_address
    return None

# Q2. Find the number of packets with that IP address
def count_packets_with_ip(packets, ip_address):
    count = 0
    for packet in packets:
        if packet.haslayer(IP):
            if packet[IP].src == ip_address or packet[IP].dst == ip_address:
                count += 1
    return count

# Q3. Find the name of the laptop and the TCP checksum of that packet
def find_laptop_name_and_checksum(packets):
    for packet in packets:
        if packet.haslayer(TCP) and packet.haslayer(Raw):
            payload = packet[Raw].load.decode(errors='ignore')
            if "laptop" in payload:  # Assuming the laptop name is prefixed with "laptop"
                # Extract the laptop name
                laptop_name = payload.split("laptop")[1].split()[0]  # Get the first word after "laptop"
                tcp_checksum = packet[TCP].chksum
                return laptop_name, tcp_checksum
    return None, None

# Q4. Find the number of packets containing the message "Order successful"
def count_order_successful_packets(packets):
    count = 0
    for packet in packets:
        if packet.haslayer(Raw):
            payload = packet[Raw].load.decode(errors='ignore')
            if "Order successful" in payload:
                count += 1
    return count

# Solve the questions
# Q1
my_ip_address = find_my_ip_address(packets)
print(f"Q1. My IP address: {my_ip_address}")

# Q2
if my_ip_address:
    packet_count = count_packets_with_ip(packets, my_ip_address)
    print(f"Q2. Number of packets with IP {my_ip_address}: {packet_count}")

# Q3
laptop_name, tcp_checksum = find_laptop_name_and_checksum(packets)
if laptop_name:
    print(f"Q3a. Laptop name: {laptop_name}")
    print(f"Q3b. TCP checksum of that packet: {tcp_checksum}")

# Q4
order_successful_count = count_order_successful_packets(packets)
print(f"Q4. Number of packets with 'Order successful': {order_successful_count}")