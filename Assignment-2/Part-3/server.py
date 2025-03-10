#!/usr/bin/python

import socket
import time
import argparse
import struct

def run_server(port, nagle_enabled, delayed_ack_enabled):
    """
    Run a TCP server with configurable Nagle and Delayed-ACK settings
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Configure socket options
    if not nagle_enabled:
        server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    
    if not delayed_ack_enabled:
        # TCP_QUICKACK is Linux-specific
        try:
            server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)
        except AttributeError:
            print("TCP_QUICKACK not available on this system")
    
    # Bind to all interfaces
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(1)
    
    print(f"Server listening on port {port}")
    print(f"Nagle's Algorithm: {'Enabled' if nagle_enabled else 'Disabled'}")
    print(f"Delayed ACK: {'Enabled' if delayed_ack_enabled else 'Disabled'}")
    
    conn, addr = server_socket.accept()
    print(f"Connection from {addr}")
    
    # Initialize metrics
    bytes_received = 0
    packets_received = 0
    max_packet_size = 0
    start_time = time.time()
    
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
                
            # Update metrics
            packet_size = len(data)
            bytes_received += packet_size
            packets_received += 1
            max_packet_size = max(max_packet_size, packet_size)
            
            # Send ACK for the data
            conn.sendall(b'ACK')
    except Exception as e:
        print(f"Error: {e}")
    finally:
        end_time = time.time()
        duration = end_time - start_time
        
        # Calculate metrics
        throughput = bytes_received / duration if duration > 0 else 0
        
        print("\nConnection closed")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Bytes received: {bytes_received}")
        print(f"Packets received: {packets_received}")
        print(f"Throughput: {throughput:.2f} bytes/sec")
        print(f"Maximum packet size: {max_packet_size} bytes")
        
        conn.close()
        server_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TCP Server with configurable Nagle and Delayed-ACK')
    parser.add_argument('--port', type=int, default=5000, help='Server port')
    parser.add_argument('--nagle', type=int, default=1, help='Enable Nagle\'s algorithm (1=enabled, 0=disabled)')
    parser.add_argument('--delayed-ack', type=int, default=1, help='Enable Delayed-ACK (1=enabled, 0=disabled)')
    
    args = parser.parse_args()
    
    run_server(args.port, bool(args.nagle), bool(args.delayed_ack))
