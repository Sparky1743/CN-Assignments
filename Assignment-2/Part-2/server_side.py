import socket
import subprocess

class Server:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port

    def handle_clients(self, server):
        while True:
            conn, addr = server.accept()
            print(f"New Connection: {addr} connected.")
            
            while True:
                try:
                    message = conn.recv(1024)
                    if not message:
                        break
                    print(f"Received from {addr}: {message.decode()}")
                    conn.send(message)  # Echo back the message
                except:
                    break
            
            print(f"Lost connection with {addr}")
            conn.close()

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen()
        print(f"Server listening on {self.host}:{self.port}")
        
        try:
            self.handle_clients(server)
        except KeyboardInterrupt:
            print("Shutting down server...")

def set_kernel_parameters():
    subprocess.run(['sudo', 'sysctl', '-w', 'net.ipv4.tcp_max_syn_backlog=2048'])
    subprocess.run(['sudo', 'sysctl', '-w', 'net.ipv4.tcp_syncookies=1'])
    subprocess.run(['sudo', 'sysctl', '-w', 'net.ipv4.tcp_synack_retries=2'])

if __name__ == "__main__":
    set_kernel_parameters()
    server = Server()
    server.start_server()
