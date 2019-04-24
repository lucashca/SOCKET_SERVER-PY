from socket import *
from threading import *
import sys
import string
import keyboard
import sys
import os
import glob
import time
import _thread as thread
host = 'localhost'
port = 8080
mysocket =  socket(AF_INET,SOCK_STREAM)
mysocket.bind((host,port))
mysocket.listen(5)
my_dir = "D:\\Estudos\\Sistemas Distribuidos\\Projeto Server-Client\\"

mutex = thread.allocate_lock()

param = sys.argv[1:]
##port = param[0]
##file_directory = param[1]


def listen(tecla):  
    while True:
        keyboard.wait(tecla)
        print ("Servidor finalizado")
        sys.exit()

def process_request(conexao):
    mutex.acquire()
    data = conexao.recv(1024)
    #print("Dado recebido ", data.decode())
    if data.decode() == "-list":
        os.chdir(my_dir)
        for file in glob.glob("*.*"):
            size_file = os.path.getsize(file)
            msg_send = file + "  "+str(size_file)
            print("",end=" ")
            conexao.send(str.encode(msg_send))
    else:
        file_search = data.decode()
        arq = open(file_search, 'rb')
        size = os.path.getsize(file_search)
        #Região critica
        try:
            conexao.send(str.encode(str(size))) 
            for i in arq.readlines():
                conexao.send(i)
        except:
            print("Erro ao estabelecer a comunicação com o cliente!")
        arq.close()
        #Fim região critica
    conexao.close()
    print("\nConexão Finalizada")
    print("Aguardando nova conexão")
    mutex.release()
def server():
   
    pid = 0;
    while True:
      
        conexao, endereco = mysocket.accept()
        print("Server conectado por",endereco,"as",time_now())
      

        thread_server = Thread(target=process_request, kwargs={"conexao":conexao})
        thread_server.start()
      
    
def time_now():
     return time.ctime(time.time())

def main():
    threads = [Thread(target=listen, kwargs={"tecla":chr(27)})]
    for thread in threads:
            thread.start()
    print("Servidor iniciado, aguardando conexão.")
    print("Precione a tecla 'ESC' para sair.")
    server()

main()



