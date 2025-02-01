import socket
import time
from collections import defaultdict
import argparse
import dpkt 
import matplotlib.pyplot as plt

class PacketSniffer:
    def __init__(self):
        self.packet_count = 0
        self.start_time = None
        self.total_bytes = 0
        self.stats = defaultdict(int)
        self.packet_sizes = []
        self.src_dst_pairs = defaultdict(int)
        self.peak_pps = 0  
        self.peak_mbps = 0
        self.packets = []  # Store raw packet data for analysis

    def parse_packet(self, packet):
        # This function calculates the packet length
        packet_length = len(packet)
        self.packet_sizes.append(packet_length)
        
        try:
            eth = dpkt.ethernet.Ethernet(packet)
            if isinstance(eth.payload, dpkt.ip.IP):
                ip = eth.payload
                if isinstance(ip.payload, dpkt.tcp.TCP):
                    src_ip = ip.src
                    dst_ip = ip.dst
                    src_port = ip.payload.sport
                    dst_port = ip.payload.dport
                    self.src_dst_pairs[(src_ip, src_port, dst_ip, dst_port)] += packet_length
        except Exception as e:
            pass 

        return packet_length

    def packet_callback(self, packet, pcap_writer):
        if self.start_time is None:
            self.start_time = time.time()
        
        packet_length = self.parse_packet(packet)
        self.packet_count += 1
        self.total_bytes += packet_length
        
        # Store the raw packet for later analysis
        self.packets.append(packet)
        
        # Write the packet to pcap file
        timestamp = time.time()
        pcap_writer.writepkt(packet, ts=timestamp)

        # Calculate current metrics
        duration = time.time() - self.start_time
        pps = self.packet_count / duration
        mbps = (self.total_bytes * 8 / (1024 * 1024)) / duration
        
        # Update peak PPS and peak Mbps
        if pps > self.peak_pps:
            self.peak_pps = pps
        if mbps > self.peak_mbps:
            self.peak_mbps = mbps
        
        if int(duration) > len(self.stats):
            self.stats[int(duration)] = (pps, mbps)
            print(f"Current PPS: {pps:.2f}, Mbps: {mbps:.2f}")

    def start_sniffing(self, interface="eth0", duration=60, pcap_path=None):
        print(f"Starting packet capture on {interface} for {duration} seconds...")

        # Create a raw socket and bind it to the interface
        sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
        try:
            sock.bind((interface, 0))
            print(f"Successfully bound to {interface}")
        except Exception as e:
            print(f"Failed to bind to {interface}: {e}")
            return
        
        sock.settimeout(1)  # Timeout after 1 second if no packet is received

        # Open pcap file for writing
        if pcap_path:
            pcap_file = open(pcap_path, 'wb')
            pcap_writer = dpkt.pcap.Writer(pcap_file)
        else:
            pcap_writer = None

        start_time = time.time()
        try:
            while True:
                try:
                    packet = sock.recv(65535)
                    self.packet_callback(packet, pcap_writer)
                except socket.timeout:
                    print("No packets received in the last second, continuing...")

                if time.time() - start_time >= duration:
                    break

        except KeyboardInterrupt:
            print("\nCapture interrupted by user. Printing final statistics...")
            if self.packet_count == 0:
                print("No packet data found.")
                return

        # Print final statistics
        if self.start_time:
            total_duration = time.time() - self.start_time
            avg_pps = self.packet_count / total_duration
            avg_mbps = (self.total_bytes * 8 / (1024 * 1024)) / total_duration
            print(f"\nFinal Statistics:")
            print(f"Total Packets: {self.packet_count}")
            print(f"Total Bytes Transferred: {self.total_bytes} bytes")
            print(f"Average PPS: {avg_pps:.2f}")
            print(f"Average Mbps: {avg_mbps:.2f}")
            print(f"Total Duration: {total_duration:.2f} seconds")
            print(f"Peak PPS: {self.peak_pps:.2f}")
            print(f"Peak Mbps: {self.peak_mbps:.2f}")

        # Close pcap file
        if pcap_writer:
            pcap_file.close()

        # Further analysis options after capture
        self.loop_analysis_tasks(pcap_path)

    def loop_analysis_tasks(self, pcap_file_path):
        while True:
            print("\nPress 'a' to analyze packets, 'h' to make a histogram, 'u' for unique source-destination pairs, 'm' to analyze flows, or 'q' to quit.")
            choice = input("Enter your choice: ").strip()

            if choice == 'a':
                self.analyze_packets()
            elif choice == 'h':
                self.make_histogram()
            elif choice == 'u':
                self.unique_source_destination_pairs()
            elif choice == 'm':
                self.analyze_flows()
            elif choice == 'q':
                if pcap_file_path:
                    print(f"\nPCAP file saved at {pcap_file_path} for further analysis.")
                print("Exiting the program...")
                break  # Exit the loop if 'q' is pressed
            else:
                print("Invalid choice, please try again.")

    def analyze_packets(self):
        if not self.packet_sizes:
            print("No packet data to analyze.")
            return

        min_size = min(self.packet_sizes)
        max_size = max(self.packet_sizes)
        avg_size = sum(self.packet_sizes) / len(self.packet_sizes) if self.packet_sizes else 0
        print(f"\nTotal Packets: {self.packet_count}")
        print(f"Total Bytes Transferred: {self.total_bytes} bytes")
        print(f"Minimum Packet Size: {min_size} bytes")
        print(f"Maximum Packet Size: {max_size} bytes")
        print(f"Average Packet Size: {avg_size:.2f} bytes")

    def make_histogram(self):
        if not self.packet_sizes:
            print("No packet data to create histogram.")
            return

        # Plot and show histogram of packet sizes in a window
        plt.hist(self.packet_sizes, bins=50, color='blue', alpha=0.7)
        plt.title('Distribution of Packet Sizes')
        plt.xlabel('Packet Size (bytes)')
        plt.ylabel('Frequency')
        plt.show()

    def unique_source_destination_pairs(self):
        if not self.packet_sizes:
            print("No packet data to find pairs.")
            return
        
        unique_pairs = set()

        for packet in self.packets:
            try:
                # Parse the raw packet into an Ethernet frame
                eth = dpkt.ethernet.Ethernet(packet)
                if isinstance(eth.data, dpkt.ip.IP): 
                    ip = eth.data
                    src = socket.inet_ntoa(ip.src)
                    dst = socket.inet_ntoa(ip.dst)

                    if isinstance(ip.data, dpkt.tcp.TCP):
                        src += f":{ip.data.sport}"
                        dst += f":{ip.data.dport}"
                    elif isinstance(ip.data, dpkt.udp.UDP):
                        src += f":{ip.data.sport}"
                        dst += f":{ip.data.dport}"

                    unique_pairs.add((src, dst))
            except Exception as e:
                print(f"Error parsing packet: {e}")
                continue

        with open("unique_pairs.txt", "w") as file:
            file.write(f"Unique Source-Destination Pairs: {len(unique_pairs)}\n")
            for pair in unique_pairs:
                file.write(f"{pair}\n")
        print(f"Unique source-destination pairs written to part1_step2.txt")

    def analyze_flows(self):
        if not self.packet_sizes:
            print("No packet data to analyze flows.")
            return
        
        src_flows = defaultdict(int)
        dst_flows = defaultdict(int)
        flow_data = defaultdict(int)

        for packet in self.packets:
            try:
                eth = dpkt.ethernet.Ethernet(packet)
                if isinstance(eth.data, dpkt.ip.IP): 
                    ip = eth.data
                    src = socket.inet_ntoa(ip.src)
                    dst = socket.inet_ntoa(ip.dst)

                    if isinstance(ip.data, dpkt.tcp.TCP):
                        src += f":{ip.data.sport}"
                        dst += f":{ip.data.dport}"
                    elif isinstance(ip.data, dpkt.udp.UDP):
                        src += f":{ip.data.sport}"
                        dst += f":{ip.data.dport}"

                    src_flows[src] += 1
                    dst_flows[dst] += 1
                    flow_data[(src, dst)] += len(packet)
            except Exception as e:
                print(f"Error parsing packet: {e}")
                continue

        # Find the source-destination pair transferring the most data
        max_data_pair = max(flow_data, key=flow_data.get, default=None)
        max_data_transferred = flow_data[max_data_pair] if max_data_pair else 0

        with open("total_flows.txt", "w") as file:
            file.write("\nSource IP -> Total Flows:\n")
            for ip, flows in src_flows.items():
                file.write(f"{ip}: {flows}\n")

            file.write("\nDestination IP -> Total Flows:\n")
            for ip, flows in dst_flows.items():
                file.write(f"{ip}: {flows}\n")

            file.write("\nSource-Destination Pair Transferring the Most Data:\n")
            if max_data_pair:
                file.write(f"{max_data_pair}: {max_data_transferred} bytes\n")
        print(f"Flow analysis written to part1_step3.txt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Network Packet Sniffer')
    parser.add_argument('--interface', '-i', default='eth0', help='Interface to sniff on')
    parser.add_argument('--duration', '-d', type=int, default=60, help='Duration to sniff (seconds)')
    parser.add_argument('--pcap', '-p', required=True, help='Path to save the pcap file')
    args = parser.parse_args()

    sniffer = PacketSniffer()
    sniffer.start_sniffing(args.interface, args.duration, args.pcap)