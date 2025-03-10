import pyshark
import matplotlib.pyplot as plt
import datetime
import numpy as np
from concurrent.futures import ThreadPoolExecutor

pcap_file = 'client_traffic.pcap'

connection_start_times = {}
connection_durations = {}
packet_colors = {}

syn_only_connections = 0
completed_connections = 0
ignored_packets = 0

MAX_PACKET_SIZE = 1500  

def process_packet(packet):
    global ignored_packets, completed_connections

    try:
        if 'TCP' not in packet or not hasattr(packet, 'length') or int(packet.length) > MAX_PACKET_SIZE:
            ignored_packets += 1
            return

        src_ip = packet.ip.src
        dest_ip = packet.ip.dst
        src_port = packet.tcp.srcport
        dest_port = packet.tcp.dstport
        tcp_flags = int(packet.tcp.flags, 16)
        sniff_timestamp = float(packet.sniff_timestamp)

        connection_id = (src_ip, src_port, dest_ip, dest_port)

        if tcp_flags & 0x02:
            connection_start_times[connection_id] = sniff_timestamp
            connection_durations[connection_id] = 100  
            packet_colors[connection_id] = 'red'  

        elif (tcp_flags & 0x11) or (tcp_flags & 0x04):  
            if connection_id in connection_start_times:
                start_time = connection_start_times[connection_id]
                connection_durations[connection_id] = sniff_timestamp - start_time
                completed_connections += 1
                packet_colors[connection_id] = 'blue'

    except Exception:
        ignored_packets += 1


def process_pcap():
    global packets
    try:
        packets = pyshark.FileCapture(pcap_file, display_filter="tcp")
        with ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(process_packet, packets)
    except pyshark.capture.capture.TSharkCrashException as e:
        print("[Warning] TShark crashed! Retrying with debug mode...")
        packets.close()
        packets = pyshark.FileCapture(pcap_file, display_filter="tcp")
        packets.set_debug()  # Enable debug mode to see more details
        with ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(process_packet, packets)
    finally:
        packets.close()


process_pcap()

syn_only_connections = sum(1 for d in connection_durations.values() if d == 100)

print(f"Total SYN packets: {len(connection_start_times)}")
print(f"Completed Connections: {completed_connections}")
print(f"Incomplete Connections: {syn_only_connections}")
print(f"Ignored Packets: {ignored_packets}")

start_times = np.array([datetime.datetime.fromtimestamp(t) for t in connection_start_times.values()])
durations = np.array(list(connection_durations.values()))
colors = np.array([packet_colors[conn_id] for conn_id in connection_start_times.keys()])

sorted_indices = np.argsort(start_times)
start_times, durations, colors = start_times[sorted_indices], durations[sorted_indices], colors[sorted_indices]

# Identify attack start and end based on first and last red dot
red_dot_indices = np.where(colors == 'red')[0]

if len(red_dot_indices) > 0:
    attack_start_time = start_times[red_dot_indices[0]]
    attack_end_time = start_times[red_dot_indices[-1]]
else:
    attack_start_time = start_times[0] + datetime.timedelta(seconds=20)
    attack_end_time = start_times[0] + datetime.timedelta(seconds=100)

plt.figure(figsize=(10, 6))
plt.scatter(start_times, durations, c=colors, alpha=0.7)

plt.axvline(attack_start_time, color='r', linestyle='dashed', label="Attack Start")
plt.axvline(attack_end_time, color='g', linestyle='dashed', label="Attack End")
plt.xlabel("Start Time")
plt.ylabel("Connection Duration (seconds)")
plt.title("TCP Connection Duration vs. Start Time")
plt.xticks(rotation=45)
plt.legend(["TCP Connections", "Attack Start", "Attack End"])
plt.grid(True)
plt.show()
