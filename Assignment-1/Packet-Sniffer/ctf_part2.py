from scapy.all import *

packets = rdpcap('capture.pcap')

# Q1. Find the IP address in a TCP packet containing the message "<my ip address = >"
def find_my_ip_address(packets):
    for packet in packets:
        if packet.haslayer(TCP) and packet.haslayer(Raw):
            payload = packet[Raw].load.decode(errors='ignore')
            if "ip address" in payload:
                # Extract the IP address from the payload
                start_index = payload.find("ip address =") + len("ip address =")
                end_index = payload.find(">", start_index)  # Find the closing '>'
                ip_address = payload[start_index:end_index].strip()
                return ip_address[1:]
    return None

# Q2. Find the number of packets with that IP address
def count_packets_with_ip(packets, ip_address):
    count = 0
    for packet in packets:
        if packet.haslayer(IP):
            if packet[IP].src == ip_address or packet[IP].dst == ip_address:
                count += 1
    return count

def find_laptop_name_and_checksum(packets):
    for packet in packets:
        if packet.haslayer(TCP) and packet.haslayer(Raw):
            payload = packet[Raw].load.decode(errors='ignore')

            index = payload.find("name of laptop")
            if index != -1: 
                next_chars = payload[index + len("laptop"): index + len("laptop") + 30]

                tcp_checksum = packet[TCP].chksum
                return next_chars, tcp_checksum

    return None, None


# Q4. Find the number of packets containing the message "Order successful"
def count_order_successful_packets(packets):
    count = 0
    for packet in packets:
        if packet.haslayer(Raw):
            payload = packet[Raw].load.decode(errors='ignore')
            if "Order Successful" in payload:
                count += 1
    return count

# Results
my_ip_address = find_my_ip_address(packets)
print(f"Q1. My IP address: {my_ip_address}")

if my_ip_address:
    packet_count = count_packets_with_ip(packets, my_ip_address)
    print(f"Q2. Number of packets with IP {my_ip_address}: {packet_count}")

laptop_name, tcp_checksum = find_laptop_name_and_checksum(packets)
if laptop_name:
    print(f"Q3a. {laptop_name[2:]}")
    print(f"Q3b. TCP checksum of that packet: {tcp_checksum}")

order_successful_count = count_order_successful_packets(packets)
print(f"Q4. Number of packets with 'Order successful': {order_successful_count}")