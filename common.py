#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
import select
import time
from hashlib import sha256
from RC4 import RC4 #noentiendo el fallo
# Define las clases comunes al cliente y servidor

class grupo:
    def __init__(self,nombre,participantes):
        self.nombre=""
        self.participantes=tuple() # tupla con los nombres de los participantes

class mensaje:
    headers = [
        ("len", 6),
        ("contenido", 1),
        ("nombre", 20),
    ]
    headerencoding = "utf-32"
    encoding="utf-8"
    enckey = "" # se comparte entre todas las instancias de mensaje
    headersize = sum([i[1] for i in headers])

    def __init__(self, nombre, contenido, objetivo="a", tipo="t"):
        self.nombre = nombre
        self.contenido = contenido
        self.tipo = tipo
        self.msg=b"" # forma en la que se envia
        # tipos:
        # l (login, se envía uno al conectarse al server, el nombre de ese mensaje es el que sirve para identificar al socket)
        # t (texto, mensajes normales)
        # i (info, del server al cliente)
        # c (lista de clientes conectados)
        # b (desconexión) no implementado
        # g (creación de grupo) no implementado
        # por ahora solo existe a , para mandar mensajes privados se usaría la variable sock.nombre o el grupo
        self.objetivo = objetivo

    def enviar(self, socketAEnviar):  # envia el mensaje convertido a bytes con un null byte de terminación
        if self.msg == b"":
            self.msg = self.toBytes()
        #print(f"enviando bytes sin encriptar: {self.msg}")
        try:
            socketAEnviar.sendall(self.msg)
        except ConnectionError:
            print("conexión reseteada con el cliente",socketAEnviar)
            socketAEnviar.close()
    def toBytes(self):  # transforma el mensaje en texto con los headers correspondiente

        if len(str(len(self.contenido.encode(mensaje.headerencoding)))) > 6: # mensaje demasiado largo
            self.contenido ="Este usuario ha intentado enviar un mensaje demasiado largo"
        self.contenido = RC4(self.contenido,self.__class__.enckey) # solo se cifra el contenido del mensaje
        headers = "{:<6}{:<1}{:<20}".format(len(self.contenido),self.tipo,self.nombre)
        headers=headers.encode("utf-32")
        return headers+self.contenido
    @classmethod
    # constructor para crear un mensaje con los datos de un mensaje recibido
    def deRecibido(cls, mensaje):
        nombre, tipo, texto = mensaje
        return cls(nombre, texto,tipo=tipo)

    @classmethod
    def deTexto(cls, nombre, texto):  # constructor alternativo
        if nombre == "":
            print("No tienes nombre, cambialo con self.nombre")
        return cls(nombre, texto)

    @classmethod
    def headerdecode(cls, data):  # obtiene los datos del header de un mensaje
        headers = []
        len = 0
        start = 0
        try:
            print(f"raw headers: {data}")
            data=data.decode(mensaje.headerencoding)
        

            for i in cls.headers:
                len += i[1]

                headers.append(data[start:len])
                #print(f"header {i}:{data[start:len].decode(headerencoding)}")
                start = len
        except UnicodeDecodeError:
            return -1
        return headers


class sock(socket.socket):  # subclase wrapper de socket

    def __init__(self, server, port):
        # constructor de la superclase
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server = server
        self.port = port
        self.nombre = ""
        self.enckey=""
        
    def recibir(self, objetivo):
        try:
            headerdata = objetivo.recv(mensaje.headersize*4 + 4) # cada caracter en utf-32 son 4 bytes
        except Exception as e:
            print(e)
            objetivo.close()
            raise ConnectionError
        #print("longiud headers", len(headerdata))
        #print("header raw data",headerdata,type(headerdata))
        if not headerdata:  # no hay datos porque select detecta un socket cerrado como readable
            x = objetivo.getpeername()
            objetivo.close()
            print("objetivo cerrado",objetivo.fileno())
            raise ConnectionError
        if mensaje.headerdecode(headerdata) != -1:
            msglen, tipo, nombre = [i.strip() for i in mensaje.headerdecode(headerdata)]
            
        else:
            with open("log.txt","w") as log:
                log.write(f"Headerdata:\n{headerdata}",)
            objetivo.close()
            return ("","t","Para de intentar romper el chat coño pesado")

        #print(f"longitud:{msglen}, tipo {tipo}, enviado por {nombre}")

        #print(f"longitud: {msglen}, tipo: {tipo},nombre: {nombre}")
        msglen = int(msglen)
        msg = b""

        while True:
            try:
                x = objetivo.recv(msglen)
                msg += x if x != "" else ""
                #print("recibido:",msg,type(msg))
                contenidoDecodificado = RC4(msg,mensaje.enckey).decode(mensaje.encoding)
                #print("recibido decriptado:",contenidoDecodificado)
                return (nombre, tipo,contenidoDecodificado)
                # if msg.decode("utf-8") != "":
                #     print("debug", msg.decode("utf-8"))
            except UnicodeDecodeError:
                return (nombre,tipo,"bytes no validos en utf-8 o longitud del mensaje mal codificada")
