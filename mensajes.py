import json
from RC4 import RC4
class mensaje:

    encoding="utf-8"
    enckey = "clave".encode("utf-8") # se comparte entre todas las instancias de mensaje

    def __init__(self, nombre, contenido, objetivo="a", tipo="t"):
        self.nombre = nombre
        self.contenido = contenido
        self.tipo = tipo
        # tipos:
        # l (login, se envía uno al conectarse al server, el nombre de ese mensaje es el que sirve para identificar al socket)
        # t (texto, mensajes normales)
        # i (info, del server al cliente)
        # c (lista de clientes conectados)
        # b (desconexión) no implementado
        
        # por ahora solo existe a , para mandar mensajes privados se usaría la variable sock.nombre o el grupo
        self.objetivo = objetivo

    def enviar(self, socketAEnviar):  # envia el mensaje convertido a bytes con un null byte de terminación
        try:
            aux=self.encrypt()
            print(type(aux))

            lenheader="{:>10}".format(len(aux)).encode(self.encoding) # el header es necesario para indicar cuando termina un mensaje
            print("enviando:",lenheader+aux)
            print("decriptado:",self.toJson())
            socketAEnviar.sendall(lenheader+aux)

        except ConnectionError:
            print("conexión reseteada con el cliente",socketAEnviar)
            socketAEnviar.close()

    def toJson(self):
        return json.dumps(self.__dict__)

    def encrypt(self) -> bytes: 
        return RC4(self.toJson().encode(self.encoding),self.enckey)
    @classmethod
    def decrypt(cls,mensaje: bytes,enckey = None) ->str:
        if enckey == None:
            enckey = cls.enckey
        return RC4(mensaje,enckey)

    @classmethod
    # constructor para crear un mensaje con los datos de un mensaje recibido
    def deRecibido(cls, mensaje : str):
        atrs = json.loads(mensaje)
        return cls(atrs["nombre"], atrs["contenido"],tipo=atrs["tipo"])

    @classmethod
    def deTexto(cls, nombre, texto):  # constructor alternativo
        if nombre == "":
            print("No tienes nombre, cambialo con self.nombre")
        return cls(nombre, texto)


if __name__ == "__main__":
    msg = mensaje.deTexto("test","contenido")
    encodedmsg = msg.toJson()
    enviado = msg.encrypt()
    decriptado = mensaje.decrypt(enviado)
    print("mensaje:",msg)
    print("json:", encodedmsg)
    print("encriptado:",enviado)
    print("decriptado:", decriptado)
