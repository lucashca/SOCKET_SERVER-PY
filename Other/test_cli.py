from socket import *



client_socket = socket(AF_INET,SOCK_STREAM)

while True:
    client_socket.connect(('localhost',8080))
    client_socket.send(str.encode("Test"))
    while True:
        data = client_socket.recv(1024)
        print(data.decode())
        if not data:
            print("Todos os arquivos listados")
            break
    client_socket.close()