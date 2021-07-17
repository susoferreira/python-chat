Chat pensado para redes locales, creado usando python y Qt, Es un proyecto creado con fines de aprendizaje y puede no ser completamente estable
### Funcionamiento
Se comunica usando sockets, con el modelo cliente/servidor y un protocolo de comunicación propio usando json
### Características
- Soporte UTF-8
- Envío de mensajes privados (seleccionando los objetivos en la lista de usuarios)
- Encripción usando RC4 (**No es un algoritmo seguro a día de hoy**)
- Se puede añadir html directamente en los mensajes gracias al soporte nativo de Qt
### Características planeadas
- Cambio del algoritmo de encripción por AES-256
- Añadir una opción de envíar un fichero a través del chat