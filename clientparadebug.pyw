#! /usr/bin/python3
print("antes de imports")
from select import select
import socket
from sys import argv,exit
from time import sleep
from PyQt5 import QtWidgets,QtGui,QtCore
from clientUI import Ui_Chattogu
from common import mensaje, sock
print("despues de imports")

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
			sleep(1/60) # sin este sleep el bucle gasta demasiada cpu
			try: 

				readable, writable, exceptional = select([self], [self], [], 0)
				if readable:
					self.messagehandler()
				if writable:
					if len(self.listaDeMensajes) != 0:
						self.sg.writablesignal.emit() # señal de pyqt que esta conectada con MainWindow.enviar()
						#print("hay mensajes para enviar")
					
			except KeyboardInterrupt:
			 	self.close()
			except ConnectionError:
				#print("Servidor Cerrado")
				self.close()
				window.conectado = False
				window.CuadroDeTexto.append("Servidor Cerrado")
				break
		while True: #cerrar el hilo causa un segfault porque diosito lo quiere, así que mejor dejarlo en un bucle infinito
			pass

	def messagehandler(self):
		nombre,tipo,texto = self.recibir()
		if tipo == "t": #añadir a lista de mensajes
			#print(f"<{nombre}>:{texto}")
			window.CuadroDeTexto.append(f"<{nombre}>:{texto}")	
		if tipo == "c": # enviar lista de personas conectadas
			window.UsuariosConectados.clear()
			#print(f"Recibida lista de clientes de {nombre},{texto}")
			#print(texto)
			listanombres = texto.split("\t")
			listanombres.pop() # eliminamos el ultimo elemento porque es un string vacío
			#print(listanombres)
			for i in listanombres:
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
		#print(f"enviando {texto}")
		self.MensajeAEnviar.clear()
		self.clientsocket.listaDeMensajes.append(texto)

	def enviar(self):
		for texto in self.clientsocket.listaDeMensajes:
			mensaje.deTexto(self.clientsocket.nombre,texto).enviar(self.clientsocket)
		self.clientsocket.listaDeMensajes.clear()


	def conectar(self):
		try:
			if not self.conectado:
				
				self.clientsocket = clientsock( self.IP.text(), int(self.Port.text()) ) # crea el socket
				self.clientsocket.setup(self.Nombre.text())# conecta el socket 
				self.clientsocket.sg.writablesignal.connect(self.enviar)
				mensaje(self.clientsocket.nombre,"login",tipo="l").enviar(self.clientsocket) #login
				self.hiloRutina = self.hilo(self.clientsocket.rutina)# crea una instancia del hilo que ejecuta la rutina
				self.hiloRutina.start()
				
				self.conectado = True
			else:
				self.CuadroDeTexto.append("Ya estás conectado al servidor")
		except ValueError:
			print("tipos de variables incorrectos")
		except ConnectionRefusedError:
			self.CuadroDeTexto.append("No Existe El servidor")
			#print("No existe el servidor")
		except KeyboardInterrupt:
			#print("Cerrado correctamente")
			self.clientsocket.close()
			self.conectado = False

	def autoScrollTexto(self):
			if self.MensajeAEnviar.text() == "": # si el cuadro para enviar mensajes esta vacio  autoscroll
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
