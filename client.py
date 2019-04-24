from socket import *
from threading import *
import string
import sys
from random import randint
import _thread as thread

my_dir = './saved_files/'
param = sys.argv[1:]
serverHost = param[0]
serverPort = int(param[1],10)
cmd_file = param[2]
try:
    file_destiny = param[3]
except:
    file_destiny = cmd_file

def progressBar(value, endvalue, bar_length):
    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length)-1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\rPercent: [{0}] {1}% | {2}/{3}  ".format(arrow + spaces, int(round(percent * 100)),value,endvalue))
    sys.stdout.flush()

def client_server():
    port = randint(10000,20000)
    host = 'localhost'                              #Server host definition 
    mysocket =  socket(AF_INET,SOCK_STREAM)         #Setting param for the socket, AF_INET = IPv4 family, SOCK_STREAM = both TCP protocol of the transport layer
    mysocket.bind((host,port))                      #Instantiate address to the socket host:port
    mysocket.listen(5)                              #Setting limit of the multiples clientes conected
    print("Sending Cli_port ",port)
    client(serverHost,serverPort,'-cli_port',port)
    while True:
        try:
            conexao, endereco = mysocket.accept()
            client_aux = str(endereco).split(",")
            client_end = client_aux[0].replace("(","")
            print("Servidor : ",endereco," ativou uma conexão com o cliente")
            while True:
                data = conexao.recv(1024)
                print(data.decode())
                if(not data):
                    break
        except:
            print("Finalizando cliente")
        



def client(serverHost,serverPort,cmd_file,file_destiny):
    global my_dir
    
   
    socketobj = socket(AF_INET,SOCK_STREAM)
    socketobj.connect((serverHost,serverPort))

    if cmd_file == "-list":
        socketobj.send(str.encode("-list"))
        while True:
            data = socketobj.recv(1024)
            print(data.decode())
            if not data:
                print("Todos os arquivos listados")
                break
    elif cmd_file == "-list-cache":
        socketobj.send(str.encode("-list-cache"))
        while True:
            data = socketobj.recv(1024)
            print(data.decode())
            if not data:
                print("Todos os arquivos listados")
                break
    elif cmd_file == "-cli_port":
        socketobj.send(str.encode("-cli_port"))
        data = socketobj.recv(1024)
        print(data.decode())
        socketobj.send(str.encode(str(file_destiny)))
       
    else:
        file_search = cmd_file
        file_destiny = my_dir+file_destiny
        file_name = file_destiny
      
        arq = open(file_destiny, 'wb')

        socketobj.send(str.encode(file_search))
        header = socketobj.recv(1024)
        if(header.decode() == "ERRO"):
            print("File ", file_search," does not exist in the server")
            socketobj.send(str.encode("NOACK"))
            
        else:
            try:
                size = int(header.decode(),10)
            except:
                print()
            size = int(header.decode(),10)
            
            i = 1
            n = 0
            socketobj.send(str.encode("ACK"))
            while True:
                value = n*1024
                if value > size:
                    value = size
                progressBar(value,size,20)
                n = n + 1
                #print("data_socket ",file_destiny)
                data = socketobj.recv(1024)
                if not data:
                    break
                arq.write(data)  
            print("File ",file_name," saved")
            arq.close()
        
        socketobj.close()

def main():
    thread_server = Thread(target=client_server, kwargs={})
    thread_server.start()
    client(serverHost,serverPort,cmd_file,file_destiny)

main()