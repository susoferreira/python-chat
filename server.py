#! /usr/bin/python3

import log
log.LOG_FILE="./logs/serverlog"
from log import log

import socket
import select
from time import sleep
from common import sock
from hashlib import md5

from mensajes import mensaje

from typing import List  # type hinting list[Cliente]


class Server:

    def __init__(self, server: str, port: int):
        self.s = sock(server, port)
        self.clients: List[Cliente] = []  # list of connected clients
        self.nombre = "SERVER"
        # Buffer for messages to be sent to all clients
        self.aEnviar: List[mensaje] = []

    def getListaNombres(self) -> list:
        return [client.name for client in self.clients]

    def getListaSockets(self):

        return [client.s for client in self.clients]

    def abrirserver(self):
        print(f"debug: server {self.s.server}, port {self.s.port}")
        self.s.bind((self.s.server, self.s.port))
        self.s.listen(30)
        socket.gethostbyaddr("localhost")

    def getConectadosMsg(self) -> mensaje:
        listaconectados = "\t".join(i for i in self.getListaNombres())
        return mensaje(self.nombre, listaconectados, tipo="c")

    def aceptarcliente(self):
        socket, address = self.s.accept()
        msg = self.s.recibir(socket)

        if msg.tipo != "l":
            log("error recibiendo mensaje de login")
            socket.close()

        elif msg.nombre in self.getListaNombres():
            mensaje.deTexto(
                self.nombre, "Ya estás conectado a este servidor").enviar(socket)
            socket.close()
        else:
            self.clients.append(Cliente(socket, address, msg.nombre))
            for i in self.clients:
                self.getConectadosMsg().enviar(i.s)
            mensaje.deTexto(
                self.nombre, "Te Has Conectado").enviar(socket)  # TODO REFACTOR THIS TO USE client.msg
            log(f"Cliente {address} aceptado,{self.clients[-1].name}")
            self.aEnviar.append(mensaje.deTexto("SERVER",f"{self.clients[-1].name} se ha conectado"))


    def seleccionar(self):  # select.select() wrapper
        # lista con solo los sockets de los clientes para usar con select
        socketlist = self.getListaSockets()
        # si el propio socket es readable es que se puede aceptar un cliente
        socketlist.append(self.s)

        # if socketlist == []:  # A windows no le gusta select.select() con 3 listas vacías
        #     return [], [], []
        # Esas dos líneas ya no son necesarias pero constan como patrimonio cultural de este programa

        return select.select(socketlist, socketlist, [])

    def sender(self):  # sends all messages from message list to a group of sockets
        for msg in self.aEnviar:
            if msg.objetivo=="a":
                for cliente in self.clients:
                    msg.enviar(cliente.s)
            else:
                for cliente in self.clients:
                    print("recibido mensaje con objetivo custom")
                    if cliente.name in msg.objetivo.split(" "):
                        msg.enviar(cliente.s)
            self.aEnviar.remove(msg)

    def messagehandler(self, msg: mensaje) -> None:  # interprets messages received
        
        if msg.tipo == "t":  # texto
            print("recibido:",msg.__dict__)
            if msg.contenido != "":
                # echo message to clients
                self.aEnviar.append(msg)
        elif msg.tipo == "l":
            log("Error, login message received after login",msg.__dict__)
        else:
            log("tipo de mensaje inválido recibido:",msg.__dict__)

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
                            self.aEnviar.append(mensaje.deTexto("SERVER",client.name +" se ha desconectado"))
                            self.clients.remove(client)
        except KeyboardInterrupt:
            self.aEnviar.append(mensaje.deTexto(
                self.nombre, "Servidor Cerrandose"))
            self.s.close()

    def readables(self, readable: list) -> None:
        for socket in readable:
            if socket.fileno() == self.s.fileno():  # if readable == server there's a client to accept
                self.aceptarcliente()
                break
            self.messagehandler(self.s.recibir(socket))

    def writables(self, writable: list) -> None:
        if self.aEnviar:
            self.sender()


class Cliente:
    def __init__(self, s: socket.socket, ip: str, name: str):
        self.s = s
        self.ip = ip
        self.name = name
        self.msg: List[mensaje] = []  # buffer for uniue messages for a client


if __name__ == "__main__":
    serv = Server("", 12500)
    serv.abrirserver()
    mensaje.enckey = md5("gei".encode("utf-8")).digest()
    serv.rutina()
