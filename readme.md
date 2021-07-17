Chat pensado para redes locales, creado usando python y Qt,
### Funcionamiento
Se comunica usando sockets, con el modelo cliente/servidor y un protocolo de comunicación propio usando json
### Características
- Soporte UTF-8
- Envío de mensajes privados (seleccionando los objetivos en la lista de usuarios)
- Encripción usando RC4 (**No es un algoritmo seguro a día de hoy**), fue implementado por razones de aprendizaje
- Se puede añadir html directamente en los mensajes gracias al soporte nativo de Qt
