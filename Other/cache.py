class CacheObject:
    def __init__(self,file,size):
        self.file = file
        self.size = size

cache = {}
fifo_cache = []

def getCacheKey():
    return cache.keys()

def getCacheSize(cache):
    size = 0
    for obj in cache.keys():
        size = size + cache[obj].size
    return size

def putOnCache(name_key,file,size):
    global cache,fifo_cache
    
    cache_size = getCacheSize(cache)
    next_size = size + cache_size
    while next_size > 64000000:
        print(int(next_size/1000000),"mb Tamanho da cahce execdido")
        print("Removendo item")
        removeFromCache(fifo_cache[0])
        fifo_cache.pop(0)
        next_size = size + getCacheSize(cache)
       

    fifo_cache.append(name_key)
    objCache = CacheObject(file,size)
    cache[name_key] = objCache
    print(name_key," salvo na cache. Tamanho",int(next_size/1000000),"mb" )

def removeFromCache(name_key):
    global cache
    if name_key in cache.keys():
        del cache[name_key]
        print(name_key, " Removido da cache")

def printCache():
    print("Os seguintes arquivos se encontram na cache")
    for obj in cache.keys():
        print (obj)
    
print(getCacheKey())
putOnCache("L","Lucas",10000000)
putOnCache("V","Lucas",10000000)
putOnCache("T","Lucas",10000000)
putOnCache("A","Lucas",10000000)
putOnCache("C","Lucas",30000000)
putOnCache("D","Lucas",40000000)

printCache()

