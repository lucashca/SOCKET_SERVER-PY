from socket import *
from threading import *


mysocket =  socket(AF_INET,SOCK_STREAM)         #Setting param for the socket, AF_INET = IPv4 family, SOCK_STREAM = both TCP protocol of the transport layer
mysocket.bind(('localhost',8080))                      #Instantiate address to the socket host:port
mysocket.listen(5) 
mysocket.settimeout(0.0)  

close_now = False

def quitProg():
    global close_now
    while not close_now:
        a = input()
        if a == "q": 
            close_now = True
            mysocket.close()
            print("Saindo")
            exit()


thread_server = Thread(target=quitProg, kwargs={})
thread_server.start()    

while not close_now:
    
    try:
        conexao, endereco = mysocket.accept()
        print(conexao)
        print("Finalizando a conexão")   
    except:
        pass
