encoding = "utf-32"
def KSA(key): # genera un array s que se usará para generar la clave
        
       
        s = [i for i in range(256)] 
        
        j=0
        for i in range(256):
            j=(j+s[i]+key[i%len(key)])%256
            s[i],s[j] = s[j],s[i]
        return s

def PRGA(s,data):
    k=""
    

    while len(k) < len(data):
        
        
        i,j=0,0
        
        i = (i+1)%256
        j = (j + s[i])% 256
        s[i] , s[j] = s[j] , s[i]
        k+=chr(s[(s[i] + s[j]) % 256])
    kBytes = k.encode(encoding)
    return kBytes
def RC4(data,key):# encripta y decripta datos usando el algorimo RC4 , la clave es el md5 de una contraseña de cifrado 
    
    if type(data) == str: # al enviar un mensaje data es un str y al recibir un mensaje data son bytes
        data=data.encode()
    XOR = lambda s1 , s2: bytes( [a ^ b for a,b in zip(s1,s2)]) #calcula el XOR de 2 cadenas de bytes
    k=PRGA(KSA(key),data)
    
    return XOR(k,data)