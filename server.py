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
import copy

#teste
 
host = 'localhost'                              #Server host definition 
param = sys.argv[1:]                            #Getting params posted by the console. sys.argv [0] is not necessary because it is the name of the python script
my_dir = param[1]                               #param[1] is the directory path of the files bank
port = int(param[0],10)                                 #Server port definition 
mysocket =  socket(AF_INET,SOCK_STREAM)         #Setting param for the socket, AF_INET = IPv4 family, SOCK_STREAM = both TCP protocol of the transport layer
mysocket.bind((host,port))                      #Instantiate address to the socket host:port
mysocket.listen(5)                              #Setting limit of the multiples clientes conected

mutex = thread.allocate_lock()                  #Instantiente lock for the threads 
server_threads = []                             #All threads array
close_now = False                               #Key to close the sript
all_conections = []                             #All conections array
all_arq = []                                    #All archives array

cache = {}                                      #Dictionary of the cache, contains CacheObject
fifo_cache = []                                 #Array of the key of the objects in the cache
port_cli = []

#   CACHE METHODS              
class CacheObject:                              #Class of the objct inside in the cache
    def __init__(self,file,size):               #initiate method
        self.file = file                        #File in the cache
        self.size = size                        #Size of the file

#   CACHE METHODS
def getCacheKey():                              #Returns all index of cache dictionary 
    global cache
    return cache.keys()                         

def getCacheObj(key):                           #Returns a cacheObject of cache dictionary with the index = key
    global cache
    return cache[key]       

def getCacheSize(cache):                        #Returns size of the cache, sum of the all files in the cache dictionary
    size = 0
    for obj in cache.keys():
        size = size + cache[obj].size
    return size

def putOnCache(name_key,file,size):             #Method tha save a file in the cache
    global cache,fifo_cache  
    cache_size = getCacheSize(cache)
    next_size = size + cache_size               #Sum the size of the file with the cache size
    while next_size > 64000000:                 #Verify if the next_size is bigger then 64000000 ~= 64MB  
    #   print(int(next_size/1000000),"mb Tamanho da cahce execdido")
    #   print("Removendo item")
        removeFromCache(fifo_cache[0])          #Remove the fist file insrte in the cahce (FIFO policy)
        fifo_cache.pop(0)                       #Remove the fist file insrte in the fifo array
        next_size = size + getCacheSize(cache)  #Refresh de next_size value
    fifo_cache.append(name_key)                 #Put on fifo cache key of the new file in the cache        
    objCache = CacheObject(file,size)           #Create a cacheObcjet
    cache[name_key] = objCache                  #Put on cache the cacheObject that was created before
    #print(name_key," salvo na cache. Tamanho",int(next_size/1000000),"mb" )
   
def removeFromCache(name_key):
    global cache
    if name_key in cache.keys():
        del cache[name_key]
        #print(name_key, " Removido da cache")

def printCache():
    print("Os seguintes arquivos se encontram na cache")
    for obj in cache.keys():
        print (obj)

#FIM DAS FUNÇÕES DA CACHE

def listen(tecla):  
    global close_now
    while not close_now:
        a = input()
        if a == "quit":
            close_now = True
            mysocket.close()
        if a == "send":
            print("Digite q para cancelar!")
            print("Digite a porta.")
            print(port_cli)
            cli_port = input()
            if(not cli_port == 'q' ):
                print("Digite o host.")
                cli_host = input()
                if(not cli_host == 'q' ):
                    print("Digite a mensagem.")
                    msg_send = input()
                    send_msg(cli_host,int(cli_port,10),msg_send)

def send_msg(cli_host,cli_port,msg_send):
    socketobj = socket(AF_INET,SOCK_STREAM)
    socketobj.connect((cli_host,cli_port))
    socketobj.send(str.encode(msg_send))
    data = socketobj.recv(1024)
    print("Mensagem de confirmação.")
    print(data.decode())
  
    
def send_size(conexao,size):
    response = ""
    try:
    #    print("Size", str.encode(str(size)))
        conexao.send(str.encode(str(size)))
        response = conexao.recv(1024)
    except NameError:
        print(NameError)
    
    if response.decode() == "ACK": 
        return True
    return False

