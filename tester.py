from threading import *
import _thread as thread
import os

mutex = thread.allocate_lock()

def call_client(str):
    os.system(str)

threads = []
for i in range(0,30):

    t1 = Thread(target=call_client, kwargs={"str":str("python3 client.py localhost 8080 a.pdf a."+str(i)+".pdf")})
    t2 = Thread(target=call_client, kwargs={"str":str("python3 client.py localhost 8080 b.pdf b."+str(i)+".pdf")})
    t3 = Thread(target=call_client, kwargs={"str":str("python3 client.py localhost 8080 c.pdf c."+str(i)+".pdf")})
    
    #t1 = Thread(target=call_client, kwargs={"str":str("python3 client.py localhost 8080 10.exe 10."+str(i)+".exe")})
    #t2 = Thread(target=call_client, kwargs={"str":str("python3 client.py localhost 8080 60.exe 60."+str(i)+".exe")})
    #t3 = Thread(target=call_client, kwargs={"str":str("python3 client.py localhost 8080 65.exe 65."+str(i)+".exe")})
    t1.setName("10."+str(i)+".exe")
    t2.setName("60."+str(i)+".exe")
    t3.setName("65."+str(i)+".exe")
    t1.start()
    t2.start()
    t3.start()
    threads.append(t1)
    threads.append(t2)
    threads.append(t3)
    
   

while True:
    br = 1
    for tr in threads:
        if tr.is_alive():
            br = 0
    if br: break
print("\nListando a cache")
call_client("python3 client.py localhost 8080 -list-cache")

    

