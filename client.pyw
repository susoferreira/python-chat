#! /usr/bin/python3
import log
log.LOG_FILE="./logs/clientlog"
from log import log
from select import select
import socket
from sys import argv,exit
from time import sleep
from PyQt5 import QtWidgets,QtGui,QtCore
from clientUI import Ui_Chattogu
from common import  sock
from hashlib import md5
from mensajes import mensaje


class clientsock(sock):
	class signals(QtCore.QObject):
		writablesignal = QtCore.pyqtSignal()
		def __init__(self):
			QtCore.QObject.__init__(self)
			
	def __init__(self, server, port):
		self.sg = self.signals()
		
		sock.__init__(self, server, port)
		# self.setblocking(0)
		self.listaDeMensajes = []

	def setup(self, nombre):
		self.connect((self.server, self.port))
		self.nombre = nombre

	def recibir(self):  # en el cliente el objetivo es el mismo cliente
		return sock.recibir(self, self)

	def rutina(self):
		
		while True:
			sleep(1/100) # sin este sleep el bucle gasta demasiada cpu
			try: 

				readable, writable, exceptional = select([self], [self], [], 0)
				if readable:
					log("readable")
					self.messagehandler()
				if writable:
					if len(self.listaDeMensajes) != 0:
						self.sg.writablesignal.emit() # señal de pyqt que esta conectada con MainWindow.enviar()
						#log("hay mensajes para enviar")
					
			except KeyboardInterrupt:
			 	self.close()
			except ConnectionError:
				log("Servidor Cerrado")
				self.close()
				window.conectado = False
				window.CuadroDeTexto.append("El servidor ha rechazado la conexión, es posible que se haya cerrado o que haya habido un error en el login (contraseña incorrecta) ")
				break
		while True: #cerrar el hilo causa un segfault porque diosito lo quiere, así que mejor dejarlo en un bucle infinito
			sleep(10000)

	def messagehandler(self):

		msg = self.recibir()
		if msg.tipo == "t": #añadir a lista de mensajes
			#log(f"<{nombre}>:{texto}")
			if msg.objetivo == "a":
				window.CuadroDeTexto.append(f"<b>&lt;{msg.nombre}&gt; -> TODOS:</b>{msg.contenido}")	
			else:
				obj=msg.objetivo.replace(msg.nombre,"")
				window.CuadroDeTexto.append(f"<b>&lt;{msg.nombre}&gt; -> {obj}:</b>{msg.contenido}")	

		if msg.tipo == "c": # enviar lista de personas conectadas
			window.UsuariosConectados.clear()

			listanombres = msg.contenido.split("\t")
			log(listanombres)

			for i in listanombres:
				log("añadiendo ",i,"a la lista de conectados")
				window.UsuariosConectados.addItem(i)

class MainWindow(Ui_Chattogu,QtWidgets.QMainWindow):
	
	def __init__(self, *args, **kwargs):
		QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
		self.setupUi(self)
		self.Conectar.clicked.connect(self.conectar)
		self.Enviar.clicked.connect(self.anadirAEnviar)
		self.CuadroDeTexto.textChanged.connect(self.autoScrollTexto)
		#self.CrearGrupo.clicked.connect(self.enviarCreacionGrupo) algun dia lo implementaré
		self.conectado = False
		
	def anadirAEnviar(self):
		texto = self.MensajeAEnviar.text()
		if self.UsuariosConectados.selectedItems():
			objetivo = "".join((i.text() for i in self.UsuariosConectados.selectedItems()))+" "+self.clientsocket.nombre
			print("objetivo:",objetivo)
			msg = mensaje(self.clientsocket.nombre,texto,objetivo=objetivo)
		else:
			msg = mensaje.deTexto(self.clientsocket.nombre,texto)

		self.clientsocket.listaDeMensajes.append(msg)
		self.MensajeAEnviar.clear()

	def enviar(self):
		for mensaje in self.clientsocket.listaDeMensajes:
			mensaje.enviar(self.clientsocket)
		self.clientsocket.listaDeMensajes.clear()


	def conectar(self):
		try:
			if not self.conectado:

				self.clientsocket = clientsock( self.IP.text(), int(self.Port.text()) ) # crea el socket
				#temporal
				mensaje.enckey = md5(self.Password.text().encode("utf-8")).digest() ## temporal
				#temporal
				self.clientsocket.setup(self.Nombre.text())# conecta el socket 
				self.clientsocket.sg.writablesignal.connect(self.enviar)
				log("conectando")
				mensaje(self.clientsocket.nombre,"login",tipo="l").enviar(self.clientsocket) #login
				self.hiloRutina = self.hilo(self.clientsocket.rutina)# crea una instancia del hilo que ejecuta la rutina
				self.hiloRutina.start()
				
				self.conectado = True
			else:
				self.CuadroDeTexto.append("Ya estás conectado al servidor")
		except ValueError:
			log("tipos de variables incorrectos")
		except ConnectionRefusedError:
			self.CuadroDeTexto.append("No Existe El servidor")

		except KeyboardInterrupt:

			self.clientsocket.close()
			self.conectado = False

	def autoScrollTexto(self):
			if self.MensajeAEnviar.text()  == "": # si el cuadro para enviar mensajes esta vacio autoscroll
				self.CuadroDeTexto.moveCursor(QtGui.QTextCursor.End)

	class hilo(QtCore.QThread): # crea un hilo con la función que se pase de argumento
		def __init__(self,func): 
			QtCore.QThread.__init__(self)
			self.func=func
		def run(self):
			self.func()
if __name__ == "__main__":
	try:
		app = QtWidgets.QApplication([])
		window = MainWindow()
		window.show()
		app.exec_()
		exit()
	except SystemExit:
		window.clientsocket.close()
		exit()
