import socket
import time

class Client:
    def __init__(self, host='172.23.198.251', port=8080):
        self.host = host
        self.port = port

    def send_legitimate_traffic(self):
        while True:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.host, self.port))

            message = "This is a TCP packet"
            client.sendall(message.encode())
            print(f"Sent message: {message}")

            try:
                response = client.recv(1024).decode()
                print(f"Received from server: {response}")
            except socket.timeout:
                print("No response received")

            client.close()
            time.sleep(1)

if __name__ == "__main__":
    client = Client()
    client.send_legitimate_traffic()
