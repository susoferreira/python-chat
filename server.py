#! /usr/bin/python3
import socket
import select
from time import sleep
from common import mensaje, sock
from hashlib import md5

<<<<<<< HEAD
=======

from typing import List #type hinting list[Cliente]
>>>>>>> class_cliente

class Server:
    
    def __init__(self, server: str, port: int):
        self.s = sock(server, port)
        self.clients: List[Cliente] = [] # list of connected clients
        self.nombre = "SERVER"
        self.aEnviar: List[mensaje] = []   # Buffer for messages to be sent to all clients
    def abrirserver(self):
        print(f"debug: server {self.s.server}, port {self.s.port}")
        self.s.bind((self.s.server, self.s.port))
        self.s.listen(30)
        socket.gethostbyaddr("localhost")

    def aceptarcliente(self):
        socket, address = self.s.accept()
        name, tipo, texto = self.s.recibir(socket)

        if tipo != "l":
            print("error recibiendo mensaje de login")
            socket.close()

<<<<<<< HEAD
        elif nombre in self.getListaNombres():
=======
        elif name in self.getListaNombres():
>>>>>>> class_cliente
            mensaje.deTexto(self.nombre, "Ya estás conectado a este servidor").enviar(socket)
            socket.close()
        else:
            self.clients.append(Cliente(socket,address,name))
            self.aEnviar.append(self.getConectadosMsg())
            mensaje.deTexto(self.nombre, "Te Has Conectado").enviar(socket) #TODO REFACTOR THIS TO USE client.msg
            print(f"Cliente {address} aceptado,{self.clients[-1].name}")

    def getConectadosMsg(self) -> mensaje:
        listaconectados = "\t".join(i for i in self.getListaNombres())
        return mensaje(self.nombre, listaconectados, tipo="c")
        
    def seleccionar(self):  # select wrapper
        # lista con solo los sockets de los clientes para usar con select
        socketlist = self.getListaSockets()
        # si el propio socket es readable es que se puede aceptar un cliente
        socketlist.append(self.s)


        # if socketlist == []:  # A windows no le gusta select.select() con 3 listas vacías
        #     return [], [], []
        # Esas dos líneas ya no son necesarias pero constan como patrimonio cultural de este programa

        return select.select(socketlist, socketlist, [])

    def sender(self, grupo = None):  # sends all messages from message list to a group of sockets
        if grupo == None:
            grupo = self.clients

        for msg in self.aEnviar:
            self.broadcast(msg,grupo)
            self.aEnviar.remove(msg)

    def messagehandler(self, msg): # interprets messages received
        nombre, tipo, texto = msg
        if tipo == "t":  # texto
            mensajeParaEnviar = mensaje.deRecibido(msg)
            if texto != "":
                self.aEnviar.append(mensajeParaEnviar) # echo message to clients
<<<<<<< HEAD
        if tipo == "l": 
=======
        elif tipo == "l": 
>>>>>>> class_cliente
            print("Error, login message received after login")
        else:
            print("tipo de mensaje inválido recibido")


    def broadcast(self, mensaje, grupo): #sends a message object to every client in a list of sockets
        for i in grupo:
            mensaje.enviar(i)

    # devuelve los nombres de los clientes conectados
    def getListaNombres(self) -> list:
        return [client.name for client in self.clients]

    def getListaSockets(self):

        return [client.s for client in self.clients]

    def rutina(self):
        try:
            while True:
                try:

                    sleep(1/100)  # sin este sleep el bucle gasta demasiada cpu

                    readable, writable, exceptional = self.seleccionar()
                    if readable:
                        self.readables(readable)
                    if writable:
                        self.writables(writable)

                    readable, writable, exceptional = [], [], []
                except ConnectionError:  # se ha desconectado un socket
                    for client in self.clients:
                        if client.s.fileno() == -1:  # el socket que se ha desconectado tiene un fd inválido
                            print(client.name, client.ip, "se ha desconectado")
                            self.clients.remove(client)
        except KeyboardInterrupt:
            self.aEnviar.append(mensaje.deTexto(self.nombre, "Servidor Cerrandose"))
            self.s.close()

    def readables(self,readable : list) -> None:
        for socket in readable:
            if socket.fileno() == self.s.fileno():  #if readable == server there's a client to accept
                self.aceptarcliente()
                break
            self.messagehandler(self.s.recibir(socket))

    def writables(self,writable : list) -> None:
            if self.aEnviar:
                self.sender(writable)
<<<<<<< HEAD
=======

class Cliente:
    def __init__(self,s : socket.socket,ip:str, name:str):
        self.s= s 
        self.ip = ip
        self.name = name
        self.msg: List[mensaje] = []  # buffer for uniue messages for a client


>>>>>>> class_cliente

if __name__ == "__main__":
    serv = Server("", 12500)
    serv.abrirserver()
    mensaje.enckey = md5("ChaoMorais".encode("utf-8")).digest()
    serv.rutina()
