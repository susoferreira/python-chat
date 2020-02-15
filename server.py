#! /usr/bin/python3
import socket
import select
from time import sleep
from common import mensaje, sock
from hashlib import md5

contadorLoVeis = 0



class Server:
	def __init__(self,server: str ,port: int):
		self.s = sock(server,port)
		self.clients = []  # lista de clientes conectados
		self.nombre = "SERVER"
		self.aEnviar = []  # Lista de Mensajes a enviar

	def abrirserver(self):
		print(f"debug: server {self.s.server}, port {self.s.port}")
		self.s.bind((self.s.server, self.s.port))
		self.s.listen(30)
		socket.gethostbyaddr("localhost")

	def aceptarcliente(self):
			socket, address = self.s.accept()
			nombre, tipo, texto = self.s.recibir(socket)

			if tipo !="l":
				print("error recibiendo mensaje de login")
				socket.close()

			elif nombre in self.getListaNombres():
				mensaje.deTexto(self.nombre,"Ya estás conectado a este servidor").enviar(socket)
				socket.close()
			else:
				self.clients.append((socket, address, nombre))
				#envia lista de los nombres de los clientes conectados a todos los clientes
				listaconectados = "".join(i+"\t" for i in self.getListaNombres())
				print(f"usuarios conectados:{listaconectados}")
				self.broadcast(mensaje(self.nombre, listaconectados,tipo="c"))
				#envia lista de
				# los nombres de los clientes conectados a todos los clientes
				mensaje.deTexto(self.nombre, "Te Has Conectado").enviar(socket)
				print(f"Cliente {address} aceptado,{self.clients[0]}")


	def seleccionar(self):  # select wrapper
		# lista con solo los sockets de los clientes para usar con select
		socketlist = self.getListaSockets()
		socketlist.append(self) # si el propio socket es readable es que se puede aceptar un cliente
		if socketlist == []:  # A windows no le gusta select.select() con 3 listas vacías
			return [], [], []
		return select.select(socketlist, socketlist, [])

	def enviador(self, socket):  # maneja el intercambio de mensajes en el server
		for texto in self.aEnviar:
			print(f"se puede enviar:{self.aEnviar}")
			for texto in enumerate(self.aEnviar):
				m = mensaje.deTexto(self.nombre, texto)
				self.broadcast(m)
				self.aEnviar.remove(texto)

	def bots(self,msg):
		print("msg en bots:",msg,type(msg))
		nombre, tipo, texto = msg
		
		##LoEntendeisBot
		if texto == "/LoVeis":
			global contadorLoVeis
			contadorLoVeis+=1
			texto = f"Lo veis dicho {contadorLoVeis} veces."
			self.broadcast(mensaje.deTexto(self.nombre,texto))
		##LoEntendeisBot

			




	def messagehandler(self, msg):
		nombre, tipo, texto = msg
		if tipo == "t":  # texto
			#print(f"<{nombre}>:{texto}")
			mensajeParaEnviar = mensaje.deRecibido(msg)
			if texto !="":
				if texto[0] == "/":
					msg = self.bots(msg)
			self.broadcast(mensajeParaEnviar)  # echo del mensaje a los clientes
		if tipo == "l":  # error, los mensajes tipo login se interpretan en self.aceptar()
			print("Error")
		if tipo == "g": # mensaje de creación de un grupo
			pass
	# envia un mensaje a un grupo de clientes, por defecto a todos (grupos aun no implementados)
	def broadcast(self, mensaje, grupo=[]):
		grupo = self.clients if grupo == [] else grupo
		socketlist = [grupo[i][0] for i in range(len(grupo))]
		for i in socketlist:
			mensaje.enviar(i)

	def getListaNombres(self): # devuelve los nombres de los clientes conectados
		return [i[2] for i in self.clients]
	
	def getListaSockets(self):

		return [i[0] for i in self.clients]

	def EnviarClientes(self):

		texto = "".join(i for i in self.getListaNombres())
		enviar = mensaje(self.nombre, texto, objetivo="a", tipo="i")
		self.broadcast(enviar)

	def rutina(self):
		try:
			while True:
				try:
				
					sleep(1/100) # sin este sleep el bucle gasta demasiada cpu
					
					
					readable, writable, exceptional = self.seleccionar()
					#print("debug:",readable,writable,exceptional)
					for socket in readable:
						if socket.fileno() ==self.s.fileno():# comprueba si un socket reada
							self.aceptarcliente()
							continue
						
						self.messagehandler(self.s.recibir(socket))
					for socket in writable:
						self.enviador(socket)
					readable, writable, exceptional = [], [], []
				except ConnectionError:  # se ha desconectado un socket
					for i in self.clients:
						if i[0].fileno() == -1:  # el socket que se ha desconectado tiene un fd inválido
							print(i[1], i[2], "se ha desconectado")
							self.clients.remove(i)
		except KeyboardInterrupt:
			self.broadcast(mensaje.deTexto(self.nombre,"Servidor Cerrandose"))
			self.s.close()

if __name__ == "__main__":
	serv = Server(12500)
	serv.abrirserver()
	mensaje.enckey=md5("ChaoMorais".encode("utf-8")).digest()
	serv.rutina()