from socket import *
from threading import *
import sys
import string
import keyboard
import sys
import os
import glob


def listen(tecla):  
    while True:
        keyboard.wait(tecla)
        print ("Servidor finalizado")
        sys.exit()
          

   

threads = [Thread(target=listen, kwargs={"tecla":chr(27)})]
for thread in threads:
        thread.start()
  
    


host = 'localhost'
port = 8080
mysocket =  socket(AF_INET,SOCK_STREAM)
mysocket.bind((host,port))
mysocket.listen(5)
my_dir = "D:\\Estudos\\Sistemas Distribuidos\\Projeto Server-Client\\"



while True:
    print("Servidor iniciado, aguardando conexão.")
    print("Precione a tecla 'ESC' para sair.")

    conexao, endereco = mysocket.accept()
    print('Server conectado por', endereco)
    
    data = conexao.recv(1024)
    print("Dado recebido ", data.decode())
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
        try:
            conexao.send(str.encode(str(size))) 
            for i in arq.readlines():
                conexao.send(i)
        except:
            print("Erro ao estabelecer a comunicação com o cliente!")
        arq.close()
    conexao.close()
    
    print("Conexão Finalizada")
    print("Aguardando nova conexão")
   





