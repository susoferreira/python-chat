#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
import select
import time
from hashlib import sha256
from RC4 import RC4 #noentiendo el fallo
from mensajes import mensaje
# Define las clases comunes al cliente y servidor

class sock(socket.socket):  # subclase wrapper de socket

    def __init__(self, server, port):
        # constructor de la superclase
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server = server
        self.port = port
        self.nombre = ""
        self.enckey=""
        
    def recibir(self, objetivo :socket.socket) -> mensaje:
        response = objetivo.recv(1024)
        
        if not response: # if socket is readable but first read is empty then the socket is dead
            x = objetivo.getpeername()
            objetivo.close()
            print(x," se ha desconectado")
            raise ConnectionError
        else:
            try:
                while True:
                    buffer = objetivo.recv(1024)
                    if buffer:
                        response+=buffer
                    else:
                        break
                return mensaje.deRecibido(mensaje.decrypt(buffer))
            except Exception:
                return mensaje("SERVER",
                "Alguien ha intentado envíar un mensaje con bytes inválidos, esto puede deberse a ue tenga una versión desactualizada del cliente o a una contraseña incorrecta")