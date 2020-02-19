#! /usr/bin/python3
import socket
import select
from time import sleep
from common import mensaje, sock
from hashlib import md5

contadorLoVeis = 0


class Server:
    
    def __init__(self, server: str, port: int):
        self.s = sock(server, port)
        self.clients = []  # list of connected clients
        self.nombre = "SERVER"
        self.aEnviar = []  # Buffer for messages to be sent

    def abrirserver(self):
        print(f"debug: server {self.s.server}, port {self.s.port}")
        self.s.bind((self.s.server, self.s.port))
        self.s.listen(30)
        socket.gethostbyaddr("localhost")

    def aceptarcliente(self):
        socket, address = self.s.accept()
        nombre, tipo, texto = self.s.recibir(socket)

        if tipo != "l":
            print("error recibiendo mensaje de login")
            socket.close()

        elif nombre in self.getListaNombres():
            mensaje.deTexto(
                self.nombre, "Ya estás conectado a este servidor").enviar(socket)
            socket.close()
        else:
            self.clients.append((socket, address, nombre))
            self.aEnviar.append(self.getConectadosMsg())
            mensaje.deTexto(self.nombre, "Te Has Conectado").enviar(socket)
            print(f"Cliente {address} aceptado,{self.clients[0]}")

    def getConectadosMsg(self) -> mensaje:
        listaconectados = "\t".join(i for i in self.getListaNombres())
        mensaje(self.nombre, listaconectados, tipo="c")

    def seleccionar(self):  # select wrapper
        # lista con solo los sockets de los clientes para usar con select
        socketlist = self.getListaSockets()
        # si el propio socket es readable es que se puede aceptar un cliente
        socketlist.append(self.s)
        if socketlist == []:  # A windows no le gusta select.select() con 3 listas vacías
            return [], [], []
        return select.select(socketlist, socketlist, [])

    def sender(self, grupo =None):  # sends all messages from message list to a group of sockets
        if grupo == None:
            grupo = self.clients

        for texto in self.aEnviar:
            m = mensaje.deTexto(self.nombre, texto)
            self.broadcast(m,grupo)
            self.aEnviar.remove(texto)

    def bots(self, msg):
        
        nombre, tipo, texto = msg

        # LoEntendeisBot
        if texto == "/LoVeis":
            global contadorLoVeis
            contadorLoVeis += 1
            texto = f"Lo veis dicho {contadorLoVeis} veces."
            self.aEnviar.append(mensaje.deTexto(self.nombre, texto))
        # LoEntendeisBot

    def messagehandler(self, msg):
        nombre, tipo, texto = msg
        if tipo == "t":  # texto
            mensajeParaEnviar = mensaje.deRecibido(msg)
            if texto != "":
                if texto[0] == "/":
                    self.bots(msg)
            self.aEnviar.append(mensajeParaEnviar) # echo message to clients

        if tipo == "l": 
            print("Error, login message received after login")
        if tipo == "g":  #this type is planned to use for group creation
            pass
    

    def broadcast(self, mensaje, grupo): #sends a message object to every client in a group
        socketlist = [grupo[i][0] for i in range(len(grupo))] #gets a list of sockets from the socketlist
        for i in socketlist:
            mensaje.enviar(i)

    # devuelve los nombres de los clientes conectados
    def getListaNombres(self) -> list:
        return [i[2] for i in self.clients]

    def getListaSockets(self):

        return [i[0] for i in self.clients]

    def rutina(self):
        try:
            while True:
                try:

                    sleep(1/100)  # sin este sleep el bucle gasta demasiada cpu

                    readable, writable, exceptional = self.seleccionar()


                    self.readables(readable)
                    self.messagehandler(self.s.recibir(socket))

                
                    
                    readable, writable, exceptional = [], [], []
                except ConnectionError:  # se ha desconectado un socket
                    for i in self.clients:
                        if i[0].fileno() == -1:  # el socket que se ha desconectado tiene un fd inválido
                            print(i[1], i[2], "se ha desconectado")
                            self.clients.remove(i)
        except KeyboardInterrupt:
            self.aEnviar.append(mensaje.deTexto(self.nombre, "Servidor Cerrandose"))
            self.s.close()

    def readables(self,readable : list) -> None:
        for socket in readable:
            if socket.fileno() == self.s.fileno():  #if readable == server there's a client to accept
                self.aceptarcliente()
                break

    def writables(self,writable : list) -> None:
        for socket in writable:
            self.sender(socket)

if __name__ == "__main__":
    serv = Server("", 12500)
    serv.abrirserver()
    mensaje.enckey = md5("ChaoMorais".encode("utf-8")).digest()
    serv.rutina()
