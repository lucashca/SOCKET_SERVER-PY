from socket import *
from threading import *
import string
import sys
from random import randint
import _thread as thread
import time


enableLog = False



host = 'localhost'                              #Server host definition 

#Socket to response server request
server_socket = socket(AF_INET,SOCK_STREAM)         #Setting param for the socket, AF_INET = IPv4 family, SOCK_STREAM = both TCP protocol of the transport layer

my_dir = './saved_files/'                            #Directory to save requested files 
param = sys.argv[1:]                                 #Get arguments from console  

arq = None
close_now = False

def progressBar(value, endvalue, bar_length):        #Function to make download progress bar layout
    percent = float(value) / endvalue                
    arrow = '-' * int(round(percent * bar_length)-1) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    sys.stdout.write("\rPercent: [{0}] {1}% | {2}/{3}  ".format(arrow + spaces, int(round(percent * 100)),value,endvalue)) # Regular expression to print progress bar
    sys.stdout.flush()  # To print in the same line on the console


def printLog(msg):
    if(enableLog):
        print("***************************LOG*******************************")
        print(msg)
        print("***************************LOG*******************************")

# O conection to listen a server call
def client_server():
    global close_now,server_socket
    while not close_now:
        try:
            conexao, endereco = server_socket.accept()       #wait for a conection
            print("Server : ",endereco," has created a conection with me")
            data = conexao.recv(1024)                         #wait for a msg
            print(data.decode())                                   
            conexao.send(str.encode('ACK'))                   #Send confirmation  
            conexao.close()
        except:
            pass
                    
def initServerSocket():                                 #Start socket to response server
    global server_socket,host
    Sucess = False               
    while not Sucess:    
        port = randint(10000,20000)                     #crate a random port
        try:                                            #Check if that random port is busy
            server_socket.bind((host,port))             #Instantiate address to the socket host:port
            server_socket.listen(5)                     #Setting limit of the multiples clientes conected
            server_socket.settimeout(0.0)               #set server_socket on non-blocking mode, to quit program in any time
            Sucess = True
        except NameError:
            print(NameError)
            port = randint(10000,20000)                 #crate a random port   
    sendPort(port)                                      #Sending port to the server

def initClientSocket():                                 #Start socket to request server
    global client_socket,param
    client_socket = socket(AF_INET,SOCK_STREAM)         #Socket to request file from the server
    serverHost = param[0]                               #get host passed by console
    serverPort = int(param[1],10)                       #get port passed by console
    client_socket.connect((serverHost,serverPort))      #start a conection with the server
    
def getListServer(msg):                                 #send a request for a list of files in directory or cache   
    global client_socket
    client_socket.send(str.encode(msg))                 #send a header of request
    while True:
        data = client_socket.recv(1024)                 #receive data form server 
        print(data.decode()) 
        if not data:
            print("All files listed")
            break
    client_socket.close()

def sendPort(port):                                     #send a port to the server for response requestes of the same
    global client_socket
    client_socket.send(str.encode("-cli_port"))         #Send a header
    data = client_socket.recv(1024)                     #Wait confirmation 
    if(data.decode()=="ACK"): 
        client_socket.send(str.encode(str(port)))       #Send a port
    

def requestFile(file_search,file_destiny):              #Request and save a file
    global client_socket,arq        
    file_name = file_destiny                            
    arq = open(file_destiny, 'wb')                      #Create a file to save a dowload
    client_socket.send(str.encode(file_search))         #Send request, name of file file_search
    header = client_socket.recv(1024)                   #get size of file    
    if(header.decode() == "ERRO"):
        print("File ", file_search," does not exist in the server")
        client_socket.send(str.encode("NOACK"))
    else:
        try:
            size = int(header.decode(),10)              
        except:
            print("Error- Header incorret ", header.decode())
            exit()
        n = 0                                           #Aux progress bar      
        client_socket.send(str.encode("ACK"))           #Send confirmatio msg
        while True:                                     
            value = n*1024                              #Aux progress bar
            if value > size:                            #Aux progress bar, limit is size (100%)
                value = size
            progressBar(value,size,20)                  #Call progress bar (current position)
            n = n + 1
            data = client_socket.recv(1024)             #receive a data
            if not data:
                break
            arq.write(data)                             #save data
        print("File ",file_name," saved")
        arq.close()                                     #close file
    client_socket.close()

def callingMethods():                                   #process methods
    cmd_file = param[2]                                 #read a cmd_file or file_searc from console
    file_search = cmd_file
    try:
        file_destiny = my_dir+param[3]                  #read a file_destiny param[3] form console and add directory
    except:
        file_destiny = my_dir+cmd_file                  #put file_destiny same file_search
    if cmd_file == "-list":                             
        printLog("-list")
        getListServer("-list")                          #list directory
    elif cmd_file == "-list-cache":
        printLog("-list-cache") 
        getListServer("-list-cache")                    #list cache
    else :
        printLog(("Requesting File ",file_search," and destiny is ",file_destiny)) 
        requestFile(file_search,file_destiny)           #request a file
     

    
def quitProg():                                         #quit program in any time
    global close_now,server_socket,client_socket
    while not close_now:
        a = input()
        if a == "q":
            print("Closing...")
            close_now = True
            server_socket.close()                       #close sockets
            client_socket.close()
            try:arq.close()                             #close file
            except:pass

def main():
    initClientSocket()                                          
    initServerSocket()
    thread_server = Thread(target=client_server, kwargs={}) #create a thread to response server
    thread_server.start()                                       
    thread_quit = Thread(target=quitProg, kwargs={})        #crate a thread to quit prog in any time
    thread_quit.start()
    
    callingMethods()
    

main()