def process_request(conexao,client):
    global cache, all_arq
    data = conexao.recv(1024)
    file_search = None
    linesArqCache = []
    save_cache = False
    erro = 0
    
    
    
    
    if data.decode() != "-list" and data.decode() != "-list-cache":
        file_search = data.decode()
        print("Client ",client," is requesting file ",data.decode())
      
    #Not Cache Process
    if data.decode() == "-list": #Verify files in directory
        print("Client ",client," is requesting file ",data.decode())
        os.chdir(my_dir)
        for file in glob.glob("*.*"):
            size_file = os.path.getsize(file)
            msg_send = file + "  "+str(size_file)+"\n"
            print("",end=" ")
            conexao.send(str.encode(msg_send))
        conexao.close()
    elif data.decode() == "-cli_port": #Verify files in directory
        print("-cli_port sendo solicitado")
        conexao.send(str.encode('ACK'))
        print("Aguardando")
        data = conexao.recv(1024)
        p = int(data.decode(),10)
        port_cli.append(p)
        print("Port",data.decode())
        conexao.close()
    elif file_search not in getCacheKey() and file_search != None:  # Cache miss, file not in the the cache
        try:
            arq = open(my_dir+file_search, 'rb')
            all_arq.append(arq)
            size = os.path.getsize(my_dir+file_search)
            print("Cache miss.",file_search," sent to the client")
        except:
            print("File ",file_search," does not exist")
            conexao.send(str.encode(str("ERRO")))
            erro = 1
            conexao.close()
        if not erro:
            try:
                resp = send_size(conexao,size)
                if resp:           
                    if(size < 64000000):
                        for i in arq.readlines():
                            conexao.send(i)
                            linesArqCache.append(i)
                        save_cache = True
                    else:
                        for i in arq.readlines():
                            conexao.send(i)
            except NameError:
                print(NameError)
                print("Directory- Erro ao enviar o arquivo ",file_search)
            arq.close()
            conexao.close()
    
    #Cache Process 
    elif data.decode() == "-list-cache":
        print("Client ",client," is requesting file ",data.decode())
        print("")
        if len(cache) != 0:
            for key in cache.keys():
                conexao.send(str.encode(key))
        else:              
            conexao.send(str.encode("Cache vazia!")) 
            
        conexao.close()   
    ## Initial request for the mutex lock

    if save_cache:
        mutex.acquire() 
        putOnCache(file_search,linesArqCache,size)
        mutex.release() 
    
    elif file_search in cache.keys():  # Cache hit file is in the cache    
        mutex.acquire() 
        if file_search in cache.keys():
            obj = cache.get(file_search)
            cacheFile = obj.file
            size = obj.size
            print("Cache hit.",file_search," sent to the client")
            try:
                resp = send_size(conexao,size)
                if resp:
                #time.sleep(0.2)
                    for i in cacheFile:
                        conexao.send(i)
            except NameError:
                print("Cache- Erro ao enviar o arquivo ",file_search)
                if file_search in cache.keys():
                    print(file_search," na cache")
                else:
                    print(file_search," removido da cache")
                print(NameError)
            conexao.close()
       
        elif file_search not in getCacheKey():  # Cache miss, file not in the the cache 
            try:
                arq = open(my_dir+file_search, 'rb')
                all_arq.append(arq)
                size = os.path.getsize(my_dir+file_search)
                print("Cache miss.",file_search," sent to the client")
            except:
                print("File ",file_search," does not exist")
                conexao.send(str.encode(str("ERRO")))
                erro = 1
                conexao.close()
            if not erro:
                try:
                    resp = send_size(conexao,size)
                    if resp:           
                        if(size < 64000000):
                            for i in arq.readlines():
                                conexao.send(i)
                                linesArqCache.append(i)
                            save_cache = True
                        else:
                            for i in arq.readlines():
                                conexao.send(i)
                except NameError:
                    print(NameError)
                    print("Directory- Erro ao enviar o arquivo ",file_search)
                arq.close()
            conexao.close()
        mutex.release()
    conexao.close()
    
   
def server():
    global server_threads,close_now,all_conections
    while True:
        try:
            conexao, endereco = mysocket.accept()
           
            client_aux = str(endereco).split(",")
            client_end = client_aux[0].replace("(","")
            all_conections.append(conexao)
            thread_server = Thread(target=process_request, kwargs={"conexao":conexao,"client":client_end})
            thread_server.setName(endereco)
            thread_server.start()
            server_threads.append(thread_server)
        except:
            print()
        if(close_now):
            print ("Servidor finalizado")
            try:
                arq.close()
            except:
                print("Nenhum arquivo aberto") 
            killAllThreads()
            fechar_conexoes()
            fechar_arquivos()
            os.system('pkill -f server.py')
            exit()
    
def time_now():
     return time.ctime(time.time())
def fechar_arquivos():
    global  all_arq
    for a in all_arq:
        try:
            a.close()
        except:
            print()
def fechar_conexoes():
    global all_conections
    for c in all_conections:
        try:
            c.close()
            #print("Conexão Fechada")
        except:
            print("")

def killAllThreads():
    #print("Finalizando as threads")
    for th in server_threads:
        print("Th Name ",th.getName()," Is alive ",th.is_alive())

def main():
    threads = [Thread(target=listen, kwargs={"tecla":chr(27)})]
    for thread in threads:
            thread.start()
    print("Servidor iniciado na porta ",port,". Aguardando conexão com clientes.")
    print("Precione a tecla 'ESC' em seguida 'Ctrl + C' para sair.")
    server()
main()




