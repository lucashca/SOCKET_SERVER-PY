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


enableLog = False                                #Variavél responsável por ativar os logs do sistema


host = 'localhost'                              #Server host definition 
param = sys.argv[1:]                            #Getting params posted by the console. sys.argv [0] is not necessary because it is the name of the python script
my_dir = param[1]                               #param[1] is the directory path of the files bank
port = int(param[0],10)                         #Server port definition 
mysocket =  socket(AF_INET,SOCK_STREAM)         #Setting param for the socket, AF_INET = IPv4 family, SOCK_STREAM = both TCP protocol of the transport layer
mysocket.bind((host,port))                      #Instantiate address to the socket host:port
mysocket.listen(5)                              #Setting limit of the multiples clientes conected
mysocket.settimeout(0.0)                        #Configuring mysocket in non-blocking mode to close the program at any time
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
        removeFromCache(fifo_cache[0])          #Remove the fist file insrte in the cahce (FIFO policy)
        fifo_cache.pop(0)                       #Remove the fist file insrte in the fifo array
        next_size = size + getCacheSize(cache)  #Refresh de next_size value
    fifo_cache.append(name_key)                 #Put on fifo cache key of the new file in the cache        
    objCache = CacheObject(file,size)           #Create a cacheObcjet
    cache[name_key] = objCache                  #Put on cache the cacheObject that was created before
   
def removeFromCache(name_key):                  #romove one element in the cache by the index name_keys
    global cache
    if name_key in cache.keys():
        del cache[name_key]
        
def printCache():                               #Print list of all cache files
    print("Os seguintes arquivos se encontram na cache")
    for obj in cache.keys():
        print (obj)

#FIM DAS FUNÇÕES DA CACHE
def printLog(msg):                              #Log function
    if(enableLog):
        print("***************************LOG*******************************")
        print(msg)
        print("***************************LOG*******************************")
        
def getIpAddress(endereco):                     #Get ip(host) address in a var like (host,port)
    client_aux = str(endereco).split(",")
    return client_aux[0].replace("(","")

def quitProg():                                 #Method to close the programa in any time by a thread
    global close_now
    a = None
    while not close_now:
        print("Press q to quit or send to conect with clients")
        printLog(a)
        a = None
        a = input()
        if a == "q":
            close_now = True
        elif a == "send":
            VerifyClientsOnline()               #Check clinetes conected
            print("Press 'e' to cancel!")
            print("Online clients:")
            print(port_cli)
            cli_port = input()
            if(not cli_port == 'e' ):
                print("enter the message")
                msg_send = input()
                try:
                    send_msg('localhost',int(cli_port,10),msg_send) #Send the msg to the client
                except:
                    print("Error! make sure the port is correct (0-65535)")

def VerifyClientsOnline():                              #Check clinetes conected
    global port_cli
    for port in port_cli:
        try:
            send_msg('localhost',port,'isOn?',True)     #Send a msg in test mode(True)
        except:
            port_cli.remove(port)                       #Remove if disconected

def send_msg(cli_host,cli_port,msg_send,test=False):    #Send the msg to the client

    socketobj = socket(AF_INET,SOCK_STREAM)             
    socketobj.connect((cli_host,cli_port))              #Create a conection withi cli
    socketobj.send(str.encode(msg_send))                #Send a mensege
    data = socketobj.recv(1024)                         #wait for confirmation
    if(not test):                                       
        print("Mensagem de confirmação.")
        print(data.decode())
  
    
def send_size(conexao,size):                            #Send size of file before download
    response = ""                                       
    try:
        printLog(("Size", str.encode(str(size))))
        conexao.send(str.encode(str(size)))             #Send size
        response = conexao.recv(1024)                   #wait for response
    except NameError:       
        #print(NameError)                    
        pass

    if response.decode() == "ACK":                       
        return True
    return False

