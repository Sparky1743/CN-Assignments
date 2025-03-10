#!/usr/bin/python

import socket
import time
import argparse
import os

def create_test_file(file_path, size=4096):
    """Create a test file of specified size (default 4KB)"""
    with open(file_path, 'wb') as f:
        f.write(os.urandom(size))
    return file_path

def run_client(server_ip, port, file_path, transfer_rate, duration, nagle_enabled, delayed_ack_enabled):
    """
    Run a TCP client that sends a file at a specific transfer rate
    """
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Configure socket options
    if not nagle_enabled:
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        
    if not delayed_ack_enabled:
        try:
            client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)
        except AttributeError:
            print("TCP_QUICKACK not available on this system")
    
    # Connect to the server
    client_socket.connect((server_ip, port))
    
    print(f"Connected to {server_ip}:{port}")
    print(f"Nagle's Algorithm: {'Enabled' if nagle_enabled else 'Disabled'}")
    print(f"Delayed ACK: {'Enabled' if delayed_ack_enabled else 'Disabled'}")
    print(f"Transfer rate: {transfer_rate} bytes/sec")
    print(f"Duration: {duration} seconds")
    
    # Initialize metrics
    bytes_sent = 0
    packets_sent = 0
    acks_received = 0
    packet_losses = 0
    start_time = time.time()
    end_time = start_time + duration
    
    # Calculate sleep time between sends
    sleep_time = 1.0 / (transfer_rate / 40)  # Send 40 bytes at a time
    
    try:
        file_index = 0
        while time.time() < end_time:
            # Send data in chunks of 40 bytes
            chunk_size = 40
            chunk = file_data[file_index:file_index+chunk_size]
            file_index = (file_index + chunk_size) % len(file_data)  # Wrap around if needed
            
            if not chunk:
                break
                
            # Send the chunk
            client_socket.sendall(chunk)
            packets_sent += 1
            bytes_sent += len(chunk)
            
            # Wait for ACK
            try:
                client_socket.settimeout(1.0)  # 1 second timeout for ACK
                ack = client_socket.recv(3)
                if ack == b'ACK':
                    acks_received += 1
            except socket.timeout:
                packet_losses += 1
            
            # Sleep to maintain transfer rate
            time.sleep(sleep_time)
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        actual_duration = time.time() - start_time
        
        # Calculate metrics
        throughput = bytes_sent / actual_duration if actual_duration > 0 else 0
        goodput = (acks_received * 40) / actual_duration if actual_duration > 0 else 0
        packet_loss_rate = packet_losses / packets_sent if packets_sent > 0 else 0
        
        print("\nTransfer completed")
        print(f"Actual duration: {actual_duration:.2f} seconds")
        print(f"Bytes sent: {bytes_sent}")
        print(f"Packets sent: {packets_sent}")
        print(f"ACKs received: {acks_received}")
        print(f"Throughput: {throughput:.2f} bytes/sec")
        print(f"Goodput: {goodput:.2f} bytes/sec")
        print(f"Packet loss rate: {packet_loss_rate:.2%}")
        
        client_socket.close()
        
        # Return metrics for analysis
        return {
            "throughput": throughput,
            "goodput": goodput,
            "packet_loss_rate": packet_loss_rate,
            "bytes_sent": bytes_sent,
            "packets_sent": packets_sent,
            "acks_received": acks_received,
            "duration": actual_duration,
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TCP Client with configurable Nagle and Delayed-ACK')
    parser.add_argument('--server', type=str, default='127.0.0.1', help='Server IP address')
    parser.add_argument('--port', type=int, default=5000, help='Server port')
    parser.add_argument('--rate', type=int, default=40, help='Transfer rate in bytes/second')
    parser.add_argument('--duration', type=int, default=120, help='Duration in seconds')
    parser.add_argument('--nagle', type=int, default=1, help='Enable Nagle\'s algorithm (1=enabled, 0=disabled)')
    parser.add_argument('--delayed-ack', type=int, default=1, help='Enable Delayed-ACK (1=enabled, 0=disabled)')
    
    args = parser.parse_args()
    
    file_path = create_test_file('/tmp/test_file.bin')
    
    run_client(args.server, args.port, file_path, args.rate, args.duration, 
               bool(args.nagle), bool(args.delayed_ack))