def process_request(conexao,client):                    #Process and answer a request
    global cache, all_arq
    
    printLog("process_request")

    data = conexao.recv(1024)                           #Wait for the fist request

    if data.decode() == "-cli_port":                    #if the request is -cli_port, it saves the port that the client listens
        conexao.send(str.encode('ACK'))                 #Send a msg of confirmation
        data = conexao.recv(1024)                       #whait for a port
        p = int(data.decode(),10)               
        port_cli.append(p)
        printLog(("Port",p))
        data = conexao.recv(1024)                       #wait for a new request, for other options
    printLog(data.decode())

    file_search = None
    linesArqCache = []
    save_cache = False
    erro = 0


    if data.decode() != "-list" and data.decode() != "-list-cache" and data.decode() != "-cli_port": # Just for show a msg 
        file_search = data.decode()
        print("Client ",client," is requesting file ",file_search)



    #Not Cache Process
    if data.decode() == "-list":                                    #Verify files in directory
        print("Client ",client," is requesting comand ",data.decode())
        os.chdir(my_dir)
        for file in glob.glob("*.*"):
            size_file = os.path.getsize(file)                       #get size of a file in directory
            msg_send = file + "  "+str(size_file)+"\n"  
            print("",end=" ")
            conexao.send(str.encode(msg_send))
        conexao.close()
    elif file_search not in getCacheKey() and file_search != None:  # Cache miss, file not in the the cache
        printLog("Not in cache")
        try:
            arq = open(my_dir+file_search, 'rb')                    #Open a file to send
            all_arq.append(arq)                                     #add for a security policy
            size = os.path.getsize(my_dir+file_search)              #get size of a file in directory
            print("Cache miss.",file_search," sent to the client")
        except:
            print("File ",file_search," does not exist")
            conexao.send(str.encode(str("ERRO")))
            erro = 1
        if not erro:                    
            try:
                resp = send_size(conexao,size)                      #Send size of file to the client
                if resp:           
                    if(size < 64000000):                            #checks if size fits in cache 
                        for i in arq.readlines():                     
                            conexao.send(i)                         #Send line of a file
                            linesArqCache.append(i)                 #save line of a file in array of cache
                        save_cache = True                           #set option save_cache true, inform to the program to save file in cache later
                    else:
                        for i in arq.readlines():                   
                            conexao.send(i)                         #just send file
            except NameError:
                print(NameError)
                print("Directory- Error uploading file ",file_search)
            arq.close()
        conexao.close()

    #Cache Process 
    elif data.decode() == "-list-cache":                            #gel all name of files in cache
        print("Client ",client," is requesting comand ",data.decode())
        print("")
        if len(cache) != 0:
            for key in cache.keys():
                conexao.send(str.encode(key+'\n'))
                                       #send a name of file
        else:              
            conexao.send(str.encode("Cache vazia!")) 
        conexao.close()   
    
    ## Initial request for the mutex lock

    if save_cache:                                                  #Save a file in cache
        mutex.acquire()                                             #lock cache
        putOnCache(file_search,linesArqCache,size)                  #save a file    
        mutex.release()                                             #relase cache
    
    elif file_search in cache.keys():                               # Cache hit file is in the cache    
        mutex.acquire()                                             #lock cache
        if file_search in cache.keys():                             #verify again after get acess before the lock, ensure cache consistency
            obj = cache.get(file_search)                            #get a object in cache
            cacheFile = obj.file                                    #get file in object
            size = obj.size                                         #get size of object
            print("Cache hit.",file_search," sent to the client")
            try:
                resp = send_size(conexao,size)                      #send size of file
                if resp:            
                #time.sleep(0.2)
                    for i in cacheFile:
                        conexao.send(i)                             #send a file to client
            except NameError:
                print("Cache- Error uploading file ",file_search)
                if file_search in cache.keys():
                    print(file_search," in cache")
                else:
                    print(file_search," out cache")
                print(NameError)
            conexao.close()  
        elif file_search not in getCacheKey():                      # Cache miss, file not in the the cache 
            try:                                                    # in case the object has been moved from the cache before leaving the lock
                arq = open(my_dir+file_search, 'rb')                #Open a file to send
                all_arq.append(arq)                                 #add for a security policy 
                size = os.path.getsize(my_dir+file_search)          #get size of a file in directory
                print("Cache miss.",file_search," sent to the client")
            except:
                print("File ",file_search," does not exist")
                conexao.send(str.encode(str("ERRO")))
                erro = 1
                conexao.close()
            if not erro:
                try:
                    resp = send_size(conexao,size)                                  #Send size of file to the client
                    if resp:           
                        if(size < 64000000):                                        #checks if size fits in cache
                            for i in arq.readlines():               
                                conexao.send(i)                                     #Send line of a file
                                linesArqCache.append(i)                             #save line of a file in array of cache
                            save_cache = True                                       #set option save_cache true, inform to the program to save file in cache later
                        else:
                            for i in arq.readlines():
                                conexao.send(i)                                     #Send line of a file
                except NameError:
                    print(NameError)
                    print("Directory- Erro ao enviar o arquivo ",file_search)
                
                if save_cache:                                                      #Save a file in cache
                    putOnCache(file_search,linesArqCache,size)                      #save a file    
                arq.close()
            conexao.close()
        mutex.release()



def server():                                                                       #Manage connections
    global server_threads,close_now,all_conections
    while True:
        try:
            conexao, endereco = mysocket.accept()
            printLog(("Conection created with ",endereco))
            client_end = getIpAddress(endereco)                                     #get client host
            all_conections.append(conexao)                                          #save a conection for security
            thread_server = Thread(target=process_request, kwargs={"conexao":conexao,"client":client_end}) #create a thread to process request for each connection
            thread_server.start()                                                                          #Start thread
            server_threads.append(thread_server)                                    #save threads for security
        except:
            pass
        if close_now:                                                               #close the program
            fechar_conexoes()                                                       #close conections
            fechar_arquivos()                                                       #close files
            print ("Server finish")
            exit()                                                                  #exit program
    
def fechar_arquivos(): # Close all files
    global  all_arq
    for a in all_arq:
        try:
            a.close()
        except:pass

def fechar_conexoes():  # Close all conections 
    global all_conections
    for c in all_conections:
        try:
            c.close()
        except:pass

def main():
    threads = Thread(target=quitProg, kwargs={})                                    #Creat a thread for quit program in any time
    threads.start()                                                                 
    print("Servidor iniciado na porta ",port,". Aguardando conexão com clientes.")
    print("Precione a tecla 'ESC' em seguida 'Ctrl + C' para sair.")
    server()

main()